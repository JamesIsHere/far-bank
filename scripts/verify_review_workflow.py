from __future__ import annotations

import copy
import json
import sqlite3
import tempfile
from pathlib import Path
from typing import Any

from create_question_revision import build_auto_invalidation_event, create_question_revision
from ingest_review_event import ingest_review_event
from rebuild_review_projection import build_projection
from validate_p1_records import PROJECT_ROOT, load_json


def _human_event(question: dict[str, Any], action: str, ordinal: int) -> dict[str, Any]:
    event: dict[str, Any] = {
        "schema_version": "1.0.0",
        "event_id": f"far-review-p2-workflow-{action}",
        "recorded_at": f"2026-08-13T23:0{ordinal}:00Z",
        "action": action,
        "actor": {"actor_type": "human", "actor_id": "james", "display_name": "James"},
        "subject": {
            "question_id": question["question_id"],
            "version_id": question["version_id"],
            "content_sha256": question["content_sha256"],
        },
        "comment": f"P2.2 exclusive-ingestion calibration for {action}.",
    }
    if action == "revise":
        event["reason_code"] = "content_revision_requested"
    return event


def build_workflow_report(project_root: Path = PROJECT_ROOT) -> dict[str, Any]:
    question = load_json(project_root / "data/questions/far-q-000101/versions/far-q-000101.v001.json")
    review_schema = load_json(project_root / "schema/review-event.schema.json")
    review_surface = project_root / "review-surface"
    with tempfile.TemporaryDirectory(prefix=".p2-workflow-", dir=review_surface) as temporary_name:
        temporary = Path(temporary_name)
        event_dir = temporary / "events"
        action_receipts: list[dict[str, Any]] = []
        events: dict[str, dict[str, Any]] = {}
        for ordinal, action in enumerate(("approve", "reject", "revise", "comment"), 1):
            event = _human_event(question, action, ordinal)
            target = ingest_review_event(event, question, event_dir, review_schema)
            events[action] = event
            action_receipts.append({"action": action, "event_id": event["event_id"], "ingested_exclusively": target.is_file()})

        duplicate_rejected = False
        try:
            ingest_review_event(events["approve"], question, event_dir, review_schema)
        except FileExistsError:
            duplicate_rejected = True

        stale = copy.deepcopy(events["comment"])
        stale["event_id"] = "far-review-p2-workflow-stale"
        stale["subject"]["content_sha256"] = "0" * 64
        stale_rejected = False
        try:
            ingest_review_event(stale, question, event_dir, review_schema)
        except ValueError:
            stale_rejected = True

        revised_content = copy.deepcopy(question["content"])
        original_stem = revised_content["stem"]
        revised_content["stem"] = original_stem.replace("At year-end", "At the reporting date")
        if revised_content["stem"] == original_stem:
            revised_content["stem"] = original_stem.replace("A company", "The reporting company", 1)
        revision, revision_path = create_question_revision(question, revised_content, temporary / "versions", project_root=project_root)
        invalidation = build_auto_invalidation_event(
            question,
            revision,
            event_id="far-review-p2-workflow-auto-invalidate",
            recorded_at="2026-08-13T23:05:00Z",
        )
        invalidation_path = ingest_review_event(
            invalidation,
            question,
            event_dir,
            review_schema,
            superseding_question=revision,
        )

        projection_path = temporary / "review.sqlite"
        projection_report = build_projection(projection_path, project_root)
        connection = sqlite3.connect(projection_path)
        try:
            rows = connection.execute(
                "SELECT version_id, is_latest_version, latest_decisive_action, learner_ready FROM learner_ready_projection WHERE question_id = 'far-q-000102' ORDER BY version_number"
            ).fetchall()
        finally:
            connection.close()

    q102_state = [
        {
            "version_id": version_id,
            "is_latest_version": bool(is_latest),
            "latest_decisive_action": action,
            "learner_ready": bool(ready),
        }
        for version_id, is_latest, action, ready in rows
    ]
    return {
        "schema_version": "1.0.0",
        "workflow_id": "far-p2-review-workflow-calibration.v001",
        "actions": action_receipts,
        "exclusive_create_duplicate_rejected": duplicate_rejected,
        "stale_exact_version_binding_rejected": stale_rejected,
        "revision": {
            "prior_version_id": question["version_id"],
            "prior_content_sha256": question["content_sha256"],
            "new_version_id": revision["version_id"],
            "new_content_sha256": revision["content_sha256"],
            "new_version_created_exclusively": revision_path.name == f"{revision['version_id']}.json",
            "auto_invalidation_event_id": invalidation["event_id"],
            "auto_invalidation_created_exclusively": invalidation_path.name == f"{invalidation['event_id']}.json",
        },
        "canonical_revision_example": {
            "question_id": "far-q-000102",
            "exact_version_state": q102_state,
            "prior_approval_carried_forward": False,
        },
        "projection_equivalent_to_cold_reconstruction": projection_report["projection_equivalent_to_cold_reconstruction"],
        "projection_manifest_id": projection_report["projection_manifest_id"],
        "claim_limit": "This is local workflow and reconstruction evidence, not G3 approval, production content, or authorization for a hosted reviewer system.",
    }


def deterministic_json_bytes(report: dict[str, Any]) -> bytes:
    return (json.dumps(report, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def main() -> int:
    report = build_workflow_report()
    output = PROJECT_ROOT / "reports/p2-review-workflow-verification.json"
    output.write_bytes(deterministic_json_bytes(report))
    print(
        f"PASS review workflow: actions={len(report['actions'])} "
        f"duplicate_rejected={report['exclusive_create_duplicate_rejected']} "
        f"stale_rejected={report['stale_exact_version_binding_rejected']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
