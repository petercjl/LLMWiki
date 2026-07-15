#!/usr/bin/env python3
"""Audit LLM Wiki route signals for target pages."""

from __future__ import annotations

import argparse
import json
import platform
import re
import subprocess
from os import environ
from pathlib import Path


DEFAULT_WIKI = Path(environ.get("WIKI_ROOT", str(Path.home() / "wiki")))
WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)")


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
    proc = subprocess.run(cmd, text=True, capture_output=True)
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
        except json.JSONDecodeError:
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
    combined = "\n".join(part for part in [out, err] if part).strip()
    command_error = code != 0 or bool(re.search(r"(^|\n)\s*Error:", combined, re.IGNORECASE))
    available = not command_error
    active = out.splitlines()[-1] if available and out else ""
    return {
        "available": available,
        "active_vault_path": active,
        "vault_selector": selector or "",
        "target_wiki_path": str(wiki),
        "trusted": available and bool(active) and Path(active).expanduser() == wiki,
        "error": combined if command_error else "",
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
        unresolved["counts"] = cli_lines(obsidian_cmd(wiki, "unresolved", "counts"))[:100]
        global_signals["orphans_total"] = cli_lines(obsidian_cmd(wiki, "orphans", "total"))
        global_signals["deadends_total"] = cli_lines(obsidian_cmd(wiki, "deadends", "total"))
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
            backlinks = cli_lines(obsidian_cmd(wiki, "backlinks", f"path={rel}", "counts"))
            links = cli_lines(obsidian_cmd(wiki, "links", f"path={rel}"))
            outline = cli_lines(obsidian_cmd(wiki, "outline", f"path={rel}", "format=json"))
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
