from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from build_review_surface_data import (  # noqa: E402
    build_review_data,
    deterministic_json_bytes,
)
from ingest_review_event import ingest_review_event, locate_question_version  # noqa: E402
from validate_p1_records import load_json  # noqa: E402


class ReviewSurfaceIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture_dir = PROJECT_ROOT / "fixtures" / "questions"
        cls.question = load_json(cls.fixture_dir / "valid-question-version.json")
        cls.review_schema = load_json(PROJECT_ROOT / "schema" / "review-event.schema.json")
        cls.sample_question = load_json(
            PROJECT_ROOT / "data" / "questions" / "far-q-000101" / "versions" / "far-q-000101.v001.json"
        )
        cls.test_event_dir = PROJECT_ROOT / "review-surface" / ".test-events"
        cls.test_event_dir.mkdir(exist_ok=True)

    def tearDown(self) -> None:
        for event_id in ("far-review-exclusive-test", "far-review-stale-binding-test"):
            (self.test_event_dir / f"{event_id}.json").unlink(missing_ok=True)

    def test_checked_in_review_data_is_deterministic_and_exact_bound(self) -> None:
        data = build_review_data()
        checked_in = (PROJECT_ROOT / "review-surface" / "app" / "review-data-v002.json").read_bytes()
        self.assertEqual(deterministic_json_bytes(data), checked_in)
        self.assertEqual(6, data["queue_summary"]["item_count"])
        self.assertEqual(
            sum(item["derived_readiness"]["learner_ready"] for item in data["items"]),
            data["queue_summary"]["ready_count"],
        )
        self.assertEqual(0, data["queue_summary"]["coverage_contribution"])
        self.assertEqual(
            ["far-q-000101.v001", *[f"far-q-00010{number}.v002" for number in range(2, 7)]],
            [item["identity"]["version_id"] for item in data["items"]],
        )
        for item in data["items"]:
            self.assertEqual(0, item["derived_readiness"]["coverage_contribution"])
            self.assertEqual(8, len(item["verification"]["checks"]))
            if item["derived_readiness"]["learner_ready"]:
                self.assertTrue(any(event["action"] == "approve" for event in item["review_history"]))
        keyed = [item["question"]["solution"]["keyed_answer_option_id"] for item in data["items"]]
        self.assertEqual(["A", "B", "C", "D", "B", "C"], keyed)
        self.assertEqual(
            {"approve", "reject", "revise", "comment"},
            set(data["review_actions"]["allowed"]),
        )

    def test_fixture_event_is_refused_by_canonical_ingest(self) -> None:
        event = self._event("far-review-fixture-refusal")
        with self.assertRaisesRegex(ValueError, "schema fixtures cannot create canonical"):
            ingest_review_event(
                event,
                self.question,
                self.test_event_dir,
                self.review_schema,
            )

    def test_event_ingest_is_exact_bound_and_exclusive(self) -> None:
        event = self._event("far-review-exclusive-test")
        target = ingest_review_event(
            event,
            self.question,
            self.test_event_dir,
            self.review_schema,
            allow_fixture=True,
        )
        self.assertEqual(event, load_json(target))
        with self.assertRaises(FileExistsError):
            ingest_review_event(
                event,
                self.question,
                self.test_event_dir,
                self.review_schema,
                allow_fixture=True,
            )

    def test_sample_event_locator_and_ingest_use_canonical_versions_path(self) -> None:
        event = self._event("far-review-exclusive-test")
        event["subject"] = {
            "question_id": self.sample_question["question_id"],
            "version_id": self.sample_question["version_id"],
            "content_sha256": self.sample_question["content_sha256"],
        }
        located = locate_question_version(event, PROJECT_ROOT)
        self.assertEqual(
            PROJECT_ROOT / "data" / "questions" / "far-q-000101" / "versions" / "far-q-000101.v001.json",
            located,
        )
        target = ingest_review_event(event, self.sample_question, self.test_event_dir, self.review_schema)
        self.assertEqual(event, load_json(target))

        stale = copy.deepcopy(event)
        stale["event_id"] = "far-review-stale-binding-test"
        stale["subject"]["content_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "immutable question version"):
            ingest_review_event(
                stale,
                self.sample_question,
                self.test_event_dir,
                self.review_schema,
            )

    def _event(self, event_id: str) -> dict:
        return {
            "schema_version": "1.0.0",
            "event_id": event_id,
            "recorded_at": "2026-08-13T19:00:00Z",
            "action": "comment",
            "actor": {
                "actor_type": "human",
                "actor_id": "james",
                "display_name": "James",
            },
            "subject": {
                "question_id": self.question["question_id"],
                "version_id": self.question["version_id"],
                "content_sha256": self.question["content_sha256"],
            },
            "comment": "Purpose-built append-only event writer test.",
        }


if __name__ == "__main__":
    unittest.main()
