#!/usr/bin/env python3
"""Archive an EPUB into a raw book source directory."""

from __future__ import annotations

import argparse
import json
import shutil
import zipfile
from datetime import date
from pathlib import Path

from book_epub_utils import html_to_text, inspect_epub, read_zip_text, slugify, write_json


def md_escape_cell(value: object) -> str:
    return str(value or "").replace("|", "\\|").replace("\n", " ")


def write_metadata_md(out_dir: Path, profile: dict) -> None:
    meta = profile.get("metadata", {})
    lines = [
        "# Book Metadata",
        "",
        f"- Title: {meta.get('title', '')}",
        f"- Creator: {meta.get('creator', '')}",
        f"- Publisher: {meta.get('publisher', '')}",
        f"- Publication date: {meta.get('date', '')}",
        f"- Language: {meta.get('language', '')}",
        f"- ISBN: {meta.get('isbn', '')}",
        f"- Source path: {profile.get('source_path', '')}",
        f"- SHA256: {profile.get('sha256', '')}",
        f"- Imported: {date.today().isoformat()}",
        "",
        "## Counts",
        "",
    ]
    for key, value in profile.get("counts", {}).items():
        lines.append(f"- {key}: {value}")
    lines.append("")
    out_dir.joinpath("metadata.md").write_text("\n".join(lines), encoding="utf-8")


def write_toc_md(out_dir: Path, profile: dict) -> None:
    lines = ["# Table of Contents", "", "| order | depth | title | file |", "| ---: | ---: | --- | --- |"]
    for idx, item in enumerate(profile.get("toc", []), 1):
        indent_title = ("  " * max(0, int(item.get("depth") or 1) - 1)) + str(item.get("title", ""))
        lines.append(
            f"| {idx} | {item.get('depth', '')} | {md_escape_cell(indent_title)} | `{md_escape_cell(item.get('file', ''))}` |"
        )
    lines.append("")
    out_dir.joinpath("toc.md").write_text("\n".join(lines), encoding="utf-8")


def write_manifest_md(out_dir: Path, profile: dict) -> None:
    lines = [
        "# EPUB Manifest Summary",
        "",
        f"- OPF path: `{profile.get('opf_path', '')}`",
        f"- NCX path: `{profile.get('ncx_path', '')}`",
        f"- ZIP file count: {profile.get('zip_file_count', '')}",
        "",
        "## HTML Files",
        "",
    ]
    for path in profile.get("html_files", []):
        lines.append(f"- `{path}`")
    lines += ["", "## Image Files", ""]
    for path in profile.get("image_files", []):
        lines.append(f"- `{path}`")
    lines.append("")
    out_dir.joinpath("manifest.md").write_text("\n".join(lines), encoding="utf-8")


def toc_title_by_file(profile: dict) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for item in profile.get("toc", []):
        file_path = item.get("file", "")
        title = item.get("title", "")
        if file_path and title and file_path not in mapping:
            mapping[file_path] = title
    return mapping


def extract_chapters(epub_path: Path, out_dir: Path, profile: dict) -> list[dict]:
    chapters_dir = out_dir / "chapters"
    chapters_dir.mkdir(parents=True, exist_ok=True)
    title_map = toc_title_by_file(profile)
    spine_html = [
        item.get("path")
        for item in profile.get("spine", [])
        if item.get("media_type") in {"application/xhtml+xml", "text/html"}
    ]
    if not spine_html:
        spine_html = profile.get("html_files", [])

    rows: list[dict] = []
    with zipfile.ZipFile(epub_path) as zf:
        for idx, internal_path in enumerate(spine_html, 1):
            if not internal_path:
                continue
            markup = read_zip_text(zf, internal_path)
            text, heading = html_to_text(markup)
            title = title_map.get(internal_path) or heading or f"Chapter {idx}"
            source_id = f"ch{idx:03d}"
            file_name = f"{source_id}-{slugify(title, 'chapter')}.md"
            out_path = chapters_dir / file_name
            content = [
                "---",
                f"source_id: {source_id}",
                f"source_file: {internal_path}",
                f"title: {json.dumps(title, ensure_ascii=False)}",
                "---",
                "",
                f"# {title}",
                "",
                text.strip(),
                "",
            ]
            out_path.write_text("\n".join(content), encoding="utf-8")
            rows.append(
                {
                    "source_id": source_id,
                    "title": title,
                    "source_file": internal_path,
                    "chapter_file": str(out_path.relative_to(out_dir)),
                    "char_count": len(text),
                }
            )
    write_json(out_dir / "chapters.json", rows)
    return rows


def extract_assets(epub_path: Path, out_dir: Path, profile: dict) -> None:
    assets_dir = out_dir / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(epub_path) as zf:
        for image_path in profile.get("image_files", []):
            target = assets_dir / Path(image_path).name
            target.write_bytes(zf.read(image_path))


def main() -> int:
    parser = argparse.ArgumentParser(description="Archive EPUB source files for LLM Wiki ingestion.")
    parser.add_argument("epub", type=Path, help="Path to .epub file")
    parser.add_argument("--output-dir", required=True, type=Path, help="Raw book output directory")
    parser.add_argument("--force", action="store_true", help="Overwrite generated helper files if output exists")
    parser.add_argument("--extract-assets", action="store_true", help="Extract image assets into assets/")
    args = parser.parse_args()

    epub_path = args.epub.expanduser().resolve()
    out_dir = args.output_dir.expanduser()
    if out_dir.exists() and any(out_dir.iterdir()) and not args.force:
        raise SystemExit(f"Output directory is not empty: {out_dir}. Use --force to overwrite helper files.")
    out_dir.mkdir(parents=True, exist_ok=True)

    profile = inspect_epub(epub_path)
    shutil.copy2(epub_path, out_dir / "source.epub")
    write_json(out_dir / "source-profile.json", profile)
    write_metadata_md(out_dir, profile)
    write_toc_md(out_dir, profile)
    write_manifest_md(out_dir, profile)
    chapters = extract_chapters(epub_path, out_dir, profile)
    if args.extract_assets:
        extract_assets(epub_path, out_dir, profile)

    print(f"Archived EPUB: {out_dir}")
    print(f"Chapters extracted: {len(chapters)}")
    print(f"Images listed: {profile.get('counts', {}).get('image_files', 0)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
