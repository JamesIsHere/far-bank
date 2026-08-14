from __future__ import annotations

import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from build_g3_package import build_package, package_bytes  # noqa: E402


class G3PackageTests(unittest.TestCase):
    def test_package_is_hands_on_ready_but_not_approved(self) -> None:
        package = build_package()
        self.assertEqual("ready_for_human_gate_not_approved", package["package_status"])
        self.assertEqual("not_issued", package["verdict"]["decision_state"])
        self.assertFalse(package["verdict"]["automation_authority"])
        self.assertEqual(
            ["approve", "reject", "revise", "comment"],
            [item["action"] for item in package["workflow"]["actions"]],
        )
        self.assertTrue(all(item["ingested_exclusively"] for item in package["workflow"]["actions"]))
        self.assertTrue(package["projection"]["equivalent_to_cold_reconstruction"])
        self.assertFalse(package["revision_boundary"]["prior_approval_carried_forward"])
        self.assertEqual(0, package["sample"]["production_coverage_contribution"])
        self.assertEqual(6, package["sample"]["item_count"])

    def test_checked_in_receipt_and_surface_input_are_deterministic(self) -> None:
        expected = package_bytes(build_package())
        self.assertEqual(expected, (PROJECT_ROOT / "reports" / "g3-package-manifest.json").read_bytes())
        self.assertEqual(expected, (PROJECT_ROOT / "review-surface" / "app" / "g3-workflow-package.json").read_bytes())


if __name__ == "__main__":
    unittest.main()
