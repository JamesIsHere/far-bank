from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from validate_p1_records import PROJECT_ROOT, load_json, validate_exact_binding


def canonical_event_bytes(event: dict[str, Any]) -> bytes:
    return (json.dumps(event, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def locate_question_version(event: dict[str, Any], project_root: Path) -> Path:
    subject = event["subject"]
    return (
        project_root
        / "data"
        / "questions"
        / subject["question_id"]
        / "versions"
        / f"{subject['version_id']}.json"
    )


def ingest_review_event(
    event: dict[str, Any],
    question: dict[str, Any],
    target_dir: Path,
    schema: dict[str, Any],
    *,
    allow_fixture: bool = False,
) -> Path:
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(event),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        raise ValueError(f"review event schema rejection: {errors[0].message}")
    binding = validate_exact_binding(event, question)
    if binding:
        raise ValueError(binding[0].detail)
    purpose = question["content"]["authorship"]["purpose"]
    if purpose == "schema_fixture" and not allow_fixture:
        raise ValueError("schema fixtures cannot create canonical review events")
    if event["action"] == "auto_invalidate":
        if event["actor"]["actor_type"] != "system":
            raise ValueError("auto-invalidation requires a system actor")
    elif event["actor"]["actor_id"] != "james":
        raise ValueError("P1/G2 canonical human review events require reviewer actor_id james")

    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / f"{event['event_id']}.json"
    with target.open("xb") as handle:
        handle.write(canonical_event_bytes(event))
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and exclusively ingest one downloaded append-only review event.")
    parser.add_argument("event_file", type=Path)
    args = parser.parse_args()
    event = load_json(args.event_file)
    question_path = locate_question_version(event, PROJECT_ROOT)
    if not question_path.is_file():
        raise SystemExit(f"No canonical exact question version at {question_path}")
    question = load_json(question_path)
    superseding_version_id = event.get("superseding_version_id")
    if superseding_version_id:
        superseding_path = (
            PROJECT_ROOT
            / "data"
            / "questions"
            / event["subject"]["question_id"]
            / "versions"
            / f"{superseding_version_id}.json"
        )
        if not superseding_path.is_file():
            raise SystemExit(f"No canonical superseding question version at {superseding_path}")
    schema = load_json(PROJECT_ROOT / "schema" / "review-event.schema.json")
    target = ingest_review_event(
        event,
        question,
        PROJECT_ROOT / "data" / "events" / "review",
        schema,
    )
    print(f"PASS ingested append-only review event {target.relative_to(PROJECT_ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
