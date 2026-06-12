#!/usr/bin/env python3
"""Generate a coverage matrix template from a book chapter inventory."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_inventory(path: Path) -> list[dict]:
    if path.suffix == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        return data.get("chapters", data if isinstance(data, list) else [])
    sibling_json = path.with_suffix(".json")
    if sibling_json.exists():
        data = json.loads(sibling_json.read_text(encoding="utf-8"))
        return data.get("chapters", [])
    raise SystemExit(f"Cannot parse Markdown inventory without sibling JSON: {sibling_json}")


def status_for(row: dict) -> str:
    title = str(row.get("source_title", ""))
    if any(word in title for word in ["版权", "目录", "文前插图"]):
        return "raw-only"
    if row.get("time_sensitivity") == "high":
        return "unresolved"
    targets = row.get("target_pages") or []
    if len(targets) > 1:
        return "merged"
    return "formalized"


def rationale_for(row: dict, status: str) -> str:
    if status == "raw-only":
        return "Frontmatter or non-knowledge source material; preserve in raw source only."
    if status == "unresolved":
        return "Platform-specific or time-sensitive chapter; preserve source and verify current rules before formalizing as present-day guidance."
    if status == "merged":
        return "Knowledge spans multiple formal pages; split by method and Agent routing need."
    return "Represent directly in the target formal page."


def md_cell(value: object) -> str:
    if isinstance(value, list):
        value = ", ".join(str(v) for v in value)
    return str(value or "").replace("|", "\\|").replace("\n", " ")


def write_matrix(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Coverage Matrix",
        "",
        f"- Source chapters: {len(rows)}",
        "- Scope: chapter-level starter matrix generated from `chapter-inventory`. Expand this into claim/knowledge-unit rows before marking a book ingest complete.",
        "",
        "| source_unit_id | source_location | source_unit | knowledge_role | target_pages | status | reason_or_notes | chapter_id | chapter_title | page_or_section |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        status = status_for(row)
        source_id = row.get("source_id")
        source_title = row.get("source_title")
        source_file = row.get("source_file")
        lines.append(
            "| "
            + " | ".join(
                [
                    md_cell(source_id),
                    md_cell(source_file),
                    md_cell(source_title),
                    md_cell(row.get("topic_groups") or "chapter"),
                    md_cell(row.get("target_pages")),
                    md_cell(status),
                    md_cell(rationale_for(row, status)),
                    md_cell(source_id),
                    md_cell(source_title),
                    md_cell(source_file),
                ]
            )
            + " |"
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate coverage-matrix.md from chapter inventory.")
    parser.add_argument("inventory", type=Path, help="chapter-inventory.json or chapter-inventory.md with sibling JSON")
    parser.add_argument("--output", required=True, type=Path, help="Output coverage-matrix.md")
    args = parser.parse_args()

    rows = load_inventory(args.inventory.expanduser())
    write_matrix(args.output.expanduser(), rows)
    print(f"Coverage matrix written: {args.output.expanduser()}")
    print(f"Rows: {len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
