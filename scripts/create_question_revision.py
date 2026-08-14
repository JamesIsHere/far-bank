from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from validate_p1_records import (
    PROJECT_ROOT,
    canonical_content_sha256,
    load_json,
    validate_question_contract,
)


def canonical_record_bytes(record: dict[str, Any]) -> bytes:
    return (json.dumps(record, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def create_question_revision(
    prior_question: dict[str, Any],
    revised_content: dict[str, Any],
    target_versions_dir: Path,
    *,
    project_root: Path = PROJECT_ROOT,
) -> tuple[dict[str, Any], Path]:
    if revised_content == prior_question["content"]:
        raise ValueError("a revision must change approval-bound content")
    next_number = prior_question["version_number"] + 1
    version_id = f"{prior_question['question_id']}.v{next_number:03d}"
    revision = {
        "schema_version": prior_question["schema_version"],
        "question_id": prior_question["question_id"],
        "version_id": version_id,
        "version_number": next_number,
        "content_sha256": canonical_content_sha256(revised_content),
        "content": revised_content,
    }
    if revision["content_sha256"] == prior_question["content_sha256"]:
        raise ValueError("revised content did not produce a new exact-version hash")
    taxonomy = load_json(project_root / "data/far-taxonomy.json")
    rules = {
        record["rule_version_id"]: record
        for path in project_root.glob("data/rules/*/versions/*.json")
        for record in [load_json(path)]
    }
    schema = load_json(project_root / "schema/question-version.schema.json")
    issues = validate_question_contract(revision, schema, taxonomy, rules)
    if issues:
        raise ValueError("revision contract rejection: " + "; ".join(f"{issue.contract_id}: {issue.detail}" for issue in issues[:6]))
    target_versions_dir.mkdir(parents=True, exist_ok=True)
    target = target_versions_dir / f"{version_id}.json"
    with target.open("xb") as handle:
        handle.write(canonical_record_bytes(revision))
    return revision, target


def build_auto_invalidation_event(
    prior_question: dict[str, Any],
    superseding_question: dict[str, Any],
    *,
    event_id: str,
    recorded_at: str,
) -> dict[str, Any]:
    if prior_question["question_id"] != superseding_question["question_id"]:
        raise ValueError("superseding version belongs to a different question identity")
    if superseding_question["version_number"] <= prior_question["version_number"]:
        raise ValueError("superseding version must be newer")
    return {
        "schema_version": "1.0.0",
        "event_id": event_id,
        "recorded_at": recorded_at,
        "action": "auto_invalidate",
        "actor": {
            "actor_type": "system",
            "actor_id": "far-bank-review-integrity",
            "display_name": "FAR Bank Review Integrity",
        },
        "subject": {
            "question_id": prior_question["question_id"],
            "version_id": prior_question["version_id"],
            "content_sha256": prior_question["content_sha256"],
        },
        "comment": f"{prior_question['version_id']} is superseded by {superseding_question['version_id']}; approval does not carry forward.",
        "reason_code": "content_superseded",
        "superseding_version_id": superseding_question["version_id"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Create one validated immutable question revision by exclusive file creation.")
    parser.add_argument("prior_question", type=Path)
    parser.add_argument("revised_content", type=Path, help="JSON file containing the complete revised content object")
    parser.add_argument("--target-dir", type=Path)
    args = parser.parse_args()
    prior = load_json(args.prior_question)
    content = load_json(args.revised_content)
    target_dir = args.target_dir or args.prior_question.parent
    revision, target = create_question_revision(prior, content, target_dir)
    print(f"PASS created immutable revision {target.relative_to(PROJECT_ROOT).as_posix()} hash={revision['content_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
