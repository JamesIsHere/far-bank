from __future__ import annotations

import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from rebuild_review_projection import build_projection, deterministic_json_bytes as projection_bytes  # noqa: E402
from verify_review_workflow import build_workflow_report, deterministic_json_bytes as workflow_bytes  # noqa: E402


class ProjectionAndWorkflow(unittest.TestCase):
    def test_cold_rebuild_matches_sqlite_and_checked_in_receipt(self) -> None:
        with tempfile.TemporaryDirectory(prefix=".test-projection-", dir=PROJECT_ROOT / "review-surface") as temporary:
            report = build_projection(Path(temporary) / "review.sqlite")
        checked_in = (PROJECT_ROOT / "reports/p2-projection-reconstruction.json").read_bytes()
        self.assertEqual(projection_bytes(report), checked_in)
        self.assertTrue(report["projection_equivalent_to_cold_reconstruction"])
        self.assertEqual(6, report["state_summary"]["question_identity_count"])
        self.assertEqual(11, report["state_summary"]["question_version_count"])
        self.assertEqual(6, report["state_summary"]["learner_ready_count"])
        self.assertEqual(0, report["state_summary"]["coverage_contribution_count"])

    def test_projection_replays_supersession_comment_and_exact_approval(self) -> None:
        with tempfile.TemporaryDirectory(prefix=".test-projection-state-", dir=PROJECT_ROOT / "review-surface") as temporary:
            database = Path(temporary) / "review.sqlite"
            build_projection(database)
            connection = sqlite3.connect(database)
            try:
                q102 = connection.execute(
                    "SELECT version_id, is_latest_version, latest_decisive_action, learner_ready FROM learner_ready_projection WHERE question_id='far-q-000102' ORDER BY version_number"
                ).fetchall()
                q105_v1 = connection.execute(
                    "SELECT latest_decisive_action, learner_ready FROM learner_ready_projection WHERE version_id='far-q-000105.v001'"
                ).fetchone()
            finally:
                connection.close()
        self.assertEqual(
            [("far-q-000102.v001", 0, "auto_invalidate", 0), ("far-q-000102.v002", 1, "approve", 1)],
            q102,
        )
        self.assertEqual((None, 0), q105_v1)

    def test_projected_versions_and_events_are_immutable(self) -> None:
        with tempfile.TemporaryDirectory(prefix=".test-projection-immutable-", dir=PROJECT_ROOT / "review-surface") as temporary:
            database = Path(temporary) / "review.sqlite"
            build_projection(database)
            connection = sqlite3.connect(database)
            with self.assertRaisesRegex(sqlite3.IntegrityError, "immutable projection inputs"):
                connection.execute("UPDATE question_version SET content_json='{}' WHERE version_id='far-q-000101.v001'")
            with self.assertRaisesRegex(sqlite3.IntegrityError, "append-only projection inputs"):
                connection.execute("UPDATE review_event SET comment='mutated' WHERE event_id='far-review-far-q-000101-approve-20260813t1743203278866z'")
            with self.assertRaisesRegex(sqlite3.IntegrityError, "append-only projection inputs"):
                connection.execute("DELETE FROM verification_event WHERE event_id='far-verification-000101-v001'")
            with self.assertRaisesRegex(sqlite3.IntegrityError, "append-only projection inputs"):
                connection.execute("UPDATE verification_check SET outcome='fail' WHERE event_id='far-verification-000101-v001'")
            connection.close()

    def test_all_actions_revision_and_integrity_rejections_are_exercised(self) -> None:
        report = build_workflow_report()
        checked_in = (PROJECT_ROOT / "reports/p2-review-workflow-verification.json").read_bytes()
        self.assertEqual(workflow_bytes(report), checked_in)
        self.assertEqual(["approve", "reject", "revise", "comment"], [item["action"] for item in report["actions"]])
        self.assertTrue(all(item["ingested_exclusively"] for item in report["actions"]))
        self.assertTrue(report["exclusive_create_duplicate_rejected"])
        self.assertTrue(report["stale_exact_version_binding_rejected"])
        self.assertNotEqual(report["revision"]["prior_content_sha256"], report["revision"]["new_content_sha256"])
        self.assertFalse(report["canonical_revision_example"]["prior_approval_carried_forward"])
        self.assertTrue(report["projection_equivalent_to_cold_reconstruction"])


if __name__ == "__main__":
    unittest.main()
