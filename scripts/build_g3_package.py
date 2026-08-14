from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from validate_p1_records import PROJECT_ROOT, load_json


OUTPUT_PATH = PROJECT_ROOT / "reports" / "g3-package-manifest.json"
SURFACE_OUTPUT_PATH = PROJECT_ROOT / "review-surface" / "app" / "g3-workflow-package.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_package(project_root: Path = PROJECT_ROOT) -> dict[str, Any]:
    workflow_path = project_root / "reports" / "p2-review-workflow-verification.json"
    projection_path = project_root / "reports" / "p2-projection-reconstruction.json"
    review_data_path = project_root / "review-surface" / "app" / "review-data-v002.json"
    workflow = load_json(workflow_path)
    projection = load_json(projection_path)
    review_data = load_json(review_data_path)

    q102_states = [
        state
        for state in projection["exact_version_state"]
        if state["question_id"] == workflow["canonical_revision_example"]["question_id"]
    ]
    evidence_paths = [
        workflow_path,
        projection_path,
        review_data_path,
        project_root / "data" / "contracts" / "far-g2-production-contract.v001.json",
        project_root / "schema" / "review-event.schema.json",
        project_root / "schema" / "review-projection.sql",
        project_root / "review-surface" / "app" / "page.tsx",
        project_root / "review-surface" / "app" / "evidence" / "page.tsx",
        project_root / "review-surface" / "app" / "review-actions.tsx",
        project_root / "review-surface" / "app" / "globals.css",
    ]

    return {
        "schema_version": "1.0.0",
        "package_id": "far-g3-review-workflow.v001",
        "package_status": "ready_for_human_gate_not_approved",
        "gate": "G3",
        "verdict": {
            "owner": "James",
            "decision_state": "not_issued",
            "automation_authority": False,
            "required_outcome": "James exercises the bounded local workflow and explicitly approves or rejects Gate G3.",
        },
        "hands_on_steps": [
            "Choose each of Approve, Reject, Revise, and Comment and confirm the event preview binds the displayed question ID, version ID, and content hash.",
            "Enter a reasoned comment and download a proposal; confirm downloading does not alter readiness or canonical history.",
            "Inspect the revision boundary: the prior approved version is auto-invalidated and its approval does not carry to the new version.",
            "Confirm the current sample remains non-production and contributes zero production coverage.",
            "Issue an explicit G3 verdict outside the composer; generated events and automated checks cannot approve this gate.",
        ],
        "workflow": {
            "actions": workflow["actions"],
            "exclusive_create_duplicate_rejected": workflow["exclusive_create_duplicate_rejected"],
            "stale_exact_version_binding_rejected": workflow["stale_exact_version_binding_rejected"],
            "revision_calibration": workflow["revision"],
        },
        "revision_boundary": {
            "question_id": workflow["canonical_revision_example"]["question_id"],
            "exact_version_state": q102_states,
            "prior_approval_carried_forward": workflow["canonical_revision_example"]["prior_approval_carried_forward"],
        },
        "projection": {
            "manifest_id": projection["projection_manifest_id"],
            "canonical_input_count": projection["canonical_input_count"],
            "equivalent_to_cold_reconstruction": projection["projection_equivalent_to_cold_reconstruction"],
            "ddl_sha256": projection["ddl_sha256"],
            "state_summary": projection["state_summary"],
        },
        "sample": {
            "sample_id": review_data["queue_summary"]["sample_id"],
            "item_count": review_data["queue_summary"]["item_count"],
            "mechanically_ready_count": review_data["queue_summary"]["ready_count"],
            "production_coverage_contribution": review_data["queue_summary"]["coverage_contribution"],
            "exact_version_ids": [item["identity"]["version_id"] for item in review_data["items"]],
        },
        "evidence_artifacts": [
            {"path": path.relative_to(project_root).as_posix(), "sha256": sha256(path)}
            for path in evidence_paths
        ],
        "limitations": [
            "Local-only internal review package; no hosted persistence, accounts, or public deployment.",
            "The composer downloads proposals only; canonical ingestion remains a separate schema-validating exclusive-create boundary.",
            "The six historical G2 sample items are not production-bank questions and contribute zero production coverage.",
            "Automated accessibility, integrity, reconstruction, build, and lint checks support inspection but cannot issue the human G3 verdict.",
        ],
    }


def package_bytes(value: dict[str, Any]) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the bounded local FAR Gate G3 workflow package.")
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    parser.add_argument("--surface-output", type=Path, default=SURFACE_OUTPUT_PATH)
    args = parser.parse_args()
    package = build_package()
    payload = package_bytes(package)
    for output in (args.output, args.surface_output):
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(payload)
    print(
        f"PASS G3 package {package['package_id']} actions={len(package['workflow']['actions'])} "
        f"status={package['package_status']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
