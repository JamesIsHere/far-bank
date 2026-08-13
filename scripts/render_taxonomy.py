#!/usr/bin/env python3
"""Render the source-linked FAR taxonomy for human Gate G1 review."""

from __future__ import annotations

import argparse
import html
import json
from collections import Counter
from pathlib import Path
from typing import Any


SKILL_LABELS = {
    "remembering_and_understanding": "Remembering & Understanding",
    "application": "Application",
    "analysis": "Analysis",
}


def _e(value: Any) -> str:
    return html.escape(str(value), quote=True)


def _all_tasks(taxonomy: dict[str, Any]) -> list[dict[str, Any]]:
    tasks = []
    for area in taxonomy["areas"]:
        for group in area["groups"]:
            tasks.extend(group["tasks"])
            for topic in group["topics"]:
                tasks.extend(topic["tasks"])
    return tasks


def _source_link(locator: dict[str, Any]) -> str:
    page = locator["physical_page"]
    printed = locator["printed_page_label"]
    return (
        f'<a class="source-link" href="../sources/aicpa/2026-01/CPA_Exam_Blueprints_2026.pdf#page={page}" '
        f'title="{_e(locator["anchor_text"])}">{_e(printed)} · PDF {page}</a>'
    )


def _task_rows(tasks: list[dict[str, Any]]) -> str:
    rows = []
    for task in tasks:
        skill = task["skill_level"]
        rows.append(
            "<tr>"
            f'<td class="id"><code>{_e(task["id"])}</code></td>'
            f'<td><span class="skill skill-{_e(skill)}">{_e(SKILL_LABELS[skill])}</span></td>'
            f'<td class="task-text">{_e(task["official_text"])}</td>'
            f'<td>{_source_link(task["source_locator"])}</td>'
            "</tr>"
        )
    return "".join(rows)


