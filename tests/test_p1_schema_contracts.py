from __future__ import annotations

import copy
import json
import sqlite3
import sys
import unittest
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from validate_p1_records import (  # noqa: E402
    load_json,
    schema_issues,
    validate_checked_in_fixture_bundle,
    validate_question_contract,
)


def apply_mutation(document: Any, mutation: dict[str, Any]) -> None:
    parts = [part.replace("~1", "/").replace("~0", "~") for part in mutation["path"].split("/")[1:]]
    parent = document
    for part in parts[:-1]:
        parent = parent[int(part)] if isinstance(parent, list) else parent[part]
    key = parts[-1]
    if mutation["operation"] == "remove":
        if isinstance(parent, list):
            parent.pop(int(key))
        else:
            del parent[key]
    elif mutation["operation"] in {"add", "replace"}:
        if isinstance(parent, list):
            parent[int(key)] = mutation["value"]
        else:
            parent[key] = mutation["value"]
    else:
        raise AssertionError(f"unsupported mutation operation {mutation['operation']}")


class P1SchemaContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.schema_dir = PROJECT_ROOT / "schema"
        cls.fixture_dir = PROJECT_ROOT / "fixtures" / "questions"
        cls.question_schema = load_json(cls.schema_dir / "question-version.schema.json")
        cls.question = load_json(cls.fixture_dir / "valid-question-version.json")
        cls.rule = load_json(cls.fixture_dir / "valid-rule-version.json")
        cls.taxonomy = load_json(PROJECT_ROOT / "data" / "far-taxonomy.json")

    def test_all_p1_schemas_are_valid_draft_2020_12(self) -> None:
        for path in sorted(self.schema_dir.glob("*.schema.json")):
            with self.subTest(path=path.name):
                Draft202012Validator.check_schema(load_json(path))

    def test_complete_representative_fixture_bundle_passes(self) -> None:
        self.assertEqual([], validate_checked_in_fixture_bundle())

    def test_every_declared_corruption_is_rejected_by_expected_contract(self) -> None:
        rules = {self.rule["rule_version_id"]: self.rule}
        corruption_dir = self.fixture_dir / "corruptions"
        for path in sorted(corruption_dir.glob("*.json")):
            definition = load_json(path)
            corrupt = copy.deepcopy(self.question)
            for mutation in definition["mutations"]:
                apply_mutation(corrupt, mutation)
            issues = validate_question_contract(corrupt, self.question_schema, self.taxonomy, rules)
            observed = {issue.contract_id for issue in issues}
            with self.subTest(fixture=definition["fixture_id"]):
                self.assertIn(definition["expected_contract"], observed, [issue.detail for issue in issues])

    def test_approve_is_an_exact_version_human_event(self) -> None:
        schema = load_json(self.schema_dir / "review-event.schema.json")
        event = load_json(self.fixture_dir / "valid-review-event-approve.json")
        self.assertEqual([], schema_issues(schema, event, "REVIEW_SCHEMA"))

        corrupt = copy.deepcopy(event)
        corrupt["actor"]["actor_type"] = "system"
        self.assertTrue(schema_issues(schema, corrupt, "REVIEW_SCHEMA"))

        corrupt = copy.deepcopy(event)
        del corrupt["subject"]["content_sha256"]
        self.assertTrue(schema_issues(schema, corrupt, "REVIEW_SCHEMA"))

    def test_question_records_cannot_store_mutable_status(self) -> None:
        corrupt = copy.deepcopy(self.question)
        corrupt["human_approved"] = True
        issues = validate_question_contract(
            corrupt,
            self.question_schema,
            self.taxonomy,
            {self.rule["rule_version_id"]: self.rule},
        )
        self.assertIn("QUESTION_SCHEMA", {issue.contract_id for issue in issues})

    def test_projection_ddl_has_derived_review_state_and_immutable_events(self) -> None:
        ddl = (self.schema_dir / "review-projection.sql").read_text(encoding="utf-8")
        connection = sqlite3.connect(":memory:")
        self.addCleanup(connection.close)
        connection.executescript(ddl)

        tables = {
            row[0]
            for row in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
        }
        self.assertIn("question_version", tables)
        self.assertIn("review_event", tables)
        self.assertNotIn("approval", tables)
        for table in tables:
            columns = {row[1] for row in connection.execute(f"PRAGMA table_info({table})")}
            self.assertNotIn("learner_ready", columns)
            self.assertNotIn("human_approved", columns)

        views = {
            row[0]
            for row in connection.execute("SELECT name FROM sqlite_master WHERE type = 'view'")
        }
        self.assertIn("exact_version_review_state", views)

        connection.execute(
            "INSERT INTO question_identity VALUES (?, ?, ?)",
            ("far-q-000001", "2026-08-13T18:00:00Z", "{}"),
        )
        connection.execute(
            "INSERT INTO question_version VALUES (?, ?, ?, ?, ?)",
            ("far-q-000001.v001", "far-q-000001", 1, "0" * 64, "{}"),
        )
        with self.assertRaises(sqlite3.IntegrityError):
            connection.execute(
                "UPDATE question_version SET content_json = ? WHERE version_id = ?",
                ('{"mutated":true}', "far-q-000001.v001"),
            )


if __name__ == "__main__":
    unittest.main()
