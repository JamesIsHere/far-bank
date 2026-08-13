#!/usr/bin/env python3
"""Independently probe the FAR Blueprint tables from PDF geometry.

The probe treats the table's drawn checkmarks and row rules as evidence.  It
does not consume the project taxonomy, so the verifier can use it to detect
missing rows, wrong skill assignments, and source-text drift.
"""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from pathlib import Path
from typing import Any, Iterable

import pdfplumber


def clean_text(value: str) -> str:
    """Normalize extraction artifacts without editorially rewriting wording."""
    value = "".join(" " if unicodedata.category(ch).startswith("C") else ch for ch in value)
    value = re.sub(r"\s+", " ", value).strip()
    # The source contains a control glyph between an initial capital and the
    # rest of several words (for example, "B\x07alance").
    value = re.sub(r"\b([A-Z]) ([a-z]{2,})\b", r"\1\2", value)
    return value


def _line_join(words: Iterable[dict[str, Any]]) -> str:
    lines: list[tuple[float, list[str]]] = []
    for word in sorted(words, key=lambda item: (item["top"], item["x0"])):
        for top, parts in lines:
            if abs(top - word["top"]) < 3:
                parts.append(word["text"])
                break
        else:
            lines.append((word["top"], [word["text"]]))
    return clean_text(" ".join(" ".join(parts) for _, parts in lines))


def _words_in_box(page: Any, x0: float, x1: float, top: float, bottom: float) -> list[dict[str, Any]]:
    return [
        word
        for word in page.extract_words(x_tolerance=2, y_tolerance=3)
        if word["x0"] >= x0 - 1
        and word["x1"] <= x1 + 1
        and word["top"] >= top - 1
        and word["bottom"] <= bottom + 1
    ]


def _table_group_rectangles(page: Any) -> list[dict[str, Any]]:
    return sorted(
        [
            rect
            for rect in page.rects
            if rect["width"] > 690 and 18 <= rect["height"] <= 26 and rect["top"] > 145
        ],
        key=lambda rect: rect["top"],
    )


def _checkmark_curves(page: Any) -> list[dict[str, Any]]:
    return sorted(
        [
            curve
            for curve in page.curves
            if 9 <= curve["width"] <= 13
            and 6 <= curve["height"] <= 9
            and 220 <= curve["x0"] <= 420
        ],
        key=lambda curve: curve["top"],
    )


def _skill_for_checkmark(curve: dict[str, Any]) -> str:
    center = (curve["x0"] + curve["x1"]) / 2
    if center < 279:
        return "remembering_and_understanding"
    if center < 329.4:
        return "application"
    if center < 379.8:
        return "analysis"
    return "evaluation"


def _printed_page_label(page: Any) -> str:
    match = re.search(r"\bFAR[1-9][0-9]*\b", page.extract_text() or "")
    if not match:
        raise ValueError("FAR printed page label not found")
    return match.group(0)


def _area_heading(page: Any) -> tuple[str, str, int, int] | None:
    text = clean_text(page.extract_text() or "")
    match = re.search(r"Area (I|II|III) – ([^(]+?) \(([0-9]+)–([0-9]+)%\)", text)
    if not match:
        return None
    return match.group(1), clean_text(match.group(2)), int(match.group(3)), int(match.group(4))


def _topic_events(page: Any, group_rects: list[dict[str, Any]]) -> list[dict[str, Any]]:
    words = []
    for word in page.extract_words(x_tolerance=2, y_tolerance=3):
        if not (44 <= word["x0"] and word["x1"] <= 203 and 150 <= word["top"] <= 551):
            continue
        center_y = (word["top"] + word["bottom"]) / 2
        if any(rect["top"] - 1 <= center_y <= rect["bottom"] + 1 for rect in group_rects):
            continue
        words.append(word)

    lines: list[dict[str, Any]] = []
    for word in sorted(words, key=lambda item: (item["top"], item["x0"])):
        for line in lines:
            if abs(line["top"] - word["top"]) < 3:
                line["words"].append(word)
                break
        else:
            lines.append({"top": word["top"], "words": [word]})

    events: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for line in lines:
        text = _line_join(line["words"])
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
        title = re.sub(r"\s*\(continued\)\s*$", "", title)
        event["official_title"] = title
        event["official_heading"] = f"{event['code']}. {title}"
    return events


