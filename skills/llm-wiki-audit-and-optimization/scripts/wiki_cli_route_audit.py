#!/usr/bin/env python3
"""Audit LLM Wiki route signals for target pages."""

from __future__ import annotations

import argparse
import json
import platform
import re
import shutil
import subprocess
from os import environ
from pathlib import Path


DEFAULT_WIKI = Path(environ.get("WIKI_ROOT", str(Path.home() / "wiki")))
WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)")
EXCLUDED_DIRS = {".git", ".obsidian", "_meta", "raw", "audits", "attachments"}
EXCLUDED_FILES = {"AGENTS.md", "SCHEMA.md", "TOOLS.md", "log.md"}


def obsidian_config_candidates() -> list[Path]:
    override = environ.get("OBSIDIAN_CONFIG_PATH")
    if override:
        return [Path(override).expanduser()]
    home = Path.home()
    system = platform.system().lower()
    if system.startswith("darwin"):
        return [home / "Library/Application Support/obsidian/obsidian.json"]
    if system.startswith("windows"):
        bases = [environ.get("APPDATA"), environ.get("LOCALAPPDATA")]
        return [Path(base) / "Obsidian/obsidian.json" for base in bases if base]
    return [
        home / ".config/obsidian/obsidian.json",
        home / ".var/app/md.obsidian.Obsidian/config/obsidian/obsidian.json",
    ]


def run(cmd: list[str]) -> tuple[int, str, str]:
    try:
        proc = subprocess.run(cmd, text=True, capture_output=True)
    except OSError as exc:
        return 127, "", str(exc)
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def find_vault_selector(wiki: Path) -> str | None:
    """Return the Obsidian vault id for the target path when available.

    Obsidian CLI accepts the vault selector only as a global argument before the
    command, for example: `obsidian vault=<id> files total`.
    """
    if environ.get("OBSIDIAN_VAULT"):
        return environ["OBSIDIAN_VAULT"]
    for config_path in obsidian_config_candidates():
        if not config_path.exists():
            continue
        try:
            data = json.loads(config_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError, TypeError):
            continue
        for vault_id, info in data.get("vaults", {}).items():
            path = info.get("path")
            if path and Path(path).expanduser().resolve() == wiki:
                return vault_id
    return None


def obsidian_cmd(wiki: Path, *args: str) -> list[str]:
    selector = find_vault_selector(wiki)
    if selector:
        return ["obsidian", f"vault={selector}", *args]
    return ["obsidian", *args]


def cli_status(wiki: Path) -> dict:
    selector = find_vault_selector(wiki)
    code, out, err = run(obsidian_cmd(wiki, "vault", "info=path"))
    active = out.splitlines()[-1].strip().strip('"') if out else ""
    try:
        active_matches = bool(active) and Path(active).expanduser().resolve() == wiki.resolve()
    except OSError:
        active_matches = False
    return {
        "available": code == 0,
        "command_found": shutil.which("obsidian") is not None,
        "active_vault_path": active,
        "vault_selector": selector or "",
        "target_wiki_path": str(wiki),
        "trusted": code == 0 and active_matches,
        "error": err if code else "",
    }


def md_files(wiki: Path) -> list[Path]:
    return [
        p
        for p in wiki.rglob("*.md")
        if not any(part in EXCLUDED_DIRS or part.startswith(".") for part in p.relative_to(wiki).parts[:-1])
        and p.name not in EXCLUDED_FILES
    ]


def normalize_target(path: str) -> str:
    return path[:-3] if path.endswith(".md") else path


def filesystem_links(wiki: Path, rel: str) -> list[str]:
    p = wiki / rel
    if not p.exists():
        return []
    text = p.read_text(encoding="utf-8", errors="ignore")
    return sorted(set(WIKILINK_RE.findall(text)))


def link_candidates(wiki: Path, source_rel: str, link: str) -> list[Path]:
    """Return plausible Obsidian-style file candidates for one wikilink."""
    cleaned = link.strip().replace("\\", "/")
    if not cleaned:
        return []
    if cleaned.endswith(".md"):
        cleaned = cleaned[:-3]
    source_parent = (wiki / source_rel).parent
    if cleaned.startswith("../") or cleaned.startswith("./"):
        candidates = [source_parent / f"{cleaned}.md"]
    elif "/" in cleaned:
        candidates = [wiki / f"{cleaned}.md", source_parent / f"{cleaned}.md"]
    else:
        candidates = [source_parent / f"{cleaned}.md", wiki / f"{cleaned}.md"]
        global_matches = list(wiki.rglob(f"{cleaned}.md"))
        if len(global_matches) == 1:
            candidates.extend(global_matches)
    unique = []
    seen = set()
    for candidate in candidates:
        try:
            key = str(candidate.resolve())
        except OSError:
            key = str(candidate)
        if key not in seen:
            seen.add(key)
            unique.append(candidate)
    return unique


