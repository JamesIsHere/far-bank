from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from validate_p1_records import (
    PROJECT_ROOT,
    canonical_content_sha256,
    load_json,
    schema_issues,
    validate_exact_binding,
    validate_question_contract,
)


BUILDER_ID = "far-review-projection-builder"
BUILDER_VERSION = "1.0.0"
REQUIRED_CHECK_POLICIES = {
    "far-p1-sample-candidate-checks.v001": (
        "SCHEMA_CONTRACT",
        "RECOMPUTE_INDEPENDENT",
        "RULE_TRACE_CURRENT",
        "DISTRACTOR_MODELS",
        "LANGUAGE_FAIRNESS",
        "ORIGINALITY_BOUNDARY",
        "APPROVAL_INTEGRITY",
        "VARIETY_EVIDENCE",
    )
}


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _paths(project_root: Path) -> dict[str, list[Path]]:
    patterns = {
        "identities": "data/questions/*/identity.json",
        "questions": "data/questions/*/versions/*.json",
        "references": "data/references/*.json",
        "rules": "data/rules/*/versions/*.json",
        "verification_events": "data/events/verification/*.json",
        "review_events": "data/events/review/*.json",
        "source_impact_events": "data/events/source-impact/*.json",
    }
    return {name: sorted(project_root.glob(pattern)) for name, pattern in patterns.items()}


def _load_records(project_root: Path) -> tuple[dict[str, list[tuple[Path, dict[str, Any]]]], list[dict[str, Any]]]:
    paths = _paths(project_root)
    records = {name: [(path, load_json(path)) for path in found] for name, found in paths.items()}
    manifest_entries = [
        {
            "path": path.relative_to(project_root).as_posix(),
            "sha256": _sha256(path),
            "size_bytes": path.stat().st_size,
        }
        for found in paths.values()
        for path in found
    ]
    return records, sorted(manifest_entries, key=lambda item: item["path"])


def _unique_index(records: list[tuple[Path, dict[str, Any]]], key: str, label: str) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for path, record in records:
        identity = record[key]
        if identity in result:
            raise ValueError(f"duplicate {label} {identity}")
        result[identity] = record
        if path.stem != identity and path.name != "identity.json":
            raise ValueError(f"{label} {identity} is stored under mismatched filename {path.name}")
    return result


