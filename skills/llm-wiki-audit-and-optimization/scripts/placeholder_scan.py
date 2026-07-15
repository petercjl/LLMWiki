#!/usr/bin/env python3
"""
placeholder_scan.py — mechanical compile-shell detector for an LLM Wiki.

Scans a directory of markdown knowledge pages and flags "compile shells":
pages that look ingested (title, frontmatter, agent-template scaffold) but whose
body is template boilerplate with the real knowledge missing.

This is the highest-ROI first step of an LLM Wiki compile audit, because human
reading samples a few pages and is fooled by good titles/structure, while this
diff-based scan inspects 100% of pages in seconds and catches the exact thing
sampling misses — e.g. a whole learning path where every chapter body is a clone
of the same placeholder.

Usage:
    python3 placeholder_scan.py <target_dir> [--min-bytes 500] [--json]

Verdicts per page:
    SHELL  — duplicate body shared with other pages, OR contains known boilerplate
    THIN   — formal (non-index) page whose stripped body is below --min-bytes
    OK     — passes the mechanical checks (still needs human depth audit)

Raw sources, extraction metadata, audit reports, hidden application folders, and
root operating files are excluded by default so a whole-Wiki scan measures formal
knowledge rather than internal working notes.

Exit code is 0 always; this is a diagnostic, not a gate. Parse the output.
"""
import argparse
import hashlib
import json
import os
import re
import sys
from collections import defaultdict


EXCLUDED_DIRS = {
    ".git",
    ".obsidian",
    "_meta",
    "raw",
    "audits",
    "attachments",
}
EXCLUDED_FILES = {
    "AGENTS.md",
    "SCHEMA.md",
    "TOOLS.md",
    "log.md",
}

# Boilerplate / scaffold phrases that must NOT survive into a real formal page.
# Keep these UNAMBIGUOUS: each must be a marker that would never appear in real
# knowledge prose. Bare words like 占位 / TODO are intentionally excluded because
# they collide with legitimate content (e.g. 心智占位 "occupy mind-share"). Extend
# these lists as new ingest templates are discovered.
#
# CJK markers: plain substring match (CJK has no word boundaries). Each must be a
# multi-char marker form that would not appear inside real prose.
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

# ASCII markers: matched on WORD BOUNDARIES via regex, so e.g. "TBD" does not fire
# inside "JTBD" and "TODO" does not fire inside a longer token. \b works for ASCII.
BOILERPLATE_ASCII = [
    r"TODO[:：]",
    r"\bTBD\b",
    r"<!--\s*placeholder",
    r"\bLorem ipsum\b",
]
_ASCII_RE = re.compile("|".join(BOILERPLATE_ASCII), re.IGNORECASE)


def find_boilerplate(raw: str):
    """Return list of boilerplate markers present in raw text."""
    hits = [p for p in BOILERPLATE_CJK if p in raw]
    hits += sorted(set(m.group(0) for m in _ASCII_RE.finditer(raw)))
    return hits

FRONTMATTER_RE = re.compile(r"^---\n.*?\n---\n", re.DOTALL)
HEADING_RE = re.compile(r"^#{1,6}\s.*$", re.MULTILINE)
WS_RE = re.compile(r"\s+")


def strip_to_body(text: str) -> str:
    """Remove frontmatter and all heading lines, leaving substantive prose."""
    text = FRONTMATTER_RE.sub("", text, count=1)
    text = HEADING_RE.sub("", text)
    return text.strip()


def normalize(body: str) -> str:
    """Whitespace-collapsed form for duplicate-body fingerprinting."""
    return WS_RE.sub(" ", body).strip()


def is_index_page(path: str) -> bool:
    name = os.path.basename(path).lower()
    return name in ("index.md", "readme.md") or name.endswith("/index.md")


