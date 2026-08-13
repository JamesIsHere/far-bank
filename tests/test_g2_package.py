from __future__ import annotations

import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from build_g2_package import build_package, package_bytes  # noqa: E402


class G2PackageTests(unittest.TestCase):
    def test_package_is_gate_ready_but_unratified(self) -> None:
        package = build_package()
        self.assertEqual("ready_for_human_gate_not_ratified", package["package_status"])
        self.assertEqual(6, package["item_count"])
        self.assertEqual(0, package["learner_ready_count"])
        self.assertEqual(0, package["coverage_contribution"])
        self.assertEqual(0, package["canonical_review_event_count"])
        self.assertIn("dated goal.md amendment ratification", package["gate_sequence"])

    def test_checked_in_package_manifest_is_deterministic(self) -> None:
        expected = package_bytes(build_package())
        actual = (PROJECT_ROOT / "reports" / "g2-package-manifest.json").read_bytes()
        self.assertEqual(expected, actual)


if __name__ == "__main__":
    unittest.main()
