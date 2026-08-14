from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from validate_p1_records import PROJECT_ROOT, load_json
from verify_production_controls import (
    CHECKER_ID,
    CHECKER_VERSION,
    CHECKS,
    CONTRACT_CANONICAL_SHA256,
    REQUIRED_CHECK_SET_ID,
    build_clean_calibration_bank,
    load_contract,
    run_checks,
)


def apply_corruption(
    contract: dict[str, Any],
    records: list[dict[str, Any]],
    definition: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    corrupt_contract = copy.deepcopy(contract)
    corrupt_records = copy.deepcopy(records)
    corruption_type = definition["corruption_type"]
    if corruption_type == "bad_goal_hash":
        corrupt_contract["ratification"]["goal_sha256"] = "0" * 64
    elif corruption_type == "stem_bin_mismatch":
        corrupt_records[0]["observations"]["stem_length_bin"] = "dense"
    elif corruption_type == "unsupported_difficulty_level":
        profile = corrupt_records[0]["difficulty_profile"]
        next(entry for entry in profile if entry["dimension_id"] == "reasoning_steps")["level"] = 5
    elif corruption_type == "prose_screen_failure":
        corrupt_records[0]["prose_evidence"]["double_negative_screen_passed"] = False
    elif corruption_type == "drop_task_minimum":
        task_id = corrupt_records[0]["mapping"]["primary_task_id"]
        first = next(index for index, record in enumerate(corrupt_records) if record["mapping"]["primary_task_id"] == task_id)
        corrupt_records.pop(first)
    elif corruption_type == "erase_indirect_ask_bin":
        for record in corrupt_records:
            record["observations"]["ask_placement"] = "direct_final_sentence"
    elif corruption_type == "clone_task_minimum":
        task_id = corrupt_records[0]["mapping"]["primary_task_id"]
        items = [record for record in corrupt_records if record["mapping"]["primary_task_id"] == task_id][:3]
        source = items[0]["observations"]
        for item in items[1:]:
            item["observations"]["primary_solution_representation"] = source["primary_solution_representation"]
            item["observations"]["distractor_error_model_ids"] = list(source["distractor_error_model_ids"])
            item["observations"]["fact_pattern_id"] = source["fact_pattern_id"]
    elif corruption_type == "template_concentration":
        for record in corrupt_records:
            record["observations"]["stem_template_id"] = "stem-template-monoculture"
    elif corruption_type == "remove_area_representation":
        for record in corrupt_records:
            if record["mapping"]["area_id"] == "far.area.1":
                record["observations"]["primary_solution_representation"] = "formula"
    else:
        raise ValueError(f"unsupported corruption_type {corruption_type}")
    return corrupt_contract, corrupt_records


def build_calibration_report(project_root: Path = PROJECT_ROOT) -> dict[str, Any]:
    contract = load_contract(project_root)
    records = build_clean_calibration_bank(project_root)
    clean_results = run_checks(contract, records, project_root)
    failures = [result for result in clean_results if not result.passed]
    if failures:
        raise RuntimeError("clean production-control baseline is red: " + "; ".join(f"{result.check_id}: {result.detail}" for result in failures))
    checks_by_id = {check(contract, records, project_root).check_id: check for check in CHECKS}
    definitions = [load_json(path) for path in sorted((project_root / "fixtures/production/corruptions").glob("*.json"))]
    definitions_by_check = {definition["check_id"]: definition for definition in definitions}
    if len(definitions_by_check) != len(definitions):
        raise RuntimeError("multiple production-control corruptions target one check")

    catalog: list[dict[str, Any]] = []
    for clean in clean_results:
        definition = definitions_by_check.get(clean.check_id)
        if definition is None:
            raise RuntimeError(f"missing production-control corruption for {clean.check_id}")
        corrupt_contract, corrupt_records = apply_corruption(contract, records, definition)
        red = checks_by_id[clean.check_id](corrupt_contract, corrupt_records, project_root)
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
    extras = sorted(set(definitions_by_check) - set(checks_by_id))
    if extras:
        raise RuntimeError(f"corruptions target unknown production checks: {extras}")
    return {
        "schema_version": "1.0.0",
        "checker_id": CHECKER_ID,
        "checker_version": CHECKER_VERSION,
        "required_check_set_id": REQUIRED_CHECK_SET_ID,
        "contract_id": contract["contract_id"],
        "contract_canonical_sha256": CONTRACT_CANONICAL_SHA256,
        "ratified_goal_sha256": contract["ratification"]["goal_sha256"],
        "baseline": {
            "purpose": "calibration_fixture",
            "synthetic_item_count": len(records),
            "claim_limit": "Synthetic records exercise controls only; they are not canonical questions, learner-ready items, human approvals, or production coverage.",
        },
        "checks": catalog,
        "calibration_summary": {
            "individual_check_count": len(catalog),
            "purpose_built_red_fixture_count": len(definitions),
            "waiver_count": 0,
            "uncalibrated_check_ids": [],
        },
    }


def deterministic_json_bytes(report: dict[str, Any]) -> bytes:
    return (json.dumps(report, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def main() -> int:
    report = build_calibration_report()
    output = PROJECT_ROOT / "reports/p2-production-control-calibration.json"
    output.write_bytes(deterministic_json_bytes(report))
    summary = report["calibration_summary"]
    print(
        f"PASS calibrated {summary['individual_check_count']} production-control checks "
        f"with {summary['purpose_built_red_fixture_count']} red corruptions; waivers={summary['waiver_count']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
