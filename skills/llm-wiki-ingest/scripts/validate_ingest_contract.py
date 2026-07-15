#!/usr/bin/env python3
"""Validate the minimum artifact contract for an llm-wiki-ingest run."""

from __future__ import annotations

import argparse
import hashlib
import os
import re
from collections import defaultdict
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

BOILERPLATE_CJK = [
    "本节用于把课程中的口头经验重构成稳定的方法框架",
    "请基于本节方法，分析当前品牌/产品/视觉材料是否存在同类问题",
    "请基于本节方法，分析当前品牌",
    "内容待补充",
    "待补充。",
    "（占位）",
    "(占位)",
    "占位内容",
    "此处占位",
]
BOILERPLATE_ASCII = [
    r"TODO[:：]",
    r"\bTBD\b",
    r"<!--\s*placeholder",
    r"\bLorem ipsum\b",
]
ASCII_BOILERPLATE_RE = re.compile("|".join(BOILERPLATE_ASCII), re.IGNORECASE)
FRONTMATTER_RE = re.compile(r"^---\n.*?\n---\n", re.DOTALL)
HEADING_RE = re.compile(r"^#{1,6}\s.*$", re.MULTILINE)
WHITESPACE_RE = re.compile(r"\s+")


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


def extract_frontmatter(text: str) -> str:
    if not text.startswith("---\n"):
        return ""
    try:
        end = text.index("\n---", 4)
    except ValueError:
        return ""
    return text[4:end]


def frontmatter_sources(text: str) -> list[str]:
    frontmatter = extract_frontmatter(text)
    if not frontmatter:
        return []
    lines = frontmatter.splitlines()
    sources: list[str] = []
    in_sources = False
    for line in lines:
        if line == "sources:":
            in_sources = True
            continue
        if in_sources and line and not line[0].isspace():
            break
        if in_sources:
            match = re.match(r"^\s*-\s*(.+?)\s*$", line)
            if match:
                sources.append(match.group(1).strip("'\""))
    return sources


def strip_to_body(text: str) -> str:
    text = FRONTMATTER_RE.sub("", text, count=1)
    text = HEADING_RE.sub("", text)
    return text.strip()


def find_boilerplate(text: str) -> list[str]:
    hits = [marker for marker in BOILERPLATE_CJK if marker in text]
    hits.extend(sorted(set(match.group(0) for match in ASCII_BOILERPLATE_RE.finditer(text))))
    return hits


def validate_formal_quality(formal_pages: list[Path], errors: list[str], min_body_bytes: int) -> None:
    fingerprints: dict[str, list[Path]] = defaultdict(list)
    for path in formal_pages:
        if not path.is_file() or path.suffix.lower() != ".md":
            continue
        text = read(path)
        sources = frontmatter_sources(text)
        if not any("raw/" in source.replace("\\", "/") for source in sources):
            errors.append(f"{path}: sources must include a durable raw/ source path")
        if not any("_meta/extraction-notes/" in source.replace("\\", "/") for source in sources):
            errors.append(f"{path}: sources must include an _meta/extraction-notes/ reference")
        hits = find_boilerplate(text)
        if hits:
            errors.append(f"{path}: placeholder or boilerplate marker present: {', '.join(hits)}")

        body = strip_to_body(text)
        body_bytes = len(body.encode("utf-8"))
        is_index = path.name.lower() in {"index.md", "readme.md"}
        if not is_index and body_bytes < min_body_bytes:
            errors.append(
                f"{path}: formal page body is too thin ({body_bytes} bytes; minimum {min_body_bytes})"
            )

        normalized = WHITESPACE_RE.sub(" ", body).strip()
        if normalized:
            digest = hashlib.sha1(normalized.encode("utf-8")).hexdigest()
            fingerprints[digest].append(path)

    for paths in fingerprints.values():
        if len(paths) > 1:
            joined = ", ".join(str(path) for path in paths)
            errors.append(f"duplicate formal-page bodies detected: {joined}")


def split_target_paths(value: str) -> list[str]:
    return [part.strip().strip("`") for part in re.split(r"[;,]", value) if part.strip().strip("`")]


def normalize_disposition(value: str) -> str:
    for status in sorted(ALLOWED_STATUS, key=len, reverse=True):
        if value.strip().startswith(status):
            return status
    return value.strip()


def inventory_dispositions(path: Path) -> dict[str, str]:
    text = read(path)
    result: dict[str, str] = {}
    current: list[list[str]] = []

    def consume(rows: list[list[str]]) -> None:
        if len(rows) < 2:
            return
        header = rows[0]
        id_col = next((name for name in ["source_unit_id", "ID", "id"] if name in header), None)
        status_col = next((name for name in ["status", "disposition", "处置"] if name in header), None)
        if not id_col or not status_col:
            return
        id_idx = header.index(id_col)
        status_idx = header.index(status_col)
        for row in rows[1:]:
            if len(row) <= max(id_idx, status_idx):
                continue
            unit_id = row[id_idx].strip()
            if not unit_id or not re.search(r"\d", unit_id):
                continue
            result[unit_id] = normalize_disposition(row[status_idx])

    for line in text.splitlines() + [""]:
        stripped = line.strip()
        if stripped.startswith("|") and stripped.endswith("|"):
            cells = [cell.strip() for cell in stripped.strip("|").split("|")]
            if cells and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
                continue
            current.append(cells)
        elif current:
            consume(current)
            current = []
    return result