def render_taxonomy_html(
    taxonomy: dict[str, Any], manifest: dict[str, Any], discrepancies: dict[str, Any]
) -> str:
    tasks = _all_tasks(taxonomy)
    groups = [group for area in taxonomy["areas"] for group in area["groups"]]
    topics = [topic for group in groups for topic in group["topics"]]
    skills = Counter(task["skill_level"] for task in tasks)

    area_nav = "".join(
        f'<a href="#{_e(area["id"])}">Area {_e(area["code"])} · {_e(area["official_title"])}</a>'
        for area in taxonomy["areas"]
    )
    area_sections = []
    for area in taxonomy["areas"]:
        group_sections = []
        for group in area["groups"]:
            if group["topics"]:
                content = []
                for topic in group["topics"]:
                    content.append(
                        '<section class="topic">'
                        '<div class="topic-heading">'
                        f'<h4>{_e(topic["official_heading"])}</h4>{_source_link(topic["source_locator"])}'
                        "</div>"
                        '<div class="table-wrap"><table><thead><tr>'
                        '<th scope="col">Stable task ID</th><th scope="col">Official skill</th>'
                        '<th scope="col">Representative task</th><th scope="col">Source row</th>'
                        f'</tr></thead><tbody>{_task_rows(topic["tasks"])}</tbody></table></div>'
                        "</section>"
                    )
                group_content = "".join(content)
            else:
                group_content = (
                    '<div class="table-wrap"><table><thead><tr>'
                    '<th scope="col">Stable task ID</th><th scope="col">Official skill</th>'
                    '<th scope="col">Representative task</th><th scope="col">Source row</th>'
                    f'</tr></thead><tbody>{_task_rows(group["tasks"])}</tbody></table></div>'
                )
            group_sections.append(
                '<details class="group" open>'
                '<summary>'
                f'<span><code>{_e(group["id"])}</code><strong>{_e(group["official_heading"])}</strong></span>'
                f'{_source_link(group["source_locator"])}'
                "</summary>"
                f'{group_content}</details>'
            )
        allocation = area["allocation_percent"]
        area_sections.append(
            f'<section class="area" id="{_e(area["id"])}">'
            '<div class="area-heading">'
            f'<div><p class="eyebrow">Area {_e(area["code"])}</p><h2>{_e(area["official_title"])}</h2></div>'
            f'<div class="area-meta"><span>{allocation["minimum"]}–{allocation["maximum"]}% allocation</span>'
            f'{_source_link(area["source_locator"])}</div>'
            "</div>"
            f'{"".join(group_sections)}</section>'
        )

    discrepancy_rows = "".join(
        "<tr>"
        f'<td><code>{_e(entry["id"])}</code></td>'
        f'<td>{_e(entry["status"])}</td>'
        f'<td>{_e(entry["description"])}</td>'
        f'<td>{_e(entry["disposition"])}</td>'
        "</tr>"
        for entry in discrepancies["entries"]
    )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>FAR Blueprint Taxonomy · Gate G1</title>
  <style>
    :root {{ color-scheme: light; --ink:#172033; --muted:#5f6878; --line:#dce1e9; --paper:#fff; --wash:#f4f6fa; --purple:#6f2771; --orange:#dc6d24; --ru:#4065b3; --app:#d59613; --analysis:#087f77; }}
    * {{ box-sizing:border-box; }}
    html {{ scroll-behavior:smooth; }}
    body {{ margin:0; color:var(--ink); background:var(--wash); font:15px/1.48 Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
    a {{ color:var(--purple); }}
    code {{ font:12px/1.4 ui-monospace, SFMono-Regular, Consolas, monospace; color:#384056; }}
    .hero {{ padding:56px max(24px, calc((100vw - 1320px)/2)); color:#fff; background:linear-gradient(120deg,#55236f,#9b2f68 65%,#d45e35); }}
    .hero .kicker {{ margin:0 0 10px; letter-spacing:.12em; text-transform:uppercase; opacity:.78; font-weight:700; font-size:12px; }}
    .hero h1 {{ max-width:920px; margin:0; font-size:clamp(34px,5vw,64px); line-height:1.02; letter-spacing:-.035em; }}
    .hero .lede {{ max-width:850px; margin:20px 0 0; font-size:18px; opacity:.9; }}
    main {{ width:min(1320px,calc(100% - 32px)); margin:26px auto 80px; }}
    .notice {{ display:flex; gap:16px; align-items:flex-start; padding:18px 20px; border:1px solid #efc28c; border-left:5px solid var(--orange); border-radius:12px; background:#fff8ee; }}
    .notice strong {{ white-space:nowrap; }}
    .metrics {{ display:grid; grid-template-columns:repeat(7,minmax(100px,1fr)); gap:12px; margin:22px 0; }}
    .metric {{ min-height:104px; padding:16px; border:1px solid var(--line); border-radius:12px; background:var(--paper); }}
    .metric b {{ display:block; font-size:28px; letter-spacing:-.03em; }}
    .metric span {{ color:var(--muted); font-size:13px; }}
    nav {{ display:flex; flex-wrap:wrap; gap:10px; margin:0 0 30px; }}
    nav a {{ padding:9px 12px; border:1px solid var(--line); border-radius:999px; text-decoration:none; background:#fff; font-weight:650; }}
    .provenance,.discrepancies {{ margin:24px 0 34px; padding:24px; border:1px solid var(--line); border-radius:14px; background:#fff; }}
    .provenance h2,.discrepancies h2 {{ margin:0 0 12px; }}
    .provenance dl {{ display:grid; grid-template-columns:max-content 1fr; gap:7px 16px; margin:0; }}
    .provenance dt {{ color:var(--muted); font-weight:650; }}
    .provenance dd {{ margin:0; overflow-wrap:anywhere; }}
    .area {{ scroll-margin-top:20px; margin:34px 0 50px; }}
    .area-heading {{ display:flex; justify-content:space-between; gap:20px; align-items:end; padding:0 4px 14px; border-bottom:3px solid var(--orange); }}
    .area-heading h2 {{ margin:0; font-size:31px; letter-spacing:-.025em; }}
    .eyebrow {{ margin:0 0 2px; color:var(--orange); text-transform:uppercase; letter-spacing:.1em; font-size:12px; font-weight:800; }}
    .area-meta {{ display:flex; flex-wrap:wrap; justify-content:flex-end; gap:10px 16px; color:var(--muted); }}
    details.group {{ margin:14px 0; border:1px solid var(--line); border-radius:12px; background:#fff; overflow:hidden; }}
    details.group > summary {{ display:flex; justify-content:space-between; gap:16px; align-items:center; cursor:pointer; padding:15px 18px; background:#eef0f5; }}
    details.group > summary span {{ display:flex; gap:14px; align-items:baseline; }}
    details.group > summary strong {{ font-size:16px; }}
    .topic {{ padding:10px 16px 18px; }}
    .topic + .topic {{ border-top:1px solid var(--line); }}
    .topic-heading {{ display:flex; justify-content:space-between; gap:16px; align-items:baseline; }}
    .topic-heading h4 {{ margin:8px 0; font-size:15px; }}
    .table-wrap {{ overflow-x:auto; }}
    table {{ width:100%; border-collapse:collapse; }}
    th {{ padding:9px 10px; color:var(--muted); background:#fafbfc; text-align:left; text-transform:uppercase; letter-spacing:.05em; font-size:10px; }}
    td {{ padding:10px; border-top:1px solid var(--line); vertical-align:top; }}
    td.id {{ width:235px; }}
    td.task-text {{ min-width:360px; }}
    .skill {{ display:inline-block; padding:4px 8px; border-radius:999px; color:#fff; white-space:nowrap; font-size:11px; font-weight:750; }}
    .skill-remembering_and_understanding {{ background:var(--ru); }}
    .skill-application {{ background:var(--app); color:#211a08; }}
    .skill-analysis {{ background:var(--analysis); }}
    .source-link {{ white-space:nowrap; font-size:12px; font-weight:650; }}
    .discrepancies table {{ margin-top:12px; }}
    footer {{ width:min(1320px,calc(100% - 32px)); margin:0 auto 36px; color:var(--muted); font-size:12px; }}
    @media (max-width:900px) {{ .metrics {{ grid-template-columns:repeat(2,1fr); }} .area-heading,details.group > summary,.topic-heading {{ align-items:flex-start; flex-direction:column; }} .area-meta {{ justify-content:flex-start; }} td.id {{ width:auto; }} }}
    @media print {{ body {{ background:#fff; }} .hero {{ padding:28px; }} main {{ width:100%; margin:16px 0; }} details.group {{ break-inside:avoid; }} .source-link {{ color:#000; }} }}
  </style>
</head>
<body>
  <header class="hero">
    <p class="kicker">CPA Learning · FAR Bank · Human Gate G1</p>
    <h1>Official FAR Blueprint taxonomy</h1>
    <p class="lede">A source-linked coverage spine extracted from the AICPA Blueprint effective {_e(manifest["publication"]["effective_period_label"])}. This artifact asks one question: is the captured hierarchy complete and usable?</p>
  </header>
  <main>
    <div class="notice"><strong>Scope boundary</strong><span>No questions exist at this gate. Approval here validates the taxonomy medium only; it does not approve question quality or coverage depth.</span></div>
    <section class="metrics" aria-label="Taxonomy summary">
      <div class="metric"><b>{len(taxonomy["areas"])}</b><span>official areas</span></div>
      <div class="metric"><b>{len(groups)}</b><span>official groups</span></div>
      <div class="metric"><b>{len(topics)}</b><span>official topics</span></div>
      <div class="metric"><b>{len(tasks)}</b><span>representative tasks</span></div>
      <div class="metric"><b>{skills["remembering_and_understanding"]}</b><span>remember / understand</span></div>
      <div class="metric"><b>{skills["application"]}</b><span>application</span></div>
      <div class="metric"><b>{skills["analysis"]}</b><span>analysis</span></div>
    </section>
    <nav aria-label="Area navigation">{area_nav}</nav>
    <section class="provenance">
      <h2>Source identity</h2>
      <dl>
        <dt>Publisher</dt><dd>{_e(manifest["authority"]["publisher"])}</dd>
        <dt>Official page</dt><dd><a href="{_e(manifest["authority"]["landing_page_url"])}">AICPA · What is tested on the CPA Exam</a></dd>
        <dt>Preserved file</dt><dd><a href="../sources/aicpa/2026-01/{_e(manifest["retrieval"]["local_file"])}">{_e(manifest["retrieval"]["local_file"])}</a></dd>
        <dt>Effective</dt><dd>{_e(manifest["publication"]["effective_period_label"])}</dd>
        <dt>SHA-256</dt><dd><code>{_e(manifest["retrieval"]["sha256"])}</code></dd>
        <dt>Reconciliation</dt><dd>3 areas · 22 groups · 18 topics · 113 drawn task/skill rows · zero open taxonomy discrepancies</dd>
      </dl>
    </section>
    {"".join(area_sections)}
    <section class="discrepancies">
      <h2>Discrepancy report</h2>
      <p>There are no open hierarchy discrepancies. Two source-level extraction or metadata anomalies are preserved below so the clean result is not achieved by hiding them.</p>
      <div class="table-wrap"><table><thead><tr><th>ID</th><th>Status</th><th>Observation</th><th>Disposition</th></tr></thead><tbody>{discrepancy_rows}</tbody></table></div>
    </section>
  </main>
  <footer>Deterministic artifact for taxonomy <code>{_e(taxonomy["taxonomy_id"])}</code>. Official labels are kept in the taxonomy; future teaching labels belong in the separate supplement layer.</footer>
</body>
</html>
"""


def main() -> int:
    project_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--taxonomy", type=Path, default=project_root / "data" / "far-taxonomy.json")
    parser.add_argument("--manifest", type=Path, default=project_root / "sources" / "aicpa" / "2026-01" / "source-manifest.json")
    parser.add_argument("--discrepancies", type=Path, default=project_root / "data" / "discrepancies.json")
    parser.add_argument("--output", type=Path, default=project_root / "reports" / "far-taxonomy-g1.html")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    taxonomy = json.loads(args.taxonomy.read_text(encoding="utf-8"))
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    discrepancies = json.loads(args.discrepancies.read_text(encoding="utf-8"))
    rendered = render_taxonomy_html(taxonomy, manifest, discrepancies)
    if args.check:
        current = args.output.read_text(encoding="utf-8") if args.output.exists() else ""
        if current != rendered:
            print(f"stale or missing: {args.output}")
            return 1
        print(f"reproducible: {args.output}")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8", newline="\n")
    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
