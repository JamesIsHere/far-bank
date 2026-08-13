from __future__ import annotations

import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from calibrate_question_verifier import (  # noqa: E402
    build_calibration_report,
    deterministic_json_bytes,
)
from verify_questions import (  # noqa: E402
    derive_learner_ready,
    load_fixture_bundle,
    run_checks,
)


class QuestionVerifierCalibration(unittest.TestCase):
    def test_clean_fixture_passes_every_individual_check(self) -> None:
        results = run_checks(load_fixture_bundle())
        self.assertEqual(8, len(results))
        self.assertEqual([], [result for result in results if not result.passed])
        self.assertEqual(len(results), len({result.check_id for result in results}))

    def test_every_check_has_one_observed_red_corruption_and_no_waiver(self) -> None:
        report = build_calibration_report()
        summary = report["calibration_summary"]
        self.assertEqual(8, summary["individual_check_count"])
        self.assertEqual(8, summary["purpose_built_red_fixture_count"])
        self.assertEqual(0, summary["waiver_count"])
        self.assertEqual([], summary["uncalibrated_check_ids"])
        for check in report["checks"]:
            with self.subTest(check_id=check["check_id"]):
                self.assertEqual("pass", check["clean_outcome"])
                self.assertEqual("fail", check["corrupt_outcome"])
                self.assertTrue(check["corrupt_detail"])

    def test_checked_in_calibration_report_is_deterministic(self) -> None:
        expected = deterministic_json_bytes(build_calibration_report())
        actual = (PROJECT_ROOT / "reports" / "p1-verifier-calibration.json").read_bytes()
        self.assertEqual(expected, actual)

    def test_fixture_approve_shape_cannot_make_content_learner_ready(self) -> None:
        bundle = load_fixture_bundle()
        readiness = derive_learner_ready(bundle, run_checks(bundle))
        self.assertFalse(readiness.learner_ready)
        self.assertIn("schema_fixture_not_eligible", readiness.reasons)
        self.assertIn("reference_not_admitted", readiness.reasons)
        self.assertIn("verification_event_incomplete", readiness.reasons)
        self.assertIn("required_reviewer_missing", readiness.reasons)

    def test_unreviewed_candidate_state_passes_integrity_but_not_readiness(self) -> None:
        bundle = load_fixture_bundle()
        bundle.review = None
        results = run_checks(bundle)
        approval_check = next(result for result in results if result.check_id == "APPROVAL_INTEGRITY")
        self.assertTrue(approval_check.passed)
        readiness = derive_learner_ready(bundle, results)
        self.assertFalse(readiness.learner_ready)
        self.assertIn("latest_decisive_review_not_approve", readiness.reasons)
        self.assertIn("approval_not_human", readiness.reasons)
        self.assertIn("required_reviewer_missing", readiness.reasons)


if __name__ == "__main__":
    unittest.main()
