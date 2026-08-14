from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from calibrate_correctness_routes import build_calibration_report, deterministic_json_bytes  # noqa: E402
from validate_p1_records import load_json, schema_issues  # noqa: E402
from verify_correctness_routes import (  # noqa: E402
    ROUTE_TYPES,
    check_route,
    load_route_fixtures,
    run_checks,
)


class CorrectnessRouteCalibration(unittest.TestCase):
    def test_schema_is_valid_and_all_clean_fixtures_conform(self) -> None:
        schema = load_json(PROJECT_ROOT / "schema/correctness-route.schema.json")
        reference_schema = load_json(PROJECT_ROOT / "schema/assertion-reference-fixture.schema.json")
        Draft202012Validator.check_schema(schema)
        Draft202012Validator.check_schema(reference_schema)
        records = load_route_fixtures()
        self.assertEqual(10, len(records))
        for record in records:
            with self.subTest(route_type=record["route_type"]):
                self.assertEqual([], schema_issues(schema, record, "CORRECTNESS_ROUTE_SCHEMA"))
        reference = load_json(PROJECT_ROOT / "fixtures/correctness-routes/reference/classification-assertions.json")
        self.assertEqual([], schema_issues(reference_schema, reference, "ASSERTION_REFERENCE_SCHEMA"))

    def test_every_required_route_executes_independently(self) -> None:
        records = load_route_fixtures()
        results = run_checks(records)
        self.assertEqual(set(ROUTE_TYPES), {record["route_type"] for record in records})
        self.assertEqual(10, len(results))
        self.assertEqual([], [result for result in results if not result.passed])

    def test_every_route_rejects_its_known_bad_fixture_without_waiver(self) -> None:
        report = build_calibration_report()
        summary = report["calibration_summary"]
        self.assertEqual(10, summary["route_check_count"])
        self.assertEqual(10, summary["known_bad_fixture_count"])
        self.assertEqual(0, summary["waiver_count"])
        self.assertEqual([], summary["uncalibrated_route_types"])
        for check in report["checks"]:
            with self.subTest(route_type=check["route_type"]):
                self.assertEqual("pass", check["clean_outcome"])
                self.assertEqual("fail", check["corrupt_outcome"])
                self.assertTrue(check["corrupt_detail"])

    def test_checked_in_report_is_deterministic(self) -> None:
        expected = deterministic_json_bytes(build_calibration_report())
        actual = (PROJECT_ROOT / "reports/p2-correctness-route-calibration.json").read_bytes()
        self.assertEqual(expected, actual)

    def test_shared_producer_identity_is_rejected(self) -> None:
        record = copy.deepcopy(load_route_fixtures()[0])
        record["verifier_component_id"] = record["producer_component_id"]
        result = check_route(record)
        self.assertFalse(result.passed)
        self.assertIn("not independent", result.detail)

    def test_route_fixtures_cannot_be_mistaken_for_questions(self) -> None:
        records = load_route_fixtures()
        self.assertEqual({"calibration_fixture"}, {record["purpose"] for record in records})
        self.assertFalse((PROJECT_ROOT / "data/production").exists())


if __name__ == "__main__":
    unittest.main()
