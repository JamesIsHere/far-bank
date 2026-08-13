from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from validate_p1_records import PROJECT_ROOT, canonical_content_sha256, load_json
from verify_questions import (
    CHECKER_ID,
    CHECKER_VERSION,
    CHECKS,
    REQUIRED_CHECK_SET_ID,
    QuestionBundle,
    load_fixture_bundle,
    run_checks,
)


def apply_mutation(document: Any, mutation: dict[str, Any]) -> None:
    parts = [part.replace("~1", "/").replace("~0", "~") for part in mutation["path"].split("/")[1:]]
    parent = document
    for part in parts[:-1]:
        parent = parent[int(part)] if isinstance(parent, list) else parent[part]
    key = parts[-1]
    operation = mutation["operation"]
    if operation == "remove":
        if isinstance(parent, list):
            parent.pop(int(key))
        else:
            del parent[key]
    elif operation in {"add", "replace"}:
        if isinstance(parent, list):
            parent[int(key)] = mutation["value"]
        else:
            parent[key] = mutation["value"]
    else:
        raise ValueError(f"unsupported mutation operation {operation}")


def apply_corruption(baseline: QuestionBundle, definition: dict[str, Any]) -> QuestionBundle:
    corrupt = baseline.clone()
    for mutation in definition["mutations"]:
        record = getattr(corrupt, mutation["record"])
        apply_mutation(record, mutation)

    if "rule" in definition["rehash"]:
        corrupt.rule["content_sha256"] = canonical_content_sha256(corrupt.rule["content"])
    if "question" in definition["rehash"]:
        corrupt.question["content_sha256"] = canonical_content_sha256(corrupt.question["content"])
    if definition["rebind_events"]:
        digest = corrupt.question["content_sha256"]
        corrupt.review["subject"]["content_sha256"] = digest
        corrupt.verification["subject"]["content_sha256"] = digest
        corrupt.verification["input_evidence"][0]["sha256"] = digest
    return corrupt


def build_calibration_report(project_root: Path = PROJECT_ROOT) -> dict[str, Any]:
    baseline = load_fixture_bundle(project_root)
    clean_results = run_checks(baseline, project_root)
    clean_by_id = {result.check_id: result for result in clean_results}
    failures = [result for result in clean_results if not result.passed]
    if failures:
        detail = "; ".join(f"{result.check_id}: {result.detail}" for result in failures)
        raise RuntimeError(f"clean verifier baseline is not green: {detail}")

    check_functions = {function(baseline, project_root).check_id: function for function in CHECKS}
    corruption_dir = project_root / "fixtures" / "verifier" / "corruptions"
    definitions = [load_json(path) for path in sorted(corruption_dir.glob("*.json"))]
    definition_by_check: dict[str, dict[str, Any]] = {}
    for definition in definitions:
        if definition["check_id"] in definition_by_check:
            raise RuntimeError(f"multiple calibration fixtures target {definition['check_id']}")
        definition_by_check[definition["check_id"]] = definition

    catalog: list[dict[str, Any]] = []
    for clean in clean_results:
        definition = definition_by_check.get(clean.check_id)
        if definition is None:
            raise RuntimeError(f"missing red calibration fixture for {clean.check_id}")
        corrupt = apply_corruption(baseline, definition)
        red = check_functions[clean.check_id](corrupt, project_root)
        if red.passed:
            raise RuntimeError(f"{definition['fixture_id']} did not drive {clean.check_id} red")
        catalog.append(
            {
                "check_id": clean.check_id,
                "category": clean.category,
                "clean_outcome": "pass",
                "clean_detail": clean.detail,
                "calibration_fixture_id": definition["fixture_id"],
                "corrupt_outcome": "fail",
                "corrupt_detail": red.detail,
            }
        )

    extras = sorted(set(definition_by_check) - set(clean_by_id))
    if extras:
        raise RuntimeError(f"calibration fixtures target unknown checks: {extras}")

    return {
        "schema_version": "1.0.0",
        "checker_id": CHECKER_ID,
        "checker_version": CHECKER_VERSION,
        "required_check_set_id": REQUIRED_CHECK_SET_ID,
        "baseline": {
            "purpose": baseline.question["content"]["authorship"]["purpose"],
            "question_id": baseline.question["question_id"],
            "version_id": baseline.question["version_id"],
            "content_sha256": baseline.question["content_sha256"],
            "claim_limit": "Fixture-world calibration only; not correctness, source admission, human approval, or learner readiness."
        },
        "checks": catalog,
        "calibration_summary": {
            "individual_check_count": len(catalog),
            "purpose_built_red_fixture_count": len(definitions),
            "waiver_count": 0,
            "uncalibrated_check_ids": []
        }
    }


def deterministic_json_bytes(report: dict[str, Any]) -> bytes:
    return (json.dumps(report, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Red-calibrate every individual P1 question-verifier check.")
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "reports" / "p1-verifier-calibration.json",
    )
    args = parser.parse_args()
    report = build_calibration_report()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(deterministic_json_bytes(report))
    print(
        f"PASS calibrated {report['calibration_summary']['individual_check_count']} individual checks "
        f"with {report['calibration_summary']['purpose_built_red_fixture_count']} purpose-built corruptions; "
        f"waivers={report['calibration_summary']['waiver_count']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
