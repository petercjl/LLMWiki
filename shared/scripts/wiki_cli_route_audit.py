#!/usr/bin/env python3
"""Audit LLM Wiki route signals for target pages."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path


DEFAULT_WIKI = Path("/Users/pechen/wiki")
WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)")


def run(cmd: list[str]) -> tuple[int, str, str]:
    proc = subprocess.run(cmd, text=True, capture_output=True)
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def cli_status(wiki: Path) -> dict:
    code, out, err = run(["obsidian", "vault", "info=path"])
    active = out.splitlines()[-1] if out else ""
    return {
        "available": code == 0,
        "active_vault_path": active,
        "target_wiki_path": str(wiki),
        "trusted": code == 0 and Path(active).expanduser() == wiki,
        "error": err if code else "",
    }


def md_files(wiki: Path) -> list[Path]:
    return [p for p in wiki.rglob("*.md") if ".git" not in p.parts]


def normalize_target(path: str) -> str:
    return path[:-3] if path.endswith(".md") else path


def filesystem_links(wiki: Path, rel: str) -> list[str]:
    p = wiki / rel
    if not p.exists():
        return []
    text = p.read_text(encoding="utf-8", errors="ignore")
    return sorted(set(WIKILINK_RE.findall(text)))


def filesystem_backlinks(wiki: Path, rel: str) -> list[str]:
    target = normalize_target(rel)
    target_name = Path(target).name
    hits = []
    for p in md_files(wiki):
        text = p.read_text(encoding="utf-8", errors="ignore")
        links = WIKILINK_RE.findall(text)
        if any(link == target or link.endswith("/" + target_name) or link == target_name for link in links):
            hits.append(str(p.relative_to(wiki)))
    return sorted(set(hits))


def filesystem_outline(wiki: Path, rel: str) -> list[str]:
    p = wiki / rel
    if not p.exists():
        return []
    headings = []
    for line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
        if line.startswith("#"):
            headings.append(line.strip())
    return headings


def cli_lines(cmd: list[str]) -> list[str]:
    code, out, _ = run(cmd)
    if code != 0 or not out:
        return []
    return [line for line in out.splitlines() if line.strip()]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", help="Wiki-relative markdown paths")
    parser.add_argument("--wiki", default=str(DEFAULT_WIKI))
    args = parser.parse_args()

    wiki = Path(args.wiki).expanduser().resolve()
    status = cli_status(wiki)

    unresolved = {}
    global_signals = {}
    if status["trusted"]:
        unresolved["counts"] = cli_lines(["obsidian", "unresolved", "counts"])[:100]
        global_signals["orphans_total"] = cli_lines(["obsidian", "orphans", "total"])
        global_signals["deadends_total"] = cli_lines(["obsidian", "deadends", "total"])
    else:
        unresolved["counts"] = []
        global_signals["degraded_mode"] = "Obsidian CLI active vault does not match target wiki; used filesystem checks for target pages."

    reports = []
    warnings = []
    for rel in args.paths:
        rel = rel.removeprefix(str(wiki) + "/")
        p = wiki / rel
        exists = p.exists()
        if status["trusted"]:
            backlinks = cli_lines(["obsidian", "backlinks", f"path={rel}", "counts"])
            links = cli_lines(["obsidian", "links", f"path={rel}"])
            outline = cli_lines(["obsidian", "outline", f"path={rel}", "format=json"])
        else:
            backlinks = filesystem_backlinks(wiki, rel) if exists else []
            links = filesystem_links(wiki, rel) if exists else []
            outline = filesystem_outline(wiki, rel) if exists else []

        page_warnings = []
        if not exists:
            page_warnings.append("target file does not exist")
        if exists and not backlinks:
            page_warnings.append("no backlinks found")
        if exists and not links:
            page_warnings.append("no outgoing wikilinks found")
        if exists and len(outline) <= 1:
            page_warnings.append("outline is thin or unavailable")
        warnings.extend([f"{rel}: {w}" for w in page_warnings])
        reports.append({
            "path": rel,
            "exists": exists,
            "backlinks_count": len(backlinks),
            "backlinks": backlinks[:20],
            "outgoing_links_count": len(links),
            "outgoing_links": links[:50],
            "outline_count": len(outline),
            "outline_preview": outline[:20],
            "warnings": page_warnings,
        })

    result = {
        "target_paths": args.paths,
        "cli_status": status,
        "unresolved_summary": unresolved,
        "global_signals": global_signals,
        "target_reports": reports,
        "warnings": warnings,
        "recommended_fixes": [
            "Add target pages to relevant index/query/template pages when backlinks are missing.",
            "Add outgoing wikilinks to related concepts, evidence, or Agent usage templates when dead-end signals appear.",
            "Run compile audit separately if route signals pass but content quality is uncertain.",
        ],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
