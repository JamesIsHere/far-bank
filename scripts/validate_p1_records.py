from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


PROJECT_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class ContractIssue:
    contract_id: str
    detail: str


def canonical_content_sha256(content: dict[str, Any]) -> str:
    payload = json.dumps(
        content,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def schema_issues(schema: dict[str, Any], instance: dict[str, Any], contract_id: str) -> list[ContractIssue]:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return [
        ContractIssue(contract_id, f"{list(error.absolute_path)}: {error.message}")
        for error in sorted(validator.iter_errors(instance), key=lambda item: list(item.absolute_path))
    ]


def taxonomy_task_index(taxonomy: dict[str, Any]) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for area in taxonomy["areas"]:
        for group in area["groups"]:
            for task in group["tasks"]:
                index[task["id"]] = {
                    "taxonomy_id": taxonomy["taxonomy_id"],
                    "area_id": area["id"],
                    "group_id": group["id"],
                    "topic_id": None,
                    "skill_level": task["skill_level"],
                }
            for topic in group["topics"]:
                for task in topic["tasks"]:
                    index[task["id"]] = {
                        "taxonomy_id": taxonomy["taxonomy_id"],
                        "area_id": area["id"],
                        "group_id": group["id"],
                        "topic_id": topic["id"],
                        "skill_level": task["skill_level"],
                    }
    return index


def validate_question_contract(
    question: dict[str, Any],
    question_schema: dict[str, Any],
    taxonomy: dict[str, Any],
    rules_by_version: dict[str, dict[str, Any]],
) -> list[ContractIssue]:
    issues = schema_issues(question_schema, question, "QUESTION_SCHEMA")
    if issues:
        return issues

    expected_version_id = f"{question['question_id']}.v{question['version_number']:03d}"
    if question["version_id"] != expected_version_id:
        issues.append(ContractIssue("VERSION_IDENTITY", "version_id does not match question_id and version_number"))

    actual_hash = canonical_content_sha256(question["content"])
    if question["content_sha256"] != actual_hash:
        issues.append(ContractIssue("CONTENT_HASH", f"recorded {question['content_sha256']} but computed {actual_hash}"))

    content = question["content"]
    options = content["options"]
    option_ids = [option["option_id"] for option in options]
    if set(option_ids) != {"A", "B", "C", "D"} or len(set(option_ids)) != 4:
        issues.append(ContractIssue("OPTION_IDENTITIES", "options must use A, B, C, and D exactly once"))
    normalized_text = [" ".join(option["text"].split()).casefold() for option in options]
    if len(set(normalized_text)) != 4:
        issues.append(ContractIssue("OPTION_TEXT_UNIQUENESS", "option text must be unique after whitespace and case normalization"))
    keyed = [option["option_id"] for option in options if option["is_keyed"]]
    if keyed != [content["solution"]["keyed_answer_option_id"]]:
        issues.append(ContractIssue("KEY_BINDING", "solution key must match the sole keyed option"))

    expected_dimensions = {
        "accounting_complexity",
        "reasoning_steps",
        "reading_fact_selection",
        "rule_convention_pressure",
        "distractor_elimination_burden",
        "realistic_time_pressure",
    }
    actual_dimensions = [entry["dimension_id"] for entry in content["difficulty_profile"]]
    if set(actual_dimensions) != expected_dimensions or len(set(actual_dimensions)) != 6:
        issues.append(ContractIssue("DIFFICULTY_DIMENSIONS", "all six named difficulty dimensions must appear exactly once"))

    task_index = taxonomy_task_index(taxonomy)
    for mapping in content["blueprint_mappings"]:
        resolved = task_index.get(mapping["representative_task_id"])
        recorded = {key: mapping[key] for key in ("taxonomy_id", "area_id", "group_id", "topic_id", "skill_level")}
        if resolved != recorded:
            issues.append(
                ContractIssue(
                    "BLUEPRINT_MAPPING",
                    f"{mapping['representative_task_id']} does not resolve to the recorded taxonomy path and skill",
                )
            )

    fact_ids = [fact["fact_id"] for fact in content["facts"]]
    if len(set(fact_ids)) != len(fact_ids):
        issues.append(ContractIssue("FACT_IDENTITIES", "fact_id values must be unique"))
    known_fact_ids = set(fact_ids)

    for trace in content["rule_trace"]:
        rule = rules_by_version.get(trace["rule_version_id"])
        if rule is None:
            issues.append(ContractIssue("RULE_TRACE", f"unresolved rule version {trace['rule_version_id']}"))
            continue
        known_assertions = {entry["assertion_id"] for entry in rule["content"]["assertions"]}
        if not set(trace["assertion_ids"]).issubset(known_assertions):
            issues.append(ContractIssue("RULE_TRACE", "question trace contains an assertion absent from its rule version"))
        if not set(trace["applied_to_fact_ids"]).issubset(known_fact_ids):
            issues.append(ContractIssue("RULE_TRACE", "question trace applies a rule to an unknown fact"))

    for step in content["solution"]["steps"]:
        if not set(step["fact_ids_used"]).issubset(known_fact_ids):
            issues.append(ContractIssue("SOLUTION_REFERENCES", "solution step cites an unknown fact"))

    return issues


def validate_exact_binding(event: dict[str, Any], question: dict[str, Any]) -> list[ContractIssue]:
    expected = {
        "question_id": question["question_id"],
        "version_id": question["version_id"],
        "content_sha256": question["content_sha256"],
    }
    if event["subject"] != expected:
        return [ContractIssue("EXACT_VERSION_BINDING", "event subject does not match the immutable question version")]
    return []


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_checked_in_fixture_bundle(project_root: Path = PROJECT_ROOT) -> list[ContractIssue]:
    schema_dir = project_root / "schema"
    fixture_dir = project_root / "fixtures" / "questions"
    taxonomy = load_json(project_root / "data" / "far-taxonomy.json")
    records = {
        "identity": load_json(fixture_dir / "valid-question-identity.json"),
        "reference": load_json(fixture_dir / "valid-reference-version.json"),
        "rule": load_json(fixture_dir / "valid-rule-version.json"),
        "question": load_json(fixture_dir / "valid-question-version.json"),
        "verification": load_json(fixture_dir / "valid-verification-event.json"),
        "review": load_json(fixture_dir / "valid-review-event-approve.json"),
        "source_impact": load_json(fixture_dir / "valid-source-impact-event.json"),
    }
    schema_names = {
        "identity": "question-identity.schema.json",
        "reference": "reference-version.schema.json",
        "rule": "rule-version.schema.json",
        "verification": "verification-event.schema.json",
        "review": "review-event.schema.json",
        "source_impact": "source-impact-event.schema.json",
    }

    issues: list[ContractIssue] = []
    for record_name, schema_name in schema_names.items():
        issues.extend(schema_issues(load_json(schema_dir / schema_name), records[record_name], f"{record_name.upper()}_SCHEMA"))

    rule_hash = canonical_content_sha256(records["rule"]["content"])
    if records["rule"]["content_sha256"] != rule_hash:
        issues.append(ContractIssue("RULE_CONTENT_HASH", "rule content hash does not match its canonical content"))

    expected_reference_version_id = (
        f"{records['reference']['reference_id']}.v{records['reference']['version_number']:03d}"
    )
    if records["reference"]["reference_version_id"] != expected_reference_version_id:
        issues.append(ContractIssue("REFERENCE_VERSION_IDENTITY", "reference version ID does not match its identity and number"))

    expected_rule_version_id = f"{records['rule']['rule_id']}.v{records['rule']['version_number']:03d}"
    if records["rule"]["rule_version_id"] != expected_rule_version_id:
        issues.append(ContractIssue("RULE_VERSION_IDENTITY", "rule version ID does not match its identity and number"))
    reference_ids = {records["reference"]["reference_version_id"]}
    for citation in records["rule"]["content"]["source_citations"]:
        if citation["reference_version_id"] not in reference_ids:
            issues.append(ContractIssue("RULE_SOURCE_TRACE", "rule citation does not resolve to the fixture reference"))

    issues.extend(
        validate_question_contract(
            records["question"],
            load_json(schema_dir / "question-version.schema.json"),
            taxonomy,
            {records["rule"]["rule_version_id"]: records["rule"]},
        )
    )
    issues.extend(validate_exact_binding(records["verification"], records["question"]))
    issues.extend(validate_exact_binding(records["review"], records["question"]))
    for subject in records["source_impact"]["subjects"]:
        exact_subject = {
            key: subject[key]
            for key in ("question_id", "version_id", "content_sha256")
        }
        issues.extend(validate_exact_binding({"subject": exact_subject}, records["question"]))
    if records["identity"]["question_id"] != records["question"]["question_id"]:
        issues.append(ContractIssue("QUESTION_IDENTITY", "question version does not belong to its stable identity"))
    return issues


if __name__ == "__main__":
    found = validate_checked_in_fixture_bundle()
    if found:
        for issue in found:
            print(f"FAIL {issue.contract_id}: {issue.detail}")
        raise SystemExit(1)
    print("PASS P1.1 checked-in fixture bundle satisfies schema and cross-record contracts")
