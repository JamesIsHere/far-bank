#!/usr/bin/env python3
"""Verify the preserved official source and a FAR taxonomy against it."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

import pymupdf
from jsonschema import Draft202012Validator, FormatChecker

from render_taxonomy import render_taxonomy_html


@dataclass(frozen=True)
class CheckResult:
    check_id: str
    passed: bool
    detail: str


def _result(check_id: str, passed: bool, detail: str) -> CheckResult:
    return CheckResult(check_id, passed, detail)


def clean_text(value: str) -> str:
    value = "".join(" " if unicodedata.category(ch).startswith("C") else ch for ch in value)
    value = re.sub(r"\s+", " ", value).strip()
    value = re.sub(r"\b([A-Z]) ([a-z]{2,})\b", r"\1\2", value)
    return value


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _schema_errors(schema: dict[str, Any], data: dict[str, Any]) -> list[str]:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(data), key=lambda error: list(error.path))
    return [f"{'/'.join(map(str, error.path)) or '<root>'}: {error.message}" for error in errors]


def check_source_schema(schema: dict[str, Any], manifest: dict[str, Any]) -> CheckResult:
    errors = _schema_errors(schema, manifest)
    return _result("SOURCE_SCHEMA", not errors, "valid" if not errors else errors[0])


def _source_file(source_dir: Path, manifest: dict[str, Any]) -> Path:
    return source_dir / str(manifest.get("retrieval", {}).get("local_file", ""))


def check_source_file(source_dir: Path, manifest: dict[str, Any]) -> CheckResult:
    path = _source_file(source_dir, manifest)
    if not path.is_file():
        return _result("SOURCE_FILE", False, f"missing: {path}")
    expected = manifest.get("retrieval", {}).get("size_bytes")
    actual = path.stat().st_size
    return _result("SOURCE_FILE", actual == expected, f"size expected={expected} actual={actual}")


def check_source_hash(source_dir: Path, manifest: dict[str, Any]) -> CheckResult:
    path = _source_file(source_dir, manifest)
    if not path.is_file():
        return _result("SOURCE_HASH", False, "source file missing")
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    expected = manifest.get("retrieval", {}).get("sha256")
    return _result("SOURCE_HASH", actual == expected, f"sha256 expected={expected} actual={actual}")


def check_source_pdf_identity(source_dir: Path, manifest: dict[str, Any]) -> CheckResult:
    path = _source_file(source_dir, manifest)
    if not path.is_file():
        return _result("SOURCE_PDF_IDENTITY", False, "source file missing")
    try:
        if not path.read_bytes()[:8].startswith(b"%PDF-"):
            return _result("SOURCE_PDF_IDENTITY", False, "PDF header missing")
        with pymupdf.open(path) as document:
            expected_pages = manifest.get("retrieval", {}).get("page_count")
            encrypted = bool(document.needs_pass)
            passed = len(document) == expected_pages and encrypted == manifest.get("retrieval", {}).get("encrypted")
            return _result(
                "SOURCE_PDF_IDENTITY",
                passed,
                f"pages expected={expected_pages} actual={len(document)}; encrypted={encrypted}",
            )
    except Exception as exc:  # pragma: no cover - defensive reporting boundary
        return _result("SOURCE_PDF_IDENTITY", False, f"unreadable PDF: {exc}")


def check_source_effective(source_dir: Path, manifest: dict[str, Any]) -> CheckResult:
    path = _source_file(source_dir, manifest)
    if not path.is_file():
        return _result("SOURCE_EFFECTIVE", False, "source file missing")
    publication = manifest.get("publication", {})
    with pymupdf.open(path) as document:
        cover = clean_text(document[0].get_text("text", sort=True))
    expected_phrases = [
        str(publication.get("cover_title", "")),
        "Aug. 18, 2025",
        "Effective date: January 2026",
    ]
    passed = publication.get("effective_from") == "2026-01-01" and all(phrase in cover for phrase in expected_phrases)
    return _result("SOURCE_EFFECTIVE", passed, f"effective_from={publication.get('effective_from')}; cover phrases={expected_phrases}")


def _flatten_taxonomy(taxonomy: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    flat = {"areas": [], "groups": [], "topics": [], "tasks": []}
    for area in taxonomy.get("areas", []):
        flat["areas"].append(area)
        for group in area.get("groups", []):
            group_copy = dict(group)
            group_copy["_area"] = area
            flat["groups"].append(group_copy)
            for topic in group.get("topics", []):
                topic_copy = dict(topic)
                topic_copy["_area"] = area
                topic_copy["_group"] = group
                flat["topics"].append(topic_copy)
                for task in topic.get("tasks", []):
                    task_copy = dict(task)
                    task_copy["_area"] = area
                    task_copy["_group"] = group
                    task_copy["_topic"] = topic
                    flat["tasks"].append(task_copy)
            for task in group.get("tasks", []):
                task_copy = dict(task)
                task_copy["_area"] = area
                task_copy["_group"] = group
                task_copy["_topic"] = None
                flat["tasks"].append(task_copy)
    return flat


def check_taxonomy_schema(schema: dict[str, Any], taxonomy: dict[str, Any]) -> CheckResult:
    errors = _schema_errors(schema, taxonomy)
    return _result("TAXONOMY_SCHEMA", not errors, "valid" if not errors else errors[0])


def check_taxonomy_source_binding(taxonomy: dict[str, Any], manifest: dict[str, Any], manifest_relative: str) -> CheckResult:
    expected_id = manifest.get("source_id")
    passed = taxonomy.get("source_id") == expected_id and taxonomy.get("source_manifest") == manifest_relative
    return _result(
        "TAXONOMY_SOURCE_BINDING",
        passed,
        f"source_id={taxonomy.get('source_id')} expected={expected_id}; manifest={taxonomy.get('source_manifest')}",
    )


def check_taxonomy_ids(taxonomy: dict[str, Any]) -> CheckResult:
    flat = _flatten_taxonomy(taxonomy)
    ids = [node.get("id") for kind in flat.values() for node in kind]
    duplicates = sorted({node_id for node_id in ids if ids.count(node_id) > 1})
    missing = sum(node_id is None for node_id in ids)
    return _result("TAXONOMY_IDS", not duplicates and not missing, f"duplicates={duplicates}; missing={missing}")


def check_taxonomy_parentage_order(taxonomy: dict[str, Any]) -> CheckResult:
    problems: list[str] = []
    expected_roman = ["I", "II", "III"]
    for area_index, area in enumerate(taxonomy.get("areas", []), 1):
        area_id = f"far.area.{area_index}"
        if area.get("id") != area_id:
            problems.append(f"area id {area.get('id')} != {area_id}")
        if area_index <= len(expected_roman) and area.get("code") != expected_roman[area_index - 1]:
            problems.append(f"area code order at {area_index}")
        allocation = area.get("allocation_percent", {})
        if allocation.get("minimum", 101) > allocation.get("maximum", -1):
            problems.append(f"area allocation reversed: {area_id}")
        for group_index, group in enumerate(area.get("groups", []), 1):
            expected_code = chr(64 + group_index)
            group_id = f"{area_id}.group.{str(group.get('code', '')).lower()}"
            if group.get("id") != group_id:
                problems.append(f"group id {group.get('id')} != {group_id}")
            if group.get("code") != expected_code:
                problems.append(f"group code order under {area_id}: {group.get('code')} != {expected_code}")
            for topic_index, topic in enumerate(group.get("topics", []), 1):
                topic_id = f"{group_id}.topic.{topic_index}"
                if topic.get("id") != topic_id or topic.get("code") != str(topic_index):
                    problems.append(f"topic parent/order mismatch: {topic.get('id')}")
                _check_task_order(topic.get("tasks", []), topic_id, problems)
            _check_task_order(group.get("tasks", []), group_id, problems)
    return _result("TAXONOMY_PARENTAGE_ORDER", not problems, "valid" if not problems else problems[0])


def _check_task_order(tasks: list[dict[str, Any]], parent_id: str, problems: list[str]) -> None:
    for ordinal, task in enumerate(tasks, 1):
        expected_id = f"{parent_id}.task.{ordinal:03d}"
        if task.get("ordinal_within_parent") != ordinal or task.get("id") != expected_id:
            problems.append(f"task parent/order mismatch: {task.get('id')} expected={expected_id}")


def _pdf_page_text(document: Any, physical_page: int) -> str:
    return clean_text(document[physical_page - 1].get_text("text", sort=True))


def check_taxonomy_locators(source_dir: Path, manifest: dict[str, Any], taxonomy: dict[str, Any]) -> CheckResult:
    path = _source_file(source_dir, manifest)
    if not path.is_file():
        return _result("TAXONOMY_LOCATORS", False, "source file missing")
    scope = manifest.get("far_scope", {}).get("physical_pdf_pages", {})
    first, last = scope.get("first", 0), scope.get("last", 0)
    problems: list[str] = []
    flat = _flatten_taxonomy(taxonomy)
    nodes = flat["areas"] + flat["groups"] + flat["topics"] + flat["tasks"]
    with pymupdf.open(path) as document:
        page_cache: dict[tuple[int, str], str] = {}
        for node in nodes:
            locator = node.get("source_locator", {})
            page_number = locator.get("physical_page")
            if not isinstance(page_number, int) or not first <= page_number <= last:
                problems.append(f"{node.get('id')}: physical page outside FAR range")
                continue
            expected_printed = f"FAR{page_number - first + 1}"
            if locator.get("printed_page_label") != expected_printed:
                problems.append(f"{node.get('id')}: printed page mismatch")
            anchor = clean_text(str(locator.get("anchor_text", "")))
            official = clean_text(str(node.get("official_text", node.get("official_heading", ""))))
            if anchor != official:
                problems.append(f"{node.get('id')}: anchor differs from official text")
            node_id = str(node.get("id", ""))
            if ".topic." in node_id and ".task." not in node_id:
                region = "topic"
                clip = pymupdf.Rect(44, 150, 203, 551)
            elif ".task." in node_id:
                region = "task"
                clip = pymupdf.Rect(430, 150, 748, 551)
            else:
                region = "page"
                clip = None
            cache_key = (page_number, region)
            if cache_key not in page_cache:
                page = document[page_number - 1]
                page_cache[cache_key] = clean_text(page.get_text("text", clip=clip, sort=True))
            if anchor and anchor not in page_cache[cache_key]:
                problems.append(f"{node.get('id')}: anchor not found on page {page_number}")
    return _result("TAXONOMY_LOCATORS", not problems, "valid" if not problems else problems[0])


def _independent_pdf_inventory(pdf_path: Path, first_page: int, last_page: int) -> dict[str, list[dict[str, Any]]]:
    inventory: dict[str, list[dict[str, Any]]] = {"areas": [], "groups": [], "topics": [], "tasks": []}
    seen_areas: set[str] = set()
    seen_groups: set[tuple[str, str]] = set()
    seen_topics: set[tuple[str, str, str]] = set()
    active_area: str | None = None
    active_group: str | None = None
    active_topic: str | None = None

    with pymupdf.open(pdf_path) as document:
        for physical_page in range(first_page, last_page + 1):
            page = document[physical_page - 1]
            page_text = clean_text(page.get_text("text", sort=True))
            printed_match = re.search(r"\bFAR[1-9][0-9]*\b", page_text)
            printed = printed_match.group(0) if printed_match else ""
            area_match = re.search(r"Area (I|II|III) – ([^(]+?) \(([0-9]+)–([0-9]+)%\)", page_text)
            if area_match:
                active_area = area_match.group(1)
                if active_area not in seen_areas:
                    seen_areas.add(active_area)
                    inventory["areas"].append(
                        {
                            "code": active_area,
                            "official_title": clean_text(area_match.group(2)),
                            "minimum": int(area_match.group(3)),
                            "maximum": int(area_match.group(4)),
                        }
                    )

            drawings = page.get_drawings()
            group_rects = []
            for drawing in drawings:
                if drawing.get("fill") is None:
                    continue
                for item in drawing.get("items", []):
                    if item[0] != "re":
                        continue
                    rect = item[1]
                    if rect.width > 690 and 18 <= rect.height <= 26 and rect.y0 > 145:
                        group_rects.append(rect)
            group_rects.sort(key=lambda rect: rect.y0)
            group_events: list[dict[str, Any]] = []
            for rect in group_rects:
                heading = clean_text(page.get_text("text", clip=rect, sort=True))
                heading = re.sub(r"\s*\(continued\)\s*$", "", heading)
                match = re.match(r"^([A-Z]+)\.\s*(.+)$", heading)
                if match:
                    group_events.append({"top": rect.y0, "code": match.group(1), "official_title": match.group(2)})

            topic_events = _independent_topic_events(page, group_rects)
            checkmarks = sorted(
                [
                    drawing
                    for drawing in drawings
                    if 9 <= drawing["rect"].width <= 13
                    and 6 <= drawing["rect"].height <= 9
                    and 220 <= drawing["rect"].x0 <= 420
                    and len(drawing.get("items", [])) == 2
                ],
                key=lambda drawing: drawing["rect"].y0,
            )
            row_lines = sorted(
                {
                    round(drawing["rect"].y0, 3)
                    for drawing in drawings
                    if drawing["rect"].width > 300
                    and drawing["rect"].height < 0.2
                    and 420 <= drawing["rect"].x0 <= 440
                }
            )
            task_events = [
                {"top": drawing["rect"].y0, "drawing": drawing, "ordinal": ordinal}
                for ordinal, drawing in enumerate(checkmarks, 1)
            ]
            events = (
                [(event["top"], 0, "group", event) for event in group_events]
                + [(event["top"], 1, "topic", event) for event in topic_events]
                + [(event["top"], 2, "task", event) for event in task_events]
            )
            for _, _, event_type, event in sorted(events, key=lambda item: (item[0], item[1])):
                if event_type == "group":
                    active_group = event["code"]
                    active_topic = None
                    key = (active_area or "", active_group)
                    if key not in seen_groups:
                        seen_groups.add(key)
                        inventory["groups"].append(
                            {"area_code": active_area, "code": active_group, "official_title": event["official_title"]}
                        )
                elif event_type == "topic":
                    active_topic = event["code"]
                    key = (active_area or "", active_group or "", active_topic)
                    if key not in seen_topics:
                        seen_topics.add(key)
                        inventory["topics"].append(
                            {
                                "area_code": active_area,
                                "group_code": active_group,
                                "code": active_topic,
                                "official_title": event["official_title"],
                            }
                        )
                else:
                    rect = event["drawing"]["rect"]
                    center_y = (rect.y0 + rect.y1) / 2
                    previous = max((line for line in row_lines if line < center_y), default=center_y - 15)
                    following = min((line for line in row_lines if line > center_y), default=center_y + 25)
                    task_text = clean_text(page.get_text("text", clip=pymupdf.Rect(430, previous, 748, following), sort=True))
                    center_x = (rect.x0 + rect.x1) / 2
                    if center_x < 279:
                        skill = "remembering_and_understanding"
                    elif center_x < 329.4:
                        skill = "application"
                    elif center_x < 379.8:
                        skill = "analysis"
                    else:
                        skill = "evaluation"
                    inventory["tasks"].append(
                        {
                            "area_code": active_area,
                            "group_code": active_group,
                            "topic_code": active_topic,
                            "physical_page": physical_page,
                            "printed_page_label": printed,
                            "row_ordinal_on_page": event["ordinal"],
                            "official_text": task_text,
                            "skill_level": skill,
                        }
                    )
    return inventory


def _independent_topic_events(page: Any, group_rects: list[Any]) -> list[dict[str, Any]]:
    words = []
    for word in page.get_text("words", sort=True):
        x0, y0, x1, y1, text = word[:5]
        if not (44 <= x0 and x1 <= 203 and 150 <= y0 <= 551):
            continue
        center_y = (y0 + y1) / 2
        if any(rect.y0 - 1 <= center_y <= rect.y1 + 1 for rect in group_rects):
            continue
        words.append({"x0": x0, "top": y0, "text": text})

    lines: list[dict[str, Any]] = []
    for word in words:
        for line in lines:
            if abs(line["top"] - word["top"]) < 3:
                line["words"].append(word)
                break
        else:
            lines.append({"top": word["top"], "words": [word]})

    events: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for line in sorted(lines, key=lambda item: item["top"]):
        text = clean_text(" ".join(word["text"] for word in sorted(line["words"], key=lambda item: item["x0"])))
        match = re.match(r"^([1-9][0-9]*)\.\s*(.+)$", text)
        if match:
            if current:
                events.append(current)
            current = {"top": line["top"], "code": match.group(1), "parts": [match.group(2)]}
        elif current and text:
            current["parts"].append(text)
    if current:
        events.append(current)
    for event in events:
        title = clean_text(" ".join(event.pop("parts")))
        event["official_title"] = re.sub(r"\s*\(continued\)\s*$", "", title)
    return events


def check_taxonomy_task_source(source_dir: Path, manifest: dict[str, Any], taxonomy: dict[str, Any]) -> CheckResult:
    path = _source_file(source_dir, manifest)
    if not path.is_file():
        return _result("TAXONOMY_TASK_SOURCE", False, "source file missing")
    scope = manifest["far_scope"]["physical_pdf_pages"]
    inventory = _independent_pdf_inventory(path, scope["first"] + 6, scope["last"])
    source_rows = {(task["physical_page"], task["row_ordinal_on_page"]): task for task in inventory["tasks"]}
    problems: list[str] = []
    for task in _flatten_taxonomy(taxonomy)["tasks"]:
        locator = task.get("source_locator", {})
        key = (locator.get("physical_page"), locator.get("row_ordinal_on_page"))
        source = source_rows.get(key)
        if not source:
            problems.append(f"{task.get('id')}: source row not found: {key}")
            continue
        expected_structure = (
            task["_area"].get("code"),
            task["_group"].get("code"),
            task["_topic"].get("code") if task["_topic"] else None,
        )
        actual_structure = (source["area_code"], source["group_code"], source["topic_code"])
        if clean_text(task.get("official_text", "")) != source["official_text"]:
            problems.append(f"{task.get('id')}: official task text differs from source row")
        elif task.get("skill_level") != source["skill_level"]:
            problems.append(f"{task.get('id')}: skill {task.get('skill_level')} != {source['skill_level']}")
        elif expected_structure != actual_structure:
            problems.append(f"{task.get('id')}: source hierarchy {actual_structure} != {expected_structure}")
    return _result("TAXONOMY_TASK_SOURCE", not problems, "valid" if not problems else problems[0])


def check_taxonomy_completeness(source_dir: Path, manifest: dict[str, Any], taxonomy: dict[str, Any]) -> CheckResult:
    path = _source_file(source_dir, manifest)
    if not path.is_file():
        return _result("TAXONOMY_COMPLETENESS", False, "source file missing")
    scope = manifest["far_scope"]["physical_pdf_pages"]
    source = _independent_pdf_inventory(path, scope["first"] + 6, scope["last"])
    flat = _flatten_taxonomy(taxonomy)

    source_sets = {
        "areas": {(n["code"], n["official_title"], n["minimum"], n["maximum"]) for n in source["areas"]},
        "groups": {(n["area_code"], n["code"], n["official_title"]) for n in source["groups"]},
        "topics": {(n["area_code"], n["group_code"], n["code"], n["official_title"]) for n in source["topics"]},
        "tasks": {(n["physical_page"], n["row_ordinal_on_page"]) for n in source["tasks"]},
    }
    taxonomy_sets = {
        "areas": {
            (n.get("code"), n.get("official_title"), n.get("allocation_percent", {}).get("minimum"), n.get("allocation_percent", {}).get("maximum"))
            for n in flat["areas"]
        },
        "groups": {(n["_area"].get("code"), n.get("code"), n.get("official_title")) for n in flat["groups"]},
        "topics": {
            (n["_area"].get("code"), n["_group"].get("code"), n.get("code"), n.get("official_title"))
            for n in flat["topics"]
        },
        "tasks": {
            (n.get("source_locator", {}).get("physical_page"), n.get("source_locator", {}).get("row_ordinal_on_page"))
            for n in flat["tasks"]
        },
    }
    problems = []
    for kind in ("areas", "groups", "topics", "tasks"):
        missing = source_sets[kind] - taxonomy_sets[kind]
        extra = taxonomy_sets[kind] - source_sets[kind]
        if missing or extra:
            problems.append(f"{kind}: source={len(source_sets[kind])} taxonomy={len(taxonomy_sets[kind])} missing={len(missing)} extra={len(extra)}")
    return _result("TAXONOMY_COMPLETENESS", not problems, "counts 3/22/18/113" if not problems else problems[0])


def check_taxonomy_render(
    report_path: Path,
    taxonomy: dict[str, Any],
    manifest: dict[str, Any],
    discrepancies: dict[str, Any],
) -> CheckResult:
    first = render_taxonomy_html(taxonomy, manifest, discrepancies)
    second = render_taxonomy_html(taxonomy, manifest, discrepancies)
    if first != second:
        return _result("TAXONOMY_RENDER", False, "two cold in-memory renders differ")
    if not report_path.is_file():
        return _result("TAXONOMY_RENDER", False, f"rendered artifact missing: {report_path}")
    actual = report_path.read_text(encoding="utf-8")
    expected_hash = hashlib.sha256(first.encode("utf-8")).hexdigest()
    actual_hash = hashlib.sha256(actual.encode("utf-8")).hexdigest()
    return _result(
        "TAXONOMY_RENDER",
        actual == first,
        f"expected_sha256={expected_hash} actual_sha256={actual_hash}",
    )


def run_checks(project_root: Path, taxonomy_path: Path) -> list[CheckResult]:
    source_dir = project_root / "sources" / "aicpa" / "2026-01"
    manifest_path = source_dir / "source-manifest.json"
    manifest = _load_json(manifest_path)
    taxonomy = _load_json(taxonomy_path)
    source_schema = _load_json(project_root / "schema" / "source-manifest.schema.json")
    taxonomy_schema = _load_json(project_root / "schema" / "far-taxonomy.schema.json")
    discrepancies = _load_json(project_root / "data" / "discrepancies.json")
    manifest_relative = manifest_path.relative_to(project_root).as_posix()
    return [
        check_source_schema(source_schema, manifest),
        check_source_file(source_dir, manifest),
        check_source_hash(source_dir, manifest),
        check_source_pdf_identity(source_dir, manifest),
        check_source_effective(source_dir, manifest),
        check_taxonomy_schema(taxonomy_schema, taxonomy),
        check_taxonomy_source_binding(taxonomy, manifest, manifest_relative),
        check_taxonomy_ids(taxonomy),
        check_taxonomy_parentage_order(taxonomy),
        check_taxonomy_locators(source_dir, manifest, taxonomy),
        check_taxonomy_task_source(source_dir, manifest, taxonomy),
        check_taxonomy_completeness(source_dir, manifest, taxonomy),
        check_taxonomy_render(
            project_root / "reports" / "far-taxonomy-g1.html",
            taxonomy,
            manifest,
            discrepancies,
        ),
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("taxonomy", type=Path)
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--json-output", type=Path)
    args = parser.parse_args()
    results = run_checks(args.project_root.resolve(), args.taxonomy.resolve())
    payload = json.dumps([asdict(result) for result in results], indent=2) + "\n"
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(payload, encoding="utf-8", newline="\n")
    if args.as_json:
        print(payload, end="")
    else:
        for result in results:
            print(f"{'PASS' if result.passed else 'FAIL'} {result.check_id}: {result.detail}")
    return 0 if all(result.passed for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