def validate_canonical_records(records: dict[str, list[tuple[Path, dict[str, Any]]]], project_root: Path = PROJECT_ROOT) -> dict[str, Any]:
    schema_dir = project_root / "schema"
    schemas = {
        "identities": load_json(schema_dir / "question-identity.schema.json"),
        "questions": load_json(schema_dir / "question-version.schema.json"),
        "references": load_json(schema_dir / "reference-version.schema.json"),
        "rules": load_json(schema_dir / "rule-version.schema.json"),
        "verification_events": load_json(schema_dir / "verification-event.schema.json"),
        "review_events": load_json(schema_dir / "review-event.schema.json"),
        "source_impact_events": load_json(schema_dir / "source-impact-event.schema.json"),
    }
    issues: list[str] = []
    for family, family_records in records.items():
        for path, record in family_records:
            issues.extend(
                f"{path.relative_to(project_root).as_posix()}: {issue.detail}"
                for issue in schema_issues(schemas[family], record, family.upper())
            )
    if issues:
        raise ValueError("canonical schema validation failed: " + "; ".join(issues[:10]))

    identities = _unique_index(records["identities"], "question_id", "question identity")
    questions = _unique_index(records["questions"], "version_id", "question version")
    references = _unique_index(records["references"], "reference_version_id", "reference version")
    rules = _unique_index(records["rules"], "rule_version_id", "rule version")
    verification_events = _unique_index(records["verification_events"], "event_id", "verification event")
    review_events = _unique_index(records["review_events"], "event_id", "review event")
    source_impacts = _unique_index(records["source_impact_events"], "event_id", "source-impact event")
    taxonomy = load_json(project_root / "data/far-taxonomy.json")

    for reference in references.values():
        expected = f"{reference['reference_id']}.v{reference['version_number']:03d}"
        if reference["reference_version_id"] != expected:
            issues.append(f"reference identity mismatch {reference['reference_version_id']}")
    for rule in rules.values():
        expected = f"{rule['rule_id']}.v{rule['version_number']:03d}"
        if rule["rule_version_id"] != expected:
            issues.append(f"rule identity mismatch {rule['rule_version_id']}")
        if rule["content_sha256"] != canonical_content_sha256(rule["content"]):
            issues.append(f"rule content hash mismatch {rule['rule_version_id']}")
        for citation in rule["content"]["source_citations"]:
            if citation["reference_version_id"] not in references:
                issues.append(f"unresolved reference {citation['reference_version_id']} from {rule['rule_version_id']}")

    versions_by_question: dict[str, list[int]] = defaultdict(list)
    for question in questions.values():
        identity = identities.get(question["question_id"])
        if identity is None:
            issues.append(f"question version lacks identity {question['version_id']}")
            continue
        versions_by_question[question["question_id"]].append(question["version_number"])
        for issue in validate_question_contract(question, schemas["questions"], taxonomy, rules):
            issues.append(f"{question['version_id']}: {issue.contract_id}: {issue.detail}")
    for question_id, numbers in versions_by_question.items():
        if sorted(numbers) != list(range(1, max(numbers) + 1)):
            issues.append(f"question versions are not contiguous for {question_id}: {sorted(numbers)}")

    for event in verification_events.values():
        question = questions.get(event["subject"]["version_id"])
        if question is None:
            issues.append(f"verification event has unresolved subject {event['event_id']}")
        else:
            issues.extend(issue.detail for issue in validate_exact_binding(event, question))
        check_ids = [check["check_id"] for check in event["checks"]]
        if len(check_ids) != len(set(check_ids)):
            issues.append(f"verification event repeats a check ID {event['event_id']}")
    decisive_boundaries: dict[tuple[str, str], list[str]] = defaultdict(list)
    for event in review_events.values():
        question = questions.get(event["subject"]["version_id"])
        if question is None:
            issues.append(f"review event has unresolved subject {event['event_id']}")
        else:
            issues.extend(issue.detail for issue in validate_exact_binding(event, question))
        if event["action"] != "comment":
            decisive_boundaries[(event["subject"]["version_id"], event["recorded_at"])].append(event["event_id"])
        superseding = event.get("superseding_version_id")
        if superseding:
            replacement = questions.get(superseding)
            if replacement is None or replacement["question_id"] != event["subject"]["question_id"]:
                issues.append(f"review event has invalid superseding version {event['event_id']}")
    for boundary, event_ids in decisive_boundaries.items():
        if len(event_ids) > 1:
            issues.append(f"conflicting decisive review boundary {boundary}: {sorted(event_ids)}")
    for event in source_impacts.values():
        changed = event["changed_reference"]
        if changed["prior_reference_version_id"] not in references or changed["new_reference_version_id"] not in references:
            issues.append(f"source-impact event has unresolved changed reference {event['event_id']}")
        for subject in event["subjects"]:
            question = questions.get(subject["version_id"])
            exact = {key: subject[key] for key in ("question_id", "version_id", "content_sha256")}
            if question is None or validate_exact_binding({"subject": exact}, question):
                issues.append(f"source-impact event has invalid subject {event['event_id']}:{subject['version_id']}")
    if issues:
        raise ValueError("canonical integrity validation failed: " + "; ".join(issues[:12]))
    return {
        "identities": identities,
        "questions": questions,
        "references": references,
        "rules": rules,
        "verification_events": verification_events,
        "review_events": review_events,
        "source_impact_events": source_impacts,
    }


