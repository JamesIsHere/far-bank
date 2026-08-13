from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from validate_p1_records import PROJECT_ROOT, load_json


OUTPUT_PATH = PROJECT_ROOT / "reports" / "g2-package-manifest.json"
REVIEW_DATA_PATH = PROJECT_ROOT / "review-surface" / "app" / "review-data.json"
SAMPLE_REPORT_PATH = PROJECT_ROOT / "reports" / "p1-sample-verification.json"
PROPOSAL_PATH = PROJECT_ROOT / "docs" / "gates" / "g2-proposed-amendment.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_package(project_root: Path = PROJECT_ROOT) -> dict[str, Any]:
    package_path = project_root / "reports" / "g2-package-manifest.json"
    package = load_json(package_path)
    archived_paths = {
        "data/sample/p1/manifest.json": project_root / "data" / "sample" / "p1" / "manifest.v001.json",
        "reports/p1-sample-verification.json": project_root / "reports" / "p1-sample-verification.v001.json",
    }
    for artifact in package["artifacts"]:
        path = archived_paths.get(artifact["path"], project_root / artifact["path"])
        if sha256(path) != artifact["sha256"]:
            raise RuntimeError(f"opening-package artifact hash mismatch: {artifact['path']}")
    return package


def package_bytes(value: dict[str, Any]) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify and reproduce the immutable FAR Gate G2 opening-package receipt.")
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    args = parser.parse_args()
    package = build_package()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(package_bytes(package))
    print(
        f"PASS G2 package {package['package_id']} items={package['item_count']} "
        f"ready={package['learner_ready_count']} status={package['package_status']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
