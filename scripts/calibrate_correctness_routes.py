from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from validate_p1_records import PROJECT_ROOT, load_json
from verify_correctness_routes import (
    CHECKER_ID,
    CHECKER_VERSION,
    REQUIRED_CHECK_SET_ID,
    ROUTE_TYPES,
    check_route,
    load_route_fixtures,
    run_checks,
)


def apply_mutation(document: Any, mutation: dict[str, Any]) -> None:
    parts = [part.replace("~1", "/").replace("~0", "~") for part in mutation["path"].split("/")[1:]]
    parent = document
    for part in parts[:-1]:
        parent = parent[int(part)] if isinstance(parent, list) else parent[part]
    key = parts[-1]
    operation = mutation["operation"]
    if operation == "replace":
        if isinstance(parent, list):
            parent[int(key)] = mutation["value"]
        else:
            parent[key] = mutation["value"]
    elif operation == "remove":
        if isinstance(parent, list):
            parent.pop(int(key))
        else:
            del parent[key]
    else:
        raise ValueError(f"unsupported mutation operation {operation}")


def build_calibration_report(project_root: Path = PROJECT_ROOT) -> dict[str, Any]:
    clean_records = load_route_fixtures(project_root)
    clean_results = run_checks(clean_records, project_root)
    failures = [result for result in clean_results if not result.passed]
    if failures:
        raise RuntimeError("clean correctness-route baseline is red: " + "; ".join(f"{result.check_id}: {result.detail}" for result in failures))
    records_by_id = {record["fixture_id"]: record for record in clean_records}
    definitions = [load_json(path) for path in sorted((project_root / "fixtures/correctness-routes/corruptions").glob("*.json"))]
    definitions_by_check = {definition["check_id"]: definition for definition in definitions}
    if len(definitions_by_check) != len(definitions):
        raise RuntimeError("multiple correctness-route corruptions target one check")

    catalog: list[dict[str, Any]] = []
    for clean in clean_results:
        definition = definitions_by_check.get(clean.check_id)
        if definition is None:
            raise RuntimeError(f"missing correctness-route corruption for {clean.check_id}")
        baseline = records_by_id.get(definition["fixture_id"])
        if baseline is None:
            raise RuntimeError(f"corruption names unknown fixture {definition['fixture_id']}")
        corrupt = copy.deepcopy(baseline)
        for mutation in definition["mutations"]:
            apply_mutation(corrupt, mutation)
        red = check_route(corrupt, project_root)
        if red.passed:
            raise RuntimeError(f"{definition['corruption_id']} did not drive {clean.check_id} red")
        catalog.append(
            {
                "check_id": clean.check_id,
                "route_type": clean.route_type,
                "clean_fixture_id": baseline["fixture_id"],
                "clean_outcome": "pass",
                "clean_detail": clean.detail,
                "corruption_id": definition["corruption_id"],
                "corrupt_outcome": "fail",
                "corrupt_detail": red.detail,
            }
        )
    extras = sorted(set(definitions_by_check) - {result.check_id for result in clean_results})
    if extras:
        raise RuntimeError(f"corruptions target unknown route checks: {extras}")
    return {
        "schema_version": "1.0.0",
        "checker_id": CHECKER_ID,
        "checker_version": CHECKER_VERSION,
        "required_check_set_id": REQUIRED_CHECK_SET_ID,
        "contract_id": "far-g2-production-contract.v001",
        "route_types": list(ROUTE_TYPES),
        "baseline": {
            "purpose": "calibration_fixture",
            "fixture_count": len(clean_records),
            "claim_limit": "Route fixtures calibrate independent evaluator behavior only; they are not accounting authority, canonical questions, human approvals, or production coverage.",
        },
        "checks": catalog,
        "calibration_summary": {
            "route_check_count": len(catalog),
            "known_bad_fixture_count": len(definitions),
            "waiver_count": 0,
            "uncalibrated_route_types": [],
        },
    }


def deterministic_json_bytes(report: dict[str, Any]) -> bytes:
    return (json.dumps(report, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def main() -> int:
    report = build_calibration_report()
    output = PROJECT_ROOT / "reports/p2-correctness-route-calibration.json"
    output.write_bytes(deterministic_json_bytes(report))
    summary = report["calibration_summary"]
    print(
        f"PASS calibrated {summary['route_check_count']} independent routes with "
        f"{summary['known_bad_fixture_count']} known-bad fixtures; waivers={summary['waiver_count']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
