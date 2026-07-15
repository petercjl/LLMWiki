#!/usr/bin/env python3
"""Build an LLM Wiki query pack using Obsidian CLI when available."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from pathlib import Path


DEFAULT_WIKI = Path(os.environ.get("WIKI_ROOT", str(Path.home() / "wiki")))


def run(cmd: list[str]) -> tuple[int, str, str]:
    try:
        proc = subprocess.run(cmd, text=True, capture_output=True)
    except OSError as exc:
        return 127, "", str(exc)
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


def obsidian_search(query: str, path: str | None, limit: int) -> list[str]:
    cmd = ["obsidian", "search", f"query={query}", f"limit={limit}", "format=json"]
    if path:
        cmd.append(f"path={path}")
    code, out, _ = run(cmd)
    if code != 0 or not out:
        return []
    try:
        data = json.loads(out)
        return [str(x) for x in data]
    except json.JSONDecodeError:
        return [line for line in out.splitlines() if line.strip()]


def filesystem_search(wiki: Path, query: str, path: str | None, limit: int) -> list[str]:
    base = wiki / path if path else wiki
    if not base.exists():
        return []
    terms = [t for t in query.split() if t]
    if not terms:
        return []
    scores: dict[Path, int] = {}
    if shutil.which("rg"):
        for term in terms:
            cmd = ["rg", "-l", "--glob", "*.md", term, str(base)]
            code, out, _ = run(cmd)
            if code not in {0, 1}:
                continue
            for abs_path in out.splitlines():
                p = Path(abs_path)
                scores[p] = scores.get(p, 0) + 1
    else:
        lowered_terms = [term.casefold() for term in terms]
        for candidate in base.rglob("*.md"):
            try:
                text = candidate.read_text(encoding="utf-8", errors="ignore").casefold()
            except OSError:
                continue
            score = sum(1 for term in lowered_terms if term in text)
            if score:
                scores[candidate] = score
    ranked = sorted(scores, key=lambda p: (-scores[p], len(str(p)), str(p)))
    return [str(p.relative_to(wiki)) for p in ranked[:limit]]


def unique(items: list[str]) -> list[str]:
    seen = set()
    out = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("query", help="User question or search keywords")
    parser.add_argument("--wiki", default=str(DEFAULT_WIKI))
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()

    wiki = Path(args.wiki).expanduser().resolve()
    status = cli_status(wiki)
    search = obsidian_search if status["trusted"] else lambda q, p, l: filesystem_search(wiki, q, p, l)

    query = args.query
    pack = {
        "query": query,
        "cli_status": status,
        "queries": search(query, "queries", args.limit),
        "agent_templates": unique(
            search(f"Agent 使用模板 {query}", None, args.limit)
            + search(f"agent-usage-template {query}", None, args.limit)
        ),
        "indexes": unique(
            [p for p in search(query, "domains", args.limit) if p.endswith("index.md")]
            + [p for p in search(query, "projects", args.limit) if p.endswith("index.md")]
            + [p for p in search(query, "shared", args.limit) if p.endswith("index.md")]
        ),
        "detail_pages": unique(search(query, "domains", args.limit) + search(query, "shared", args.limit)),
    }
    read_order = unique(pack["queries"] + pack["agent_templates"] + pack["indexes"] + pack["detail_pages"])
    pack["recommended_read_order"] = read_order[: min(len(read_order), args.limit)]
    pack["route_notes"] = [
        "Preferred order: query pages, Agent usage templates, indexes, then detail pages.",
        "CLI results are trusted only when active_vault_path equals target_wiki_path.",
    ]

    print(json.dumps(pack, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