def derive_cold_state(index: dict[str, Any]) -> list[dict[str, Any]]:
    questions = index["questions"]
    latest_numbers: dict[str, int] = {}
    for question in questions.values():
        latest_numbers[question["question_id"]] = max(latest_numbers.get(question["question_id"], 0), question["version_number"])
    reviews: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for event in index["review_events"].values():
        reviews[event["subject"]["version_id"]].append(event)
    verifications: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for event in index["verification_events"].values():
        verifications[event["subject"]["version_id"]].append(event)
    impacts: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for event in index["source_impact_events"].values():
        for subject in event["subjects"]:
            impacts[subject["version_id"]].append(event)

    rows: list[dict[str, Any]] = []
    for question in sorted(questions.values(), key=lambda item: (item["question_id"], item["version_number"])):
        version_id = question["version_id"]
        decisive = sorted(
            (event for event in reviews[version_id] if event["action"] != "comment"),
            key=lambda event: (event["recorded_at"], event["event_id"]),
        )
        latest_decisive = decisive[-1] if decisive else None
        verification_history = sorted(verifications[version_id], key=lambda event: (event["recorded_at"], event["event_id"]))
        verification = verification_history[-1] if verification_history else None
        required_check_ids = REQUIRED_CHECK_POLICIES.get(verification["required_check_set_id"]) if verification else None
        observed_check_ids = {check["check_id"] for check in verification["checks"]} if verification else set()
        mechanical_pass = bool(
            verification
            and required_check_ids is not None
            and observed_check_ids == set(required_check_ids)
            and all(check["outcome"] == "pass" for check in verification["checks"])
        )
        latest_impact_history = sorted(impacts[version_id], key=lambda event: (event["recorded_at"], event["event_id"]))
        latest_impact = latest_impact_history[-1] if latest_impact_history else None
        source_impact_clear = latest_impact is None or latest_impact["impact_outcome"] != "quarantine"
        applied_rules = [index["rules"][trace["rule_version_id"]] for trace in question["content"]["rule_trace"]]
        rules_current = all(rule["content"]["currency"]["assessment"] == "current" for rule in applied_rules)
        applied_references = [
            index["references"][citation["reference_version_id"]]
            for rule in applied_rules
            for citation in rule["content"]["source_citations"]
        ]
        references_admitted_current = all(
            reference["record_purpose"] == "admitted_evidence" and reference["currency"]["assessment"] == "current"
            for reference in applied_references
        )
        is_latest = question["version_number"] == latest_numbers[question["question_id"]]
        approved = bool(
            latest_decisive
            and latest_decisive["action"] == "approve"
            and latest_decisive["actor"]["actor_type"] == "human"
            and latest_decisive["actor"]["actor_id"] == "james"
        )
        eligible_purpose = question["content"]["authorship"]["purpose"] != "schema_fixture"
        learner_ready = all((is_latest, approved, mechanical_pass, source_impact_clear, rules_current, references_admitted_current, eligible_purpose))
        rows.append(
            {
                "question_id": question["question_id"],
                "version_id": version_id,
                "version_number": question["version_number"],
                "content_sha256": question["content_sha256"],
                "is_latest_version": is_latest,
                "latest_decisive_action": latest_decisive["action"] if latest_decisive else None,
                "latest_decisive_event_id": latest_decisive["event_id"] if latest_decisive else None,
                "latest_verification_event_id": verification["event_id"] if verification else None,
                "mechanical_checks_pass": mechanical_pass,
                "source_impact_clear": source_impact_clear,
                "rules_current": rules_current,
                "references_admitted_current": references_admitted_current,
                "learner_ready": learner_ready,
                "coverage_contribution": learner_ready and question["content"]["authorship"]["purpose"] == "production_candidate",
            }
        )
    return rows