def validate_coverage(notes_dir: Path, wiki_root: Path, errors: list[str]) -> dict[str, str]:
    coverage_path = notes_dir / "coverage-matrix.md"
    text = read(coverage_path)
    rows = parse_markdown_table_rows(text)
    if len(rows) < 2:
        errors.append(f"{coverage_path}: coverage table has no data rows")
        return {}
    header = rows[0]
    required = ["source_unit_id", "source_location", "source_unit", "knowledge_role", "target_pages", "status", "reason_or_notes"]
    missing_required_columns = False
    for col in required:
        if col not in header:
            errors.append(f"{coverage_path}: missing column {col}")
            missing_required_columns = True
    if missing_required_columns:
        return {}
    idx = {name: header.index(name) for name in header}
    dispositions: dict[str, str] = {}
    for row_num, row in enumerate(rows[1:], start=2):
        if len(row) < len(header):
            errors.append(f"{coverage_path}: row {row_num} has too few cells")
            continue
        unit_id = row[idx["source_unit_id"]]
        status = row[idx["status"]]
        target = row[idx["target_pages"]]
        reason = row[idx["reason_or_notes"]]
        if re.fullmatch(r"[A-Za-z]+\d+\s*[-–—]\s*[A-Za-z]*\d+", unit_id):
            errors.append(f"{coverage_path}: row {row_num} uses a unit range {unit_id!r}; every source unit needs its own row")
        if unit_id in dispositions:
            errors.append(f"{coverage_path}: duplicate source_unit_id {unit_id!r}")
        dispositions[unit_id] = status
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
    return dispositions


def validate_inventory_against_coverage(notes_dir: Path, coverage: dict[str, str], errors: list[str]) -> None:
    inventory_path = notes_dir / "knowledge-unit-inventory.md"
    if not inventory_path.is_file() or not coverage:
        return
    inventory = inventory_dispositions(inventory_path)
    for unit_id, disposition in inventory.items():
        if unit_id not in coverage:
            errors.append(f"{notes_dir / 'coverage-matrix.md'}: missing source unit {unit_id} from knowledge-unit-inventory.md")
            continue
        if disposition in ALLOWED_STATUS and coverage[unit_id] != disposition:
            errors.append(
                f"{notes_dir / 'coverage-matrix.md'}: {unit_id} status {coverage[unit_id]!r} "
                f"does not match inventory disposition {disposition!r}"
            )


def validate_audit_handoff(notes_dir: Path, errors: list[str]) -> None:
    path = notes_dir / "audit-handoff.md"
    if not path.is_file():
        return
    validate_frontmatter(path, errors)
    text = read(path)
    for heading in [
        "## Source",
        "## Outputs",
        "## Placement Confirmation",
        "## Coverage Summary",
        "## Expected Agent Use",
        "## Known Risks",
        "## Self-Validation",
    ]:
        if heading not in text:
            errors.append(f"{path}: missing required section {heading}")
    for label in [
        "User confirmation:",
        "Confirmation evidence:",
        "Final confirmed path:",
        "No formal write before placement confirmation:",
        "Placeholder scan:",
        "Representative term search:",
        "Index/log check:",
        "Remaining gaps:",
    ]:
        if label not in text:
            errors.append(f"{path}: missing required field {label}")


def validate_durable_source_inventory(notes_dir: Path, errors: list[str]) -> None:
    path = notes_dir / "source-inventory.md"
    if not path.is_file():
        return
    text = read(path).replace("\\", "/")
    if "_meta/working/" in text:
        errors.append(f"{path}: final source inventory must not reference disposable _meta/working/ paths")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wiki-root", default=os.environ.get("WIKI_ROOT", str(Path.home() / "wiki")))
    parser.add_argument("--notes-dir", required=True)
    parser.add_argument("--raw", action="append", default=[])
    parser.add_argument("--formal", action="append", default=[])
    parser.add_argument(
        "--min-body-bytes",
        type=int,
        default=500,
        help="minimum stripped body size for non-index formal pages",
    )
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
    formal_pages = list(dict.fromkeys(path.resolve() for path in formal_pages))
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
        coverage: dict[str, str] = {}
        if (notes_dir / "coverage-matrix.md").exists():
            coverage = validate_coverage(notes_dir, wiki_root, errors)
        validate_inventory_against_coverage(notes_dir, coverage, errors)
        validate_audit_handoff(notes_dir, errors)
        validate_durable_source_inventory(notes_dir, errors)

    for raw in raw_paths:
        if not raw.exists():
            errors.append(f"{raw}: raw source missing")
    for formal in formal_pages:
        if not formal.exists():
            errors.append(f"{formal}: formal page missing")
        else:
            validate_frontmatter(formal, errors)
    validate_formal_quality(formal_pages, errors, args.min_body_bytes)

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("llm-wiki-ingest contract OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
