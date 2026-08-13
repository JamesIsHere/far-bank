from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from verify_taxonomy import (  # noqa: E402
    check_source_effective,
    check_source_file,
    check_source_hash,
    check_source_pdf_identity,
    check_source_schema,
    check_taxonomy_completeness,
    check_taxonomy_ids,
    check_taxonomy_locators,
    check_taxonomy_parentage_order,
    check_taxonomy_render,
    check_taxonomy_schema,
    check_taxonomy_source_binding,
    check_taxonomy_task_source,
)


class VerifierRedCalibration(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source_dir = PROJECT_ROOT / "sources" / "aicpa" / "2026-01"
        cls.manifest = json.loads((cls.source_dir / "source-manifest.json").read_text(encoding="utf-8"))
        cls.source_schema = json.loads((PROJECT_ROOT / "schema" / "source-manifest.schema.json").read_text(encoding="utf-8"))
        cls.taxonomy_schema = json.loads((PROJECT_ROOT / "schema" / "far-taxonomy.schema.json").read_text(encoding="utf-8"))
        cls.valid = json.loads((PROJECT_ROOT / "fixtures" / "taxonomy" / "valid-minimal.json").read_text(encoding="utf-8"))
        cls.production = json.loads((PROJECT_ROOT / "data" / "far-taxonomy.json").read_text(encoding="utf-8"))
        cls.discrepancies = json.loads((PROJECT_ROOT / "data" / "discrepancies.json").read_text(encoding="utf-8"))

    def assert_rejected(self, result, check_id: str) -> None:
        self.assertEqual(result.check_id, check_id)
        self.assertFalse(result.passed, result.detail)

    def test_clean_fixture_passes_every_non_completeness_check(self) -> None:
        source_results = [
            check_source_schema(self.source_schema, self.manifest),
            check_source_file(self.source_dir, self.manifest),
            check_source_hash(self.source_dir, self.manifest),
            check_source_pdf_identity(self.source_dir, self.manifest),
            check_source_effective(self.source_dir, self.manifest),
        ]
        taxonomy_results = [
            check_taxonomy_schema(self.taxonomy_schema, self.valid),
            check_taxonomy_source_binding(self.valid, self.manifest, "sources/aicpa/2026-01/source-manifest.json"),
            check_taxonomy_ids(self.valid),
            check_taxonomy_parentage_order(self.valid),
            check_taxonomy_locators(self.source_dir, self.manifest, self.valid),
            check_taxonomy_task_source(self.source_dir, self.manifest, self.valid),
        ]
        failures = [result for result in source_results + taxonomy_results if not result.passed]
        self.assertEqual([], failures)

    def test_source_schema_rejects_missing_authority(self) -> None:
        corrupt = copy.deepcopy(self.manifest)
        del corrupt["authority"]
        self.assert_rejected(check_source_schema(self.source_schema, corrupt), "SOURCE_SCHEMA")

    def test_source_file_rejects_wrong_recorded_size(self) -> None:
        corrupt = copy.deepcopy(self.manifest)
        corrupt["retrieval"]["size_bytes"] += 1
        self.assert_rejected(check_source_file(self.source_dir, corrupt), "SOURCE_FILE")

    def test_source_hash_rejects_wrong_digest(self) -> None:
        corrupt = copy.deepcopy(self.manifest)
        corrupt["retrieval"]["sha256"] = "0" * 64
        self.assert_rejected(check_source_hash(self.source_dir, corrupt), "SOURCE_HASH")

    def test_source_pdf_identity_rejects_wrong_page_count(self) -> None:
        corrupt = copy.deepcopy(self.manifest)
        corrupt["retrieval"]["page_count"] += 1
        self.assert_rejected(check_source_pdf_identity(self.source_dir, corrupt), "SOURCE_PDF_IDENTITY")

    def test_source_effective_rejects_wrong_contract_date(self) -> None:
        corrupt = copy.deepcopy(self.manifest)
        corrupt["publication"]["effective_from"] = "2025-01-01"
        self.assert_rejected(check_source_effective(self.source_dir, corrupt), "SOURCE_EFFECTIVE")

    def test_taxonomy_schema_rejects_invalid_far_skill(self) -> None:
        corrupt = copy.deepcopy(self.valid)
        corrupt["areas"][0]["groups"][0]["topics"][0]["tasks"][0]["skill_level"] = "evaluation"
        self.assert_rejected(check_taxonomy_schema(self.taxonomy_schema, corrupt), "TAXONOMY_SCHEMA")

    def test_taxonomy_source_binding_rejects_other_source(self) -> None:
        corrupt = copy.deepcopy(self.valid)
        corrupt["source_id"] = "other-official-source"
        self.assert_rejected(
            check_taxonomy_source_binding(corrupt, self.manifest, "sources/aicpa/2026-01/source-manifest.json"),
            "TAXONOMY_SOURCE_BINDING",
        )

    def test_taxonomy_ids_reject_duplicate(self) -> None:
        corrupt = copy.deepcopy(self.valid)
        tasks = corrupt["areas"][0]["groups"][0]["topics"][0]["tasks"]
        tasks[1]["id"] = tasks[0]["id"]
        self.assert_rejected(check_taxonomy_ids(corrupt), "TAXONOMY_IDS")

    def test_taxonomy_parentage_rejects_orphaned_task_id(self) -> None:
        corrupt = copy.deepcopy(self.valid)
        corrupt["areas"][0]["groups"][0]["topics"][0]["tasks"][1]["id"] = "far.area.1.group.a.topic.1.task.003"
        self.assert_rejected(check_taxonomy_parentage_order(corrupt), "TAXONOMY_PARENTAGE_ORDER")

    def test_taxonomy_locators_reject_unfindable_official_heading(self) -> None:
        corrupt = copy.deepcopy(self.valid)
        topic = corrupt["areas"][0]["groups"][0]["topics"][0]
        topic["official_title"] = "Invented heading"
        topic["official_heading"] = "1. Invented heading"
        topic["source_locator"]["anchor_text"] = "1. Invented heading"
        self.assert_rejected(check_taxonomy_locators(self.source_dir, self.manifest, corrupt), "TAXONOMY_LOCATORS")

    def test_taxonomy_task_source_rejects_wrong_drawn_skill(self) -> None:
        corrupt = copy.deepcopy(self.valid)
        corrupt["areas"][0]["groups"][0]["topics"][0]["tasks"][0]["skill_level"] = "analysis"
        self.assert_rejected(check_taxonomy_task_source(self.source_dir, self.manifest, corrupt), "TAXONOMY_TASK_SOURCE")

    def test_taxonomy_completeness_rejects_truncated_fixture(self) -> None:
        self.assert_rejected(
            check_taxonomy_completeness(self.source_dir, self.manifest, self.valid),
            "TAXONOMY_COMPLETENESS",
        )

    def test_taxonomy_render_passes_checked_in_artifact(self) -> None:
        result = check_taxonomy_render(
            PROJECT_ROOT / "reports" / "far-taxonomy-g1.html",
            self.production,
            self.manifest,
            self.discrepancies,
        )
        self.assertTrue(result.passed, result.detail)

    def test_taxonomy_render_rejects_mutated_artifact(self) -> None:
        path = PROJECT_ROOT / "fixtures" / "render" / "corrupt-taxonomy.html"
        self.assert_rejected(
            check_taxonomy_render(path, self.production, self.manifest, self.discrepancies),
            "TAXONOMY_RENDER",
        )


if __name__ == "__main__":
    unittest.main()
