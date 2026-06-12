#!/usr/bin/env python3
"""Install the source repo's published LLM Wiki skills into Codex."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


DEFAULT_CODEX_SKILLS = Path("/Users/pechen/.codex/skills")
PUBLISHED = {
    "llm-wiki",
    "llm-wiki-ingest",
    "llm-wiki-audit-and-optimization",
    "llm-wiki-recompile-runner",
    "ai-agent-skill-registry-sync",
}
OBSOLETE = {
    "api-docs-wiki-ingest",
    "wiki-clippings-ingest",
    "book-to-llm-wiki",
    "course-transcript-to-knowledge",
}


def copytree(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default=str(Path(__file__).resolve().parents[2]))
    parser.add_argument("--codex-skills", default=str(DEFAULT_CODEX_SKILLS))
    parser.add_argument("--delete-obsolete", action="store_true")
    args = parser.parse_args()

    source = Path(args.source).resolve()
    codex = Path(args.codex_skills).resolve()
    source_skills = source / "skills"
    for name in sorted(PUBLISHED):
        src = source_skills / name
        if not src.exists():
            raise SystemExit(f"missing published skill: {src}")
        copytree(src, codex / name)
        print(f"installed {name}")
    if args.delete_obsolete:
        for name in sorted(OBSOLETE):
            path = codex / name
            if path.exists():
                shutil.rmtree(path)
                print(f"deleted obsolete {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
