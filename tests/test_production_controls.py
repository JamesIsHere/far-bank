from __future__ import annotations

import sys
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from calibrate_production_controls import (  # noqa: E402
    build_calibration_report,
    deterministic_json_bytes,
)
from validate_p1_records import load_json, schema_issues  # noqa: E402
from verify_production_controls import (  # noqa: E402
    build_clean_calibration_bank,
    load_contract,
    run_checks,
)


class ProductionControlCalibration(unittest.TestCase):
    def test_new_schemas_are_valid_and_clean_records_conform(self) -> None:
        contract_schema = load_json(PROJECT_ROOT / "schema/production-contract.schema.json")
        evidence_schema = load_json(PROJECT_ROOT / "schema/production-control-evidence.schema.json")
        Draft202012Validator.check_schema(contract_schema)
        Draft202012Validator.check_schema(evidence_schema)
        self.assertEqual([], schema_issues(contract_schema, load_contract(), "PRODUCTION_CONTRACT_SCHEMA"))
        for record in build_clean_calibration_bank():
            self.assertEqual([], schema_issues(evidence_schema, record, "PRODUCTION_EVIDENCE_SCHEMA"))

    def test_clean_calibration_bank_passes_every_control(self) -> None:
        records = build_clean_calibration_bank()
        results = run_checks(load_contract(), records)
        self.assertEqual(353, len(records))
        self.assertEqual(9, len(results))
        self.assertEqual([], [result for result in results if not result.passed])
        self.assertEqual(len(results), len({result.check_id for result in results}))

    def test_every_control_has_one_observed_red_corruption_and_no_waiver(self) -> None:
        report = build_calibration_report()
        summary = report["calibration_summary"]
        self.assertEqual(9, summary["individual_check_count"])
        self.assertEqual(9, summary["purpose_built_red_fixture_count"])
        self.assertEqual(0, summary["waiver_count"])
        self.assertEqual([], summary["uncalibrated_check_ids"])
        for check in report["checks"]:
            with self.subTest(check_id=check["check_id"]):
                self.assertEqual("pass", check["clean_outcome"])
                self.assertEqual("fail", check["corrupt_outcome"])
                self.assertTrue(check["corrupt_detail"])

    def test_checked_in_report_is_deterministic(self) -> None:
        expected = deterministic_json_bytes(build_calibration_report())
        actual = (PROJECT_ROOT / "reports/p2-production-control-calibration.json").read_bytes()
        self.assertEqual(expected, actual)

    def test_calibration_records_cannot_be_mistaken_for_production(self) -> None:
        records = build_clean_calibration_bank()
        self.assertEqual({"calibration_fixture"}, {record["purpose"] for record in records})
        self.assertIn("does not approve any production item", load_contract()["claim_limit"])
        self.assertFalse((PROJECT_ROOT / "data/production").exists())


if __name__ == "__main__":
    unittest.main()
