#!/usr/bin/env python3
"""Print a lightweight structural inventory for text/Markdown sources."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    args = parser.parse_args()

    path = Path(args.path)
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    headings = []
    code_blocks = 0
    table_lines = 0
    in_code = False
    links = set()

    for line_no, line in enumerate(lines, start=1):
        if line.startswith("```"):
            code_blocks += 0 if in_code else 1
            in_code = not in_code
        if not in_code:
            match = re.match(r"^(#{1,6})\s+(.+)$", line)
            if match:
                headings.append((line_no, len(match.group(1)), match.group(2).strip()))
            if line.strip().startswith("|") and line.strip().endswith("|"):
                table_lines += 1
        for url in re.findall(r"https?://[^\s)>\]]+", line):
            links.add(url)

    print(f"path: {path}")
    print(f"lines: {len(lines)}")
    print(f"headings: {len(headings)}")
    for line_no, depth, title in headings:
        print(f"  H{depth} L{line_no}: {title}")
    print(f"code_blocks: {code_blocks}")
    print(f"table_lines: {table_lines}")
    print(f"links: {len(links)}")
    for url in sorted(links):
        print(f"  {url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
