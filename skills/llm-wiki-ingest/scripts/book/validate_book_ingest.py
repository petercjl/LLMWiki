#!/usr/bin/env python3
"""Validate the mechanical completeness of a book-to-LLM-Wiki ingest."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


REQUIRED_RAW_FILES = ["source-profile.json", "metadata.md", "toc.md", "manifest.md"]
REQUIRED_NOTES = [
    "source-profile.md",
    "source-inventory.md",
    "segment-plan.md",
    "knowledge-architecture-plan.md",
    "chapter-inventory.md",
    "knowledge-unit-inventory.md",
    "coverage-matrix.md",
    "omission-audit.md",
    "formal-page-plan.md",
    "audit-handoff.md",
]
SHELL_MARKERS = [
    "内容待补充",
    "（占位）",
    "占位内容",
    "TODO:",
    "TBD",
    "本节用于把课程中的口头经验重构成稳定的方法框架",
]


def has_frontmatter(text: str) -> bool:
    return text.startswith("---\n") and "\n---\n" in text[4:]


def frontmatter_block(text: str) -> str:
    if not has_frontmatter(text):
        return ""
    return text.split("\n---\n", 1)[0] + "\n---"


def count_coverage_rows(path: Path) -> int:
    if not path.exists():
        return 0
    rows = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("| ch") or re.match(r"^\|\s*[^|]+\s*\|", line):
            if "---" not in line and "source_id" not in line:
                rows += 1
    return rows


def check_index_mentions(index_path: Path, formal_dir: Path) -> list[str]:
    if not index_path or not index_path.exists():
        return []
    text = index_path.read_text(encoding="utf-8")
    missing = []
    for page in sorted(formal_dir.glob("*.md")):
        rel_stem = page.stem
        if rel_stem == "index":
            continue
        if rel_stem not in text and page.name not in text:
            missing.append(page.name)
    return missing


def validate(args: argparse.Namespace) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    wiki_root = args.wiki_root.expanduser()
    raw_dir = args.raw_dir.expanduser()
    notes_dir = args.notes_dir.expanduser()
    formal_dir = args.formal_dir.expanduser()

    if not wiki_root.exists():
        errors.append(f"Missing wiki root: {wiki_root}")
    if not raw_dir.exists():
        errors.append(f"Missing raw dir: {raw_dir}")
    if not notes_dir.exists():
        errors.append(f"Missing notes dir: {notes_dir}")
    if not formal_dir.exists():
        errors.append(f"Missing formal dir: {formal_dir}")

    if raw_dir.exists():
        if not (raw_dir / "source.epub").exists() and not any(raw_dir.glob("source.*")):
            warnings.append("Raw dir has no source.epub or source.* file")
        for name in REQUIRED_RAW_FILES:
            if not (raw_dir / name).exists():
                errors.append(f"Missing raw helper file: {raw_dir / name}")
        if not (raw_dir / "chapters").exists():
            errors.append(f"Missing extracted chapters directory: {raw_dir / 'chapters'}")

    if notes_dir.exists():
        for name in REQUIRED_NOTES:
            if not (notes_dir / name).exists():
                errors.append(f"Missing extraction note: {notes_dir / name}")
        coverage_rows = count_coverage_rows(notes_dir / "coverage-matrix.md")
        if coverage_rows == 0:
            errors.append("Coverage matrix has no data rows")

    formal_pages = []
    if formal_dir.exists():
        formal_pages = sorted(formal_dir.glob("*.md"))
        if not formal_pages:
            errors.append(f"No formal Markdown pages in {formal_dir}")
        if not any(page.name.endswith("agent-usage-template.md") or "agent" in page.name for page in formal_pages):
            warnings.append("No obvious Agent usage template page found")
        for page in formal_pages:
            text = page.read_text(encoding="utf-8")
            if not has_frontmatter(text):
                errors.append(f"Missing frontmatter: {page}")
                continue
            fm = frontmatter_block(text)
            if "sources:" not in fm:
                warnings.append(f"Frontmatter has no sources field: {page}")
            for marker in SHELL_MARKERS:
                if marker in text:
                    errors.append(f"Shell marker '{marker}' found in {page}")

    if args.domain_index:
        missing = check_index_mentions(args.domain_index.expanduser(), formal_dir)
        if missing:
            warnings.append(f"Domain index may not mention pages: {', '.join(missing[:10])}")
    if args.wiki_index:
        if not args.wiki_index.expanduser().exists():
            warnings.append(f"Wiki index not found: {args.wiki_index.expanduser()}")
    elif wiki_root.exists() and not (wiki_root / "index.md").exists():
        warnings.append("Wiki root has no index.md")

    log_path = wiki_root / "log.md"
    if wiki_root.exists() and not log_path.exists():
        warnings.append("Wiki root has no log.md")

    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate mechanical completeness of a book ingest.")
    parser.add_argument("--wiki-root", required=True, type=Path)
    parser.add_argument("--raw-dir", required=True, type=Path)
    parser.add_argument("--notes-dir", required=True, type=Path)
    parser.add_argument("--formal-dir", required=True, type=Path)
    parser.add_argument("--domain-index", type=Path)
    parser.add_argument("--wiki-index", type=Path)
    args = parser.parse_args()

    errors, warnings = validate(args)
    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}")
    print(f"Warnings: {len(warnings)}")
    print(f"Errors: {len(errors)}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
