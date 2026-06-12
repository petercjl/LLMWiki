#!/usr/bin/env python3
"""Summarize LLM Wiki health signals from Obsidian CLI or filesystem fallback."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


DEFAULT_WIKI = Path("/Users/pechen/wiki")


def run(cmd: list[str]) -> tuple[int, str, str]:
    proc = subprocess.run(cmd, text=True, capture_output=True)
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wiki", default=str(DEFAULT_WIKI))
    args = parser.parse_args()
    wiki = Path(args.wiki).expanduser().resolve()

    code, out, err = run(["obsidian", "vault", "info=path"])
    active = out.splitlines()[-1] if out else ""
    trusted = code == 0 and Path(active).expanduser() == wiki
    result = {
        "wiki": str(wiki),
        "cli": {
            "available": code == 0,
            "active_vault_path": active,
            "trusted": trusted,
            "error": err if code else "",
        },
        "filesystem": {
            "markdown_files": len(list(wiki.rglob("*.md"))) if wiki.exists() else 0,
            "directories": sum(1 for p in wiki.rglob("*") if p.is_dir()) if wiki.exists() else 0,
        },
        "obsidian": {},
    }
    if trusted:
        for key, cmd in {
            "files_total": ["obsidian", "files", "total"],
            "folders_total": ["obsidian", "folders", "total"],
            "unresolved_total": ["obsidian", "unresolved", "total"],
            "orphans_total": ["obsidian", "orphans", "total"],
            "deadends_total": ["obsidian", "deadends", "total"],
            "tasks_total": ["obsidian", "tasks", "total"],
        }.items():
            c, o, e = run(cmd)
            result["obsidian"][key] = o if c == 0 else {"error": e}
    else:
        result["obsidian"]["degraded_mode"] = "Active Obsidian vault does not match target wiki."
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