def resolve_wikilink(wiki: Path, source_rel: str, link: str) -> Path | None:
    for candidate in link_candidates(wiki, source_rel, link):
        if candidate.is_file():
            try:
                return candidate.resolve()
            except OSError:
                return candidate
    return None


def filesystem_unresolved(wiki: Path, rel: str) -> list[str]:
    unresolved = []
    for link in filesystem_links(wiki, rel):
        if resolve_wikilink(wiki, rel, link) is None:
            unresolved.append(link)
    return sorted(set(unresolved))


def filesystem_backlinks(wiki: Path, rel: str) -> list[str]:
    target_path = (wiki / rel).resolve()
    hits = []
    for p in md_files(wiki):
        text = p.read_text(encoding="utf-8", errors="ignore")
        links = WIKILINK_RE.findall(text)
        source_rel = str(p.relative_to(wiki)).replace("\\", "/")
        if any(resolve_wikilink(wiki, source_rel, link) == target_path for link in links):
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


def relative_target(wiki: Path, value: str) -> str:
    path = Path(value).expanduser()
    if path.is_absolute():
        try:
            return str(path.resolve().relative_to(wiki.resolve())).replace("\\", "/")
        except (OSError, ValueError):
            return value.replace("\\", "/")
    return value.replace("\\", "/").removeprefix("./")


def filesystem_global_signals(wiki: Path) -> dict:
    pages = md_files(wiki)
    rels = [str(p.relative_to(wiki)).replace("\\", "/") for p in pages]
    backlink_counts = {rel: 0 for rel in rels}
    deadends = []
    unresolved = {}
    for rel in rels:
        links = filesystem_links(wiki, rel)
        if not links:
            deadends.append(rel)
        missing = filesystem_unresolved(wiki, rel)
        if missing:
            unresolved[rel] = missing
        resolved_links = {resolve_wikilink(wiki, rel, link) for link in links}
        for target_rel in rels:
            if (wiki / target_rel).resolve() in resolved_links:
                backlink_counts[target_rel] += 1
    orphans = [rel for rel, count in backlink_counts.items() if count == 0 and rel != "index.md"]
    return {
        "markdown_pages_total": len(rels),
        "orphans_total": len(orphans),
        "orphan_pages": orphans[:100],
        "deadends_total": len(deadends),
        "deadend_pages": deadends[:100],
        "unresolved_links_total": sum(len(items) for items in unresolved.values()),
        "unresolved_links": unresolved,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", help="Wiki-relative markdown paths")
    parser.add_argument("--wiki", default=str(DEFAULT_WIKI))
    args = parser.parse_args()

    wiki = Path(args.wiki).expanduser().resolve()
    status = cli_status(wiki)

    global_signals = filesystem_global_signals(wiki)
    if status["trusted"]:
        global_signals["obsidian_unresolved_counts"] = cli_lines(
            obsidian_cmd(wiki, "unresolved", "counts")
        )[:100]
        global_signals["obsidian_orphans_total"] = cli_lines(
            obsidian_cmd(wiki, "orphans", "total")
        )
        global_signals["obsidian_deadends_total"] = cli_lines(
            obsidian_cmd(wiki, "deadends", "total")
        )
    else:
        global_signals["degraded_mode"] = "Obsidian CLI active vault does not match target wiki; used filesystem checks for target pages."

    reports = []
    warnings = []
    for value in args.paths:
        rel = relative_target(wiki, value)
        p = wiki / rel
        exists = p.exists()
        if status["trusted"]:
            backlinks = cli_lines(obsidian_cmd(wiki, "backlinks", f"path={rel}", "counts"))
            links = cli_lines(obsidian_cmd(wiki, "links", f"path={rel}"))
            outline = cli_lines(obsidian_cmd(wiki, "outline", f"path={rel}", "format=json"))
        else:
            backlinks = filesystem_backlinks(wiki, rel) if exists else []
            links = filesystem_links(wiki, rel) if exists else []
            outline = filesystem_outline(wiki, rel) if exists else []
        unresolved_links = filesystem_unresolved(wiki, rel) if exists else []

        page_warnings = []
        if not exists:
            page_warnings.append("target file does not exist")
        if exists and not backlinks and rel != "index.md":
            page_warnings.append("no backlinks found")
        if exists and not links:
            page_warnings.append("no outgoing wikilinks found")
        if exists and len(outline) <= 1:
            page_warnings.append("outline is thin or unavailable")
        if unresolved_links:
            page_warnings.append(f"{len(unresolved_links)} unresolved wikilink(s)")
        warnings.extend([f"{rel}: {w}" for w in page_warnings])
        reports.append({
            "path": rel,
            "exists": exists,
            "backlinks_count": len(backlinks),
            "backlinks": backlinks[:20],
            "outgoing_links_count": len(links),
            "outgoing_links": links[:50],
            "unresolved_links": unresolved_links[:50],
            "outline_count": len(outline),
            "outline_preview": outline[:20],
            "warnings": page_warnings,
        })

    result = {
        "target_paths": args.paths,
        "cli_status": status,
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
