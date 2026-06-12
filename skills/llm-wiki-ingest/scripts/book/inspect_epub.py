#!/usr/bin/env python3
"""Inspect an EPUB and emit source-profile JSON."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from book_epub_utils import inspect_epub, write_json


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect EPUB metadata, spine, toc, and assets.")
    parser.add_argument("epub", type=Path, help="Path to .epub file")
    parser.add_argument("--output", type=Path, help="Write JSON profile to this path")
    args = parser.parse_args()

    profile = inspect_epub(args.epub.expanduser().resolve())
    if args.output:
        write_json(args.output.expanduser(), profile)
    else:
        print(json.dumps(profile, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
