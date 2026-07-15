#!/usr/bin/env python3
"""Validate the minimum artifact contract for an llm-wiki-ingest run."""

from __future__ import annotations

import argparse
import os
import re
from pathlib import Path


REQUIRED_NOTE_FILES = [
    "source-profile.md",
    "source-inventory.md",
    "knowledge-unit-inventory.md",
    "coverage-matrix.md",
    "omission-audit.md",
    "formal-page-plan.md",
    "audit-handoff.md",
]

ALLOWED_STATUS = {
    "formalized",
    "merged",
    "raw-only",
    "omitted-with-reason",
    "unresolved",
}


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_markdown_table_rows(text: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or not stripped.endswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if cells and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
            continue
        rows.append(cells)
    return rows


def validate_frontmatter(path: Path, errors: list[str]) -> None:
    text = read(path)
    if not text.startswith("---\n"):
        errors.append(f"{path}: missing YAML frontmatter")
        return
    try:
        end = text.index("\n---", 4)
    except ValueError:
        errors.append(f"{path}: unclosed YAML frontmatter")
        return
    frontmatter = text[4:end]
    for field in ["title:", "type:", "created:", "updated:", "domain:", "tags:", "sources:", "status:"]:
        if field not in frontmatter:
            errors.append(f"{path}: frontmatter missing {field}")


def split_target_paths(value: str) -> list[str]:
    return [part.strip().strip("`") for part in re.split(r"[;,]", value) if part.strip().strip("`")]


def validate_coverage(notes_dir: Path, wiki_root: Path, errors: list[str]) -> None:
    coverage_path = notes_dir / "coverage-matrix.md"
    text = read(coverage_path)
    rows = parse_markdown_table_rows(text)
    if len(rows) < 2:
        errors.append(f"{coverage_path}: coverage table has no data rows")
        return
    header = rows[0]
    required = ["source_unit_id", "source_location", "source_unit", "knowledge_role", "target_pages", "status", "reason_or_notes"]
    missing_required_columns = False
    for col in required:
        if col not in header:
            errors.append(f"{coverage_path}: missing column {col}")
            missing_required_columns = True
    if missing_required_columns:
        return
    idx = {name: header.index(name) for name in header}
    for row_num, row in enumerate(rows[1:], start=2):
        if len(row) < len(header):
            errors.append(f"{coverage_path}: row {row_num} has too few cells")
            continue
        unit_id = row[idx["source_unit_id"]]
        status = row[idx["status"]]
        target = row[idx["target_pages"]]
        reason = row[idx["reason_or_notes"]]
        if status not in ALLOWED_STATUS:
            errors.append(f"{coverage_path}: row {row_num} {unit_id} invalid status {status!r}")
        if status in {"raw-only", "omitted-with-reason", "unresolved"} and not reason:
            errors.append(f"{coverage_path}: row {row_num} {unit_id} requires reason_or_notes")
        if status in {"formalized", "merged"} and not target:
            errors.append(f"{coverage_path}: row {row_num} {unit_id} requires target_pages")
        if status in {"formalized", "merged"} and target:
            targets = split_target_paths(target)
            if not targets:
                errors.append(f"{coverage_path}: row {row_num} {unit_id} has no parseable target path")
            for value in targets:
                candidate = Path(value)
                if not candidate.is_absolute():
                    candidate = wiki_root / candidate
                if not candidate.is_file():
                    errors.append(f"{coverage_path}: row {row_num} {unit_id} target page missing: {candidate}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wiki-root", default=os.environ.get("WIKI_ROOT", str(Path.home() / "wiki")))
    parser.add_argument("--notes-dir", required=True)
    parser.add_argument("--raw", action="append", default=[])
    parser.add_argument("--formal", action="append", default=[])
    args = parser.parse_args()

    wiki_root = Path(args.wiki_root).resolve()
    notes_dir = Path(args.notes_dir)
    if not notes_dir.is_absolute():
        notes_dir = wiki_root / notes_dir
    formal_inputs = [Path(p) if Path(p).is_absolute() else wiki_root / p for p in args.formal]
    formal_pages: list[Path] = []
    for item in formal_inputs:
        if item.is_dir():
            formal_pages.extend(sorted(item.rglob("*.md")))
        else:
            formal_pages.append(item)
    raw_paths = [Path(p) if Path(p).is_absolute() else wiki_root / p for p in args.raw]

    errors: list[str] = []

    if not notes_dir.is_dir():
        errors.append(f"{notes_dir}: notes directory missing")
    else:
        for name in REQUIRED_NOTE_FILES:
            path = notes_dir / name
            if not path.exists():
                errors.append(f"{path}: missing")
            elif not read(path).strip():
                errors.append(f"{path}: empty")
        if (notes_dir / "coverage-matrix.md").exists():
            validate_coverage(notes_dir, wiki_root, errors)

    for raw in raw_paths:
        if not raw.exists():
            errors.append(f"{raw}: raw source missing")
    for formal in formal_pages:
        if not formal.exists():
            errors.append(f"{formal}: formal page missing")
        else:
            validate_frontmatter(formal, errors)

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("llm-wiki-ingest contract OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
