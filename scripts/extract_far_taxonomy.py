#!/usr/bin/env python3
"""Extract the complete FAR hierarchy from the preserved official PDF."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from source_probe import probe_far_tables


def locator(node: dict[str, Any], location_type: str, anchor: str, row: int | None = None) -> dict[str, Any]:
    value = {
        "physical_page": node["physical_page"],
        "printed_page_label": node["printed_page_label"],
        "location_type": location_type,
        "anchor_text": anchor,
        "occurrence_on_page": 1,
    }
    if row is not None:
        value["row_ordinal_on_page"] = row
    return value


def build_taxonomy(inventory: dict[str, Any]) -> dict[str, Any]:
    area_number = {area["code"]: index for index, area in enumerate(inventory["areas"], 1)}
    result: dict[str, Any] = {
        "schema_version": "1.0.0",
        "taxonomy_id": "far-2026-01",
        "source_id": "aicpa-cpa-exam-blueprints-2026",
        "source_manifest": "sources/aicpa/2026-01/source-manifest.json",
        "exam_section": {"code": "FAR", "official_title": "Financial Accounting and Reporting"},
        "areas": [],
    }

    for area_source in inventory["areas"]:
        area_id = f"far.area.{area_number[area_source['code']]}"
        area = {
            "id": area_id,
            "code": area_source["code"],
            "official_title": area_source["official_title"],
            "official_heading": area_source["official_heading"],
            "allocation_percent": area_source["allocation_percent"],
            "source_locator": locator(area_source, "section_heading", area_source["official_heading"]),
            "groups": [],
        }
        for group_source in [group for group in inventory["groups"] if group["area_code"] == area_source["code"]]:
            group_id = f"{area_id}.group.{group_source['code'].lower()}"
            group = {
                "id": group_id,
                "code": group_source["code"],
                "official_title": group_source["official_title"],
                "official_heading": group_source["official_heading"],
                "source_locator": locator(group_source, "table_heading", group_source["official_heading"]),
                "topics": [],
                "tasks": [],
            }
            for topic_source in [
                topic
                for topic in inventory["topics"]
                if topic["area_code"] == area_source["code"] and topic["group_code"] == group_source["code"]
            ]:
                topic_id = f"{group_id}.topic.{topic_source['code']}"
                topic = {
                    "id": topic_id,
                    "code": topic_source["code"],
                    "official_title": topic_source["official_title"],
                    "official_heading": topic_source["official_heading"],
                    "source_locator": locator(topic_source, "table_heading", topic_source["official_heading"]),
                    "tasks": [],
                }
                source_tasks = [
                    task
                    for task in inventory["tasks"]
                    if task["area_code"] == area_source["code"]
                    and task["group_code"] == group_source["code"]
                    and task["topic_code"] == topic_source["code"]
                ]
                topic["tasks"] = build_tasks(source_tasks, topic_id)
                group["topics"].append(topic)

            direct_tasks = [
                task
                for task in inventory["tasks"]
                if task["area_code"] == area_source["code"]
                and task["group_code"] == group_source["code"]
                and task["topic_code"] is None
            ]
            group["tasks"] = build_tasks(direct_tasks, group_id)
            area["groups"].append(group)
        result["areas"].append(area)
    return result


def build_tasks(source_tasks: list[dict[str, Any]], parent_id: str) -> list[dict[str, Any]]:
    tasks = []
    for ordinal, source in enumerate(source_tasks, 1):
        tasks.append(
            {
                "id": f"{parent_id}.task.{ordinal:03d}",
                "ordinal_within_parent": ordinal,
                "official_text": source["official_text"],
                "skill_level": source["skill_level"],
                "source_locator": locator(
                    source,
                    "table_row",
                    source["official_text"],
                    source["row_ordinal_on_page"],
                ),
            }
        )
    return tasks


def main() -> int:
    project_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--pdf",
        type=Path,
        default=project_root / "sources" / "aicpa" / "2026-01" / "CPA_Exam_Blueprints_2026.pdf",
    )
    parser.add_argument("--output", type=Path, default=project_root / "data" / "far-taxonomy.json")
    args = parser.parse_args()

    inventory = probe_far_tables(args.pdf)
    taxonomy = build_taxonomy(inventory)
    schema = json.loads((project_root / "schema" / "far-taxonomy.schema.json").read_text(encoding="utf-8"))
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(taxonomy),
        key=lambda error: list(error.path),
    )
    if errors:
        for error in errors:
            print(f"{'/'.join(map(str, error.path))}: {error.message}")
        return 1
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(taxonomy, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    counts = {kind: len(inventory[kind]) for kind in ("areas", "groups", "topics", "tasks")}
    print(f"wrote {args.output}: {counts}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