def scan(target_dir: str, min_bytes: int):
    pages = []
    for root, dirs, files in os.walk(target_dir):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS and not d.startswith(".")]
        for fn in sorted(files):
            if not fn.endswith(".md") or fn in EXCLUDED_FILES:
                continue
            full = os.path.join(root, fn)
            try:
                raw = open(full, encoding="utf-8").read()
            except Exception as e:  # noqa: BLE001
                pages.append({"path": full, "error": str(e)})
                continue
            body = strip_to_body(raw)
            norm = normalize(body)
            body_hash = hashlib.sha1(norm.encode("utf-8")).hexdigest()[:12] if norm else "EMPTY"
            hits = find_boilerplate(raw)
            pages.append({
                "path": full,
                "rel": os.path.relpath(full, target_dir),
                "total_bytes": len(raw.encode("utf-8")),
                "body_bytes": len(body.encode("utf-8")),
                "body_hash": body_hash,
                "boilerplate_hits": hits,
                "is_index": is_index_page(full),
            })

    # group by normalized-body hash to find duplicate bodies (template clones)
    groups = defaultdict(list)
    for p in pages:
        if "error" in p:
            continue
        if p["body_hash"] not in ("EMPTY",):
            groups[p["body_hash"]].append(p)
    dup_groups = {h: ps for h, ps in groups.items() if len(ps) > 1}
    dup_hash_to_id = {h: i + 1 for i, h in enumerate(sorted(dup_groups))}

    # assign verdicts
    for p in pages:
        if "error" in p:
            p["verdict"] = "ERROR"
            continue
        dup_id = dup_hash_to_id.get(p["body_hash"])
        p["dup_group"] = dup_id
        if p["body_hash"] == "EMPTY" or p["boilerplate_hits"] or dup_id is not None:
            p["verdict"] = "SHELL"
        elif (not p["is_index"]) and p["body_bytes"] < min_bytes:
            p["verdict"] = "THIN"
        else:
            p["verdict"] = "OK"

    return pages, dup_groups, dup_hash_to_id


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target_dir")
    ap.add_argument("--min-bytes", type=int, default=500,
                    help="formal pages with stripped body below this are THIN (default 500)")
    ap.add_argument("--json", action="store_true", help="emit JSON instead of text table")
    args = ap.parse_args()

    if not os.path.isdir(args.target_dir):
        print(f"ERROR: not a directory: {args.target_dir}", file=sys.stderr)
        sys.exit(2)

    pages, dup_groups, dup_hash_to_id = scan(args.target_dir, args.min_bytes)

    if args.json:
        print(json.dumps({
            "target": args.target_dir,
            "pages": pages,
            "duplicate_groups": {
                str(dup_hash_to_id[h]): [p["rel"] for p in ps]
                for h, ps in dup_groups.items()
            },
        }, ensure_ascii=False, indent=2))
        return

    shells = [p for p in pages if p.get("verdict") == "SHELL"]
    thins = [p for p in pages if p.get("verdict") == "THIN"]
    oks = [p for p in pages if p.get("verdict") == "OK"]

    print(f"Scanned: {len(pages)} markdown pages under {args.target_dir}")
    print(f"  SHELL: {len(shells)}   THIN: {len(thins)}   OK: {len(oks)}")
    print()

    if dup_groups:
        print("=== DUPLICATE-BODY GROUPS (template clones — P0) ===")
        for h, ps in sorted(dup_groups.items(), key=lambda kv: dup_hash_to_id[kv[0]]):
            print(f"  group {dup_hash_to_id[h]}: {len(ps)} pages share one body")
            for p in ps:
                print(f"      {p['rel']}")
        print()

    if shells or thins:
        print("=== FLAGGED PAGES ===")
        print(f"  {'verdict':7} {'body_B':>7} {'dup':>3}  page")
        for p in shells + thins:
            dup = p.get("dup_group") or "-"
            tag = " ".join(p["boilerplate_hits"])[:30]
            print(f"  {p['verdict']:7} {p['body_bytes']:>7} {str(dup):>3}  {p['rel']}"
                  + (f"   [{tag}]" if tag else ""))
        print()

    if shells:
        print("VERDICT: compile-placeholder shells present — treat as P0. "
              "Recompile from raw sources before scoring routing/reasoning.")
    elif thins:
        print("VERDICT: no duplicate shells, but THIN pages exist — review depth manually.")
    else:
        print("VERDICT: no mechanical shells detected. Proceed to human depth audit.")


if __name__ == "__main__":
    main()