def _insert_projection(connection: sqlite3.Connection, index: dict[str, Any], manifest_id: str, built_at: str, manifest_json: str) -> None:
    connection.execute(
        "INSERT INTO projection_manifest VALUES (?, ?, ?, ?, ?)",
        (manifest_id, BUILDER_ID, BUILDER_VERSION, built_at, manifest_json),
    )
    for check_set_id, check_ids in REQUIRED_CHECK_POLICIES.items():
        connection.execute("INSERT INTO required_check_policy VALUES (?, ?)", (check_set_id, len(check_ids)))
        for check_id in check_ids:
            connection.execute("INSERT INTO required_check_policy_item VALUES (?, ?)", (check_set_id, check_id))
    for identity in sorted(index["identities"].values(), key=lambda item: item["question_id"]):
        connection.execute(
            "INSERT INTO question_identity VALUES (?, ?, ?)",
            (identity["question_id"], identity["created_at"], _json(identity["creation_provenance"])),
        )
    for reference in sorted(index["references"].values(), key=lambda item: item["reference_version_id"]):
        connection.execute(
            "INSERT INTO reference_version VALUES (?, ?, ?, ?, ?, ?)",
            (reference["reference_version_id"], reference["reference_id"], reference["version_number"], reference["record_purpose"], reference["authority_class"], _json(reference)),
        )
    for rule in sorted(index["rules"].values(), key=lambda item: item["rule_version_id"]):
        connection.execute(
            "INSERT INTO rule_version VALUES (?, ?, ?, ?, ?)",
            (rule["rule_version_id"], rule["rule_id"], rule["version_number"], rule["content_sha256"], _json(rule["content"])),
        )
        for ordinal, citation in enumerate(rule["content"]["source_citations"], 1):
            connection.execute(
                "INSERT INTO rule_source_reference VALUES (?, ?, ?, ?)",
                (rule["rule_version_id"], ordinal, citation["reference_version_id"], citation["role"]),
            )
    for question in sorted(index["questions"].values(), key=lambda item: item["version_id"]):
        content = question["content"]
        connection.execute(
            "INSERT INTO question_version VALUES (?, ?, ?, ?, ?)",
            (question["version_id"], question["question_id"], question["version_number"], question["content_sha256"], _json(content)),
        )
        for option in content["options"]:
            connection.execute(
                "INSERT INTO question_option VALUES (?, ?, ?, ?, ?)",
                (question["version_id"], option["option_id"], option["text"], int(option["is_keyed"]), _json(option.get("error_model")) if option.get("error_model") else None),
            )
        for ordinal, mapping in enumerate(content["blueprint_mappings"], 1):
            connection.execute(
                "INSERT INTO blueprint_mapping VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (question["version_id"], ordinal, mapping["taxonomy_id"], mapping["area_id"], mapping["group_id"], mapping["topic_id"], mapping["representative_task_id"], mapping["skill_level"], mapping["mapping_rationale"], mapping["mcq_scope_limit"]),
            )
        for dimension in content["difficulty_profile"]:
            connection.execute(
                "INSERT INTO difficulty_dimension VALUES (?, ?, ?, ?, ?, ?)",
                (question["version_id"], dimension["dimension_id"], dimension["rubric_version_id"], dimension["rubric_status"], dimension["provisional_level"], _json(dimension["observable_measurements"])),
            )
        for ordinal, trace in enumerate(content["rule_trace"], 1):
            connection.execute(
                "INSERT INTO question_rule_trace VALUES (?, ?, ?, ?)",
                (question["version_id"], ordinal, trace["rule_version_id"], _json(trace["assertion_ids"])),
            )
    for event in sorted(index["verification_events"].values(), key=lambda item: item["event_id"]):
        subject = event["subject"]
        checker = event["checker"]
        connection.execute(
            "INSERT INTO verification_event VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (event["event_id"], event["recorded_at"], subject["question_id"], subject["version_id"], subject["content_sha256"], checker["checker_id"], checker["checker_version"], event["required_check_set_id"], _json(event["input_evidence"])),
        )
        for check in event["checks"]:
            connection.execute(
                "INSERT INTO verification_check VALUES (?, ?, ?, ?, ?, ?, ?)",
                (event["event_id"], check["check_id"], check["category"], check["outcome"], check["detail"], _json(check.get("evidence", [])), _json(check["calibration_fixture_ids"])),
            )
    for event in sorted(index["review_events"].values(), key=lambda item: item["event_id"]):
        actor = event["actor"]
        subject = event["subject"]
        connection.execute(
            "INSERT INTO review_event VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (event["event_id"], event["recorded_at"], event["action"], actor["actor_type"], actor["actor_id"], actor["display_name"], subject["question_id"], subject["version_id"], subject["content_sha256"], event["comment"], event.get("reason_code"), event.get("superseding_version_id")),
        )
    for event in sorted(index["source_impact_events"].values(), key=lambda item: item["event_id"]):
        actor = event["actor"]
        changed = event["changed_reference"]
        connection.execute(
            "INSERT INTO source_impact_event VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (event["event_id"], event["recorded_at"], actor["actor_type"], actor["actor_id"], changed["prior_reference_version_id"], changed["new_reference_version_id"], event["impact_outcome"], event["basis"]),
        )
        for subject in event["subjects"]:
            connection.execute(
                "INSERT INTO source_impact_subject VALUES (?, ?, ?, ?, ?)",
                (event["event_id"], subject["version_id"], subject["question_id"], subject["content_sha256"], subject["impact_detail"]),
            )