def probe_far_tables(pdf_path: Path, first_page: int = 35, last_page: int = 46) -> dict[str, Any]:
    areas: list[dict[str, Any]] = []
    groups: list[dict[str, Any]] = []
    topics: list[dict[str, Any]] = []
    tasks: list[dict[str, Any]] = []
    seen_areas: set[str] = set()
    seen_groups: set[tuple[str, str]] = set()
    seen_topics: set[tuple[str, str, str]] = set()
    active_area: str | None = None
    active_group: str | None = None
    active_topic: str | None = None

    with pdfplumber.open(pdf_path) as pdf:
        for physical_page in range(first_page, last_page + 1):
            page = pdf.pages[physical_page - 1]
            printed_page = _printed_page_label(page)
            area = _area_heading(page)
            if area:
                code, title, minimum, maximum = area
                active_area = code
                if code not in seen_areas:
                    seen_areas.add(code)
                    areas.append(
                        {
                            "code": code,
                            "official_title": title,
                            "official_heading": f"Area {code} – {title} ({minimum}–{maximum}%)",
                            "allocation_percent": {"minimum": minimum, "maximum": maximum},
                            "physical_page": physical_page,
                            "printed_page_label": printed_page,
                        }
                    )

            group_rects = _table_group_rectangles(page)
            group_events = []
            for rect in group_rects:
                heading = _line_join(_words_in_box(page, rect["x0"], rect["x1"], rect["top"], rect["bottom"]))
                heading = re.sub(r"\s*\(continued\)\s*$", "", heading)
                match = re.match(r"^([A-Z]+)\.\s*(.+)$", heading)
                if not match:
                    continue
                group_events.append({"top": rect["top"], "code": match.group(1), "official_title": match.group(2), "official_heading": heading})

            topic_events = _topic_events(page, group_rects)
            curve_events = [{"top": curve["top"], "curve": curve, "ordinal": index} for index, curve in enumerate(_checkmark_curves(page), 1)]
            events = (
                [(item["top"], 0, "group", item) for item in group_events]
                + [(item["top"], 1, "topic", item) for item in topic_events]
                + [(item["top"], 2, "task", item) for item in curve_events]
            )

            row_lines = sorted(
                {
                    round(line["top"], 3)
                    for line in page.lines
                    if line["width"] > 300 and 420 <= line["x0"] <= 440
                }
            )
            for _, _, event_type, event in sorted(events, key=lambda item: (item[0], item[1])):
                if event_type == "group":
                    active_group = event["code"]
                    active_topic = None
                    key = (active_area or "", active_group)
                    if key not in seen_groups:
                        seen_groups.add(key)
                        groups.append(
                            {
                                "area_code": active_area,
                                "code": active_group,
                                "official_title": event["official_title"],
                                "official_heading": event["official_heading"],
                                "physical_page": physical_page,
                                "printed_page_label": printed_page,
                            }
                        )
                elif event_type == "topic":
                    active_topic = event["code"]
                    key = (active_area or "", active_group or "", active_topic)
                    if key not in seen_topics:
                        seen_topics.add(key)
                        topics.append(
                            {
                                "area_code": active_area,
                                "group_code": active_group,
                                "code": active_topic,
                                "official_title": event["official_title"],
                                "official_heading": event["official_heading"],
                                "physical_page": physical_page,
                                "printed_page_label": printed_page,
                            }
                        )
                else:
                    curve = event["curve"]
                    center_y = (curve["top"] + curve["bottom"]) / 2
                    previous = max((line for line in row_lines if line < center_y), default=center_y - 15)
                    following = min((line for line in row_lines if line > center_y), default=center_y + 25)
                    task_text = _line_join(_words_in_box(page, 430, 748, previous, following))
                    tasks.append(
                        {
                            "area_code": active_area,
                            "group_code": active_group,
                            "topic_code": active_topic,
                            "physical_page": physical_page,
                            "printed_page_label": printed_page,
                            "row_ordinal_on_page": event["ordinal"],
                            "skill_level": _skill_for_checkmark(curve),
                            "official_text": task_text,
                        }
                    )

    return {
        "probe_version": "1.0.0",
        "pdf_sha256_required": None,
        "physical_page_range": {"first": first_page, "last": last_page},
        "areas": areas,
        "groups": groups,
        "topics": topics,
        "tasks": tasks,
        "counts": {
            "areas": len(areas),
            "groups": len(groups),
            "topics": len(topics),
            "tasks": len(tasks),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--first-page", type=int, default=35)
    parser.add_argument("--last-page", type=int, default=46)
    args = parser.parse_args()
    print(json.dumps(probe_far_tables(args.pdf, args.first_page, args.last_page), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
