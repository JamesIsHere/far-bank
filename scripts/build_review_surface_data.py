from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from validate_p1_records import PROJECT_ROOT, load_json
from verify_p1_sample import MANIFEST_PATH, REPORT_PATH, load_bundles, load_review_history
from verify_questions import derive_learner_ready, run_checks


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def taxonomy_labels(taxonomy: dict[str, Any], task_id: str) -> dict[str, str | None]:
    for area in taxonomy["areas"]:
        for group in area["groups"]:
            for task in group["tasks"]:
                if task["id"] == task_id:
                    return {
                        "area": area["official_title"],
                        "group": group["official_title"],
                        "topic": None,
                        "task": task["official_text"],
                    }
            for topic in group["topics"]:
                for task in topic["tasks"]:
                    if task["id"] == task_id:
                        return {
                            "area": area["official_title"],
                            "group": group["official_title"],
                            "topic": topic["official_title"],
                            "task": task["official_text"],
                        }
    raise ValueError(f"unresolved taxonomy task {task_id}")


def build_review_data(
    project_root: Path = PROJECT_ROOT,
    *,
    manifest_path: Path = MANIFEST_PATH,
    sample_report_path: Path = REPORT_PATH,
    include_reviews: bool = True,
) -> dict[str, Any]:
    taxonomy_path = project_root / "data" / "far-taxonomy.json"
    taxonomy = load_json(taxonomy_path)
    manifest = load_json(manifest_path)
    bundles = load_bundles(manifest_path, include_reviews=include_reviews)
    items: list[dict[str, Any]] = []
    source_paths = {
        manifest_path,
        project_root / "reports" / "p1-verifier-calibration.json",
        sample_report_path,
        taxonomy_path,
    }
    for entry, bundle in zip(manifest["items"], bundles):
        source_paths.update(project_root / entry[key] for key in (
            "identity_path", "question_path", "rule_path", "reference_path", "verification_path"
        ))
        results = run_checks(bundle, project_root)
        readiness = derive_learner_ready(bundle, results)
        review_history = load_review_history(bundle.question, project_root) if include_reviews else []
        for event in review_history:
            source_paths.add(project_root / "data" / "events" / "review" / f"{event['event_id']}.json")
        question = bundle.question
        content = question["content"]
        mapping = content["blueprint_mappings"][0]
        items.append({
            "identity": {
                "question_id": question["question_id"],
                "version_id": question["version_id"],
                "version_number": question["version_number"],
                "content_sha256": question["content_sha256"],
            },
            "derived_readiness": {
                "learner_ready": readiness.learner_ready,
                "reasons": list(readiness.reasons),
                "coverage_contribution": 0,
            },
            "question": {
                "stem": content["stem"],
                "options": content["options"],
                "facts": content["facts"],
                "assumptions": content["assumptions"],
                "solution": content["solution"],
                "correctness_evidence": content["correctness_evidence"],
                "accounting_model_id": content["accounting_model_id"],
            },
            "blueprint": {**mapping, "labels": taxonomy_labels(taxonomy, mapping["representative_task_id"])},
            "rule": bundle.rule,
            "reference": bundle.reference,
            "challenge_mechanics": content["challenge_mechanics"],
            "difficulty_profile": content["difficulty_profile"],
            "originality_boundary": content["originality_boundary"],
            "verification": {
                "checker_id": "far-p1-question-verifier",
                "checker_version": "1.0.0",
                "checks": [result.as_dict() for result in results],
            },
            "review_history": review_history,
        })
    return {
        "surface_version": "p1.6-g2-sample-review.v002" if include_reviews else "p1.5-g2-sample-review.v001",
        "surface_scope": {
            "record_purpose": "sample_candidate",
            "claim": "Internal G2 exact-version review only. A current item becomes mechanically learner-ready only after James approves that exact version; no item is coverage-bearing until G2 ratification.",
            "canonical_event_note": "Downloaded action events are proposals until validated and exclusively ingested into the canonical append-only event directory.",
        },
        "source_manifest": [
            {"path": path.relative_to(project_root).as_posix(), "sha256": file_sha256(path)}
            for path in sorted(source_paths)
        ],
        "queue_summary": {
            "sample_id": manifest["sample_id"],
            "item_count": len(items),
            "ready_count": sum(item["derived_readiness"]["learner_ready"] for item in items),
            "coverage_contribution": 0,
        },
        "items": items,
        "review_actions": {
            "allowed": ["approve", "reject", "revise", "comment"],
            "reviewer": {"actor_type": "human", "actor_id": "james", "display_name": "James"},
            "event_schema": "schema/review-event.schema.json",
            "ingest_command": "python scripts/ingest_review_event.py <downloaded-event.json>",
        },
    }


def deterministic_json_bytes(data: dict[str, Any]) -> bytes:
    return (json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the exact-version local G2 sample review queue.")
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "review-surface" / "app" / "review-data-v002.json",
    )
    args = parser.parse_args()
    data = build_review_data()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(deterministic_json_bytes(data))
    print(
        f"PASS review queue {data['queue_summary']['sample_id']} "
        f"items={data['queue_summary']['item_count']} "
        f"ready={data['queue_summary']['ready_count']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