def _projection_state(connection: sqlite3.Connection) -> list[dict[str, Any]]:
    connection.row_factory = sqlite3.Row
    rows = connection.execute(
        "SELECT question_id, version_id, version_number, content_sha256, is_latest_version, latest_decisive_action, latest_decisive_event_id, latest_verification_event_id, mechanical_checks_pass, source_impact_clear, rules_current, references_admitted_current, learner_ready, coverage_contribution FROM learner_ready_projection ORDER BY question_id, version_number"
    ).fetchall()
    boolean_fields = {"is_latest_version", "mechanical_checks_pass", "source_impact_clear", "rules_current", "references_admitted_current", "learner_ready", "coverage_contribution"}
    return [{key: bool(row[key]) if key in boolean_fields else row[key] for key in row.keys()} for row in rows]


def build_projection(output_path: Path, project_root: Path = PROJECT_ROOT) -> dict[str, Any]:
    records, manifest_entries = _load_records(project_root)
    index = validate_canonical_records(records, project_root)
    cold_state = derive_cold_state(index)
    manifest_json = _json(manifest_entries)
    manifest_id = "far-projection-inputs-" + hashlib.sha256(manifest_json.encode("utf-8")).hexdigest()
    timestamps = [record["created_at"] for record in index["identities"].values()]
    timestamps.extend(event["recorded_at"] for family in ("verification_events", "review_events", "source_impact_events") for event in index[family].values())
    built_at = max(timestamps)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{output_path.name}.", suffix=".tmp", dir=output_path.parent)
    os.close(descriptor)
    temporary_path = Path(temporary_name)
    try:
        connection = sqlite3.connect(temporary_path)
        try:
            connection.executescript((project_root / "schema/review-projection.sql").read_text(encoding="utf-8"))
            with connection:
                _insert_projection(connection, index, manifest_id, built_at, manifest_json)
            foreign_key_issues = connection.execute("PRAGMA foreign_key_check").fetchall()
            integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
            if foreign_key_issues or integrity != "ok":
                raise ValueError(f"projection integrity failure: foreign_keys={foreign_key_issues} integrity={integrity}")
            sql_state = _projection_state(connection)
            if sql_state != cold_state:
                raise ValueError("SQLite derived state differs from independent cold JSON reconstruction")
        finally:
            connection.close()
        os.replace(temporary_path, output_path)
    except Exception:
        temporary_path.unlink(missing_ok=True)
        raise
    ddl_sha256 = _sha256(project_root / "schema/review-projection.sql")
    counts = {family: len(found) for family, found in records.items()}
    return {
        "schema_version": "1.0.0",
        "builder_id": BUILDER_ID,
        "builder_version": BUILDER_VERSION,
        "projection_manifest_id": manifest_id,
        "canonical_input_count": len(manifest_entries),
        "canonical_family_counts": counts,
        "ddl_sha256": ddl_sha256,
        "projection_equivalent_to_cold_reconstruction": True,
        "state_summary": {
            "question_identity_count": len(index["identities"]),
            "question_version_count": len(index["questions"]),
            "latest_version_count": sum(row["is_latest_version"] for row in cold_state),
            "learner_ready_count": sum(row["learner_ready"] for row in cold_state),
            "coverage_contribution_count": sum(row["coverage_contribution"] for row in cold_state),
            "superseded_approved_or_invalidated_count": sum((not row["is_latest_version"]) and row["latest_decisive_action"] in {"approve", "auto_invalidate"} for row in cold_state),
        },
        "exact_version_state": cold_state,
        "claim_limit": "SQLite is a disposable projection. This receipt proves reconstruction equivalence for current canonical records; it grants no G3 approval or production coverage.",
    }


def deterministic_json_bytes(report: dict[str, Any]) -> bytes:
    return (json.dumps(report, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Transactionally rebuild the disposable FAR review SQLite projection from canonical JSON.")
    parser.add_argument("--output", type=Path, default=PROJECT_ROOT / "build/review.sqlite")
    parser.add_argument("--report", type=Path, default=PROJECT_ROOT / "reports/p2-projection-reconstruction.json")
    args = parser.parse_args()
    report = build_projection(args.output)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_bytes(deterministic_json_bytes(report))
    summary = report["state_summary"]
    print(
        f"PASS rebuilt projection: versions={summary['question_version_count']} "
        f"ready={summary['learner_ready_count']} coverage={summary['coverage_contribution_count']} "
        f"manifest={report['projection_manifest_id']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
