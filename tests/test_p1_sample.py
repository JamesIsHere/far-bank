from __future__ import annotations

import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from verify_p1_sample import build_report, report_bytes  # noqa: E402


class P1SampleTests(unittest.TestCase):
    def test_sample_spans_areas_skills_and_reports_current_review_state(self) -> None:
        report = build_report()
        summary = report["summary"]
        self.assertEqual("pass", summary["outcome"])
        self.assertEqual(6, summary["item_count"])
        self.assertEqual(["far.area.1", "far.area.2", "far.area.3"], summary["area_ids"])
        self.assertEqual(["analysis", "application", "remembering_and_understanding"], summary["skill_levels"])
        self.assertTrue(summary["all_checks_pass"])
        self.assertFalse(summary["all_items_candidate_only"])
        self.assertEqual(
            sum(item["learner_ready"] for item in report["items"]),
            summary["learner_ready_count"],
        )
        self.assertEqual(6 - summary["learner_ready_count"], summary["pending_review_count"])
        self.assertEqual(
            len(list((PROJECT_ROOT / "data" / "events" / "review").glob("*.json"))),
            summary["canonical_review_event_count"],
        )
        self.assertGreaterEqual(summary["exact_current_version_review_event_count"], 1)

    def test_every_item_has_eight_passing_checks_and_only_current_approval_is_ready(self) -> None:
        for item in build_report()["items"]:
            with self.subTest(question_id=item["question_id"]):
                self.assertEqual(8, len(item["checks"]))
                self.assertTrue(all(check["outcome"] == "pass" for check in item["checks"]))
                if item["learner_ready"]:
                    self.assertEqual([], item["readiness_hold_reasons"])
                else:
                    self.assertIn("required_reviewer_missing", item["readiness_hold_reasons"])

    def test_checked_in_report_is_deterministic(self) -> None:
        expected = report_bytes(build_report())
        actual = (PROJECT_ROOT / "reports" / "p1-sample-verification.v002.json").read_bytes()
        self.assertEqual(expected, actual)


if __name__ == "__main__":
    unittest.main()
