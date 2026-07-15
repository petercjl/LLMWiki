#!/usr/bin/env python3
"""Build a read-only query pack for a Markdown LLM Wiki.

The helper is deliberately Python-standard-library only. It does not require
Obsidian CLI, ripgrep, Git, a database, or network access.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path


FORMAL_ROOTS = (
    "queries",
    "domains",
    "shared",
    "projects",
    "concepts",
    "comparisons",
    "entities",
    "decisions",
)
SKIP_PARTS = {"raw", ".obsidian", ".git", "_archive", "node_modules", "__pycache__"}
ASCII_WORD = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.+-]+")
CJK_RUN = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff]{2,}")
WIKILINK = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]")
COMMON_CJK = {
    "一个", "一下", "什么", "怎么", "怎样", "如何", "可以", "应该", "需要",
    "我的", "我们", "里面", "知识库", "帮我", "请从", "找到", "简单", "分别",
    "只查询", "不要", "修改", "给我", "当前", "这个", "那个", "相关", "注意",
}
FILLER_PHRASES = (
    "不要修改知识库", "请从我的知识库里找一下", "从我的知识库里找一下",
    "请从知识库里找一下", "从知识库里找一下", "给我一个简单的", "分别应该注意什么",
    "应该注意什么", "帮我整理成", "我准备做一条", "准备做一条", "请帮我", "帮我",
    "我的知识库", "知识库", "找一下", "给我", "一个", "简单的", "先只查询",
    "只查询", "不要修改", "请", "我", "里",
)


def load_config_root() -> Path | None:
    config_path = Path.home() / ".llmwiki" / "config.json"
    if not config_path.is_file():
        return None
    try:
        data = json.loads(config_path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return None
    value = data.get("WIKI_ROOT") or data.get("wiki_root")
    return Path(str(value)).expanduser() if value else None


def default_wiki() -> Path:
    env = os.environ.get("WIKI_ROOT")
    if env:
        return Path(env).expanduser()
    return load_config_root() or (Path.home() / "wiki")


def valid_wiki(wiki: Path) -> bool:
    return wiki.is_dir() and all((wiki / name).is_file() for name in ("SCHEMA.md", "index.md", "log.md"))


def query_terms(query: str) -> list[str]:
    terms: list[str] = []
    for term in ASCII_WORD.findall(query.lower()):
        if len(term) >= 2:
            terms.append(term)
    for run in CJK_RUN.findall(query):
        cleaned = run
        for filler in FILLER_PHRASES:
            cleaned = cleaned.replace(filler, " ")
        for segment in re.split(r"[\s和与及并]+", cleaned):
            if len(segment) < 2 or segment in COMMON_CJK:
                continue
            if len(segment) <= 16:
                terms.append(segment)
            for size in (4, 3, 2):
                if len(segment) < size:
                    continue
                for i in range(len(segment) - size + 1):
                    phrase = segment[i : i + size]
                    if phrase not in COMMON_CJK:
                        terms.append(phrase)
    return unique(terms)


def unique(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def formal_markdown(wiki: Path) -> list[Path]:
    pages: list[Path] = []
    for root_name in FORMAL_ROOTS:
        root = wiki / root_name
        if not root.is_dir():
            continue
        for path in root.rglob("*.md"):
            rel = path.relative_to(wiki)
            if not any(part in SKIP_PARTS for part in rel.parts):
                pages.append(path)
    for name in ("index.md", "SCHEMA.md"):
        path = wiki / name
        if path.is_file():
            pages.append(path)
    return sorted(set(pages), key=lambda p: p.as_posix())


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8-sig", errors="replace")
    except OSError:
        return ""


def score(path: Path, wiki: Path, terms: list[str]) -> int:
    rel = path.relative_to(wiki).as_posix().lower()
    name = path.stem.lower()
    text = read_text(path).lower()
    value = 0
    for term in terms:
        t = term.lower()
        if t in name:
            value += 12 + min(len(t), 6)
        if t in rel:
            value += 5
        count = text.count(t)
        if count:
            value += min(count, 5) * (2 if len(t) >= 3 else 1)
    if value and rel.startswith("queries/"):
        value += 35
    if value and path.name.lower() == "index.md":
        value += 5
    return value


def ranked(
    pages: list[Path],
    wiki: Path,
    terms: list[str],
    limit: int,
    relative_cutoff: float = 0.0,
) -> list[str]:
    scored = [(score(path, wiki, terms), path) for path in pages]
    scored = [(value, path) for value, path in scored if value > 0]
    scored.sort(key=lambda item: (-item[0], len(item[1].as_posix()), item[1].as_posix()))
    if scored and relative_cutoff:
        minimum = scored[0][0] * relative_cutoff
        scored = [(value, path) for value, path in scored if value >= minimum]
    return [path.relative_to(wiki).as_posix() for _, path in scored[:limit]]


def resolve_wikilink(wiki: Path, source: Path, target: str) -> str | None:
    clean = target.strip().replace("\\", "/")
    candidates = [wiki / clean, source.parent / clean]
    if not clean.lower().endswith(".md"):
        candidates.extend([wiki / f"{clean}.md", source.parent / f"{clean}.md"])
    for candidate in candidates:
        try:
            resolved = candidate.resolve()
            resolved.relative_to(wiki)
        except (OSError, ValueError):
            continue
        if resolved.is_file() and resolved.suffix.lower() == ".md":
            return resolved.relative_to(wiki).as_posix()
    return None


def linked_pages(wiki: Path, routes: list[str], limit: int) -> list[str]:
    result: list[str] = []
    for rel in routes:
        source = wiki / rel
        for target in WIKILINK.findall(read_text(source)):
            resolved = resolve_wikilink(wiki, source, target)
            if resolved:
                result.append(resolved)
            if len(unique(result)) >= limit:
                return unique(result)
    return unique(result)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a read-only Markdown Wiki query pack")
    parser.add_argument("query", help="User question or search phrase")
    parser.add_argument("--wiki", default=str(default_wiki()), help="Wiki root")
    parser.add_argument("--limit", type=int, default=20, help="Maximum read-order items")
    args = parser.parse_args()

    wiki = Path(args.wiki).expanduser().resolve()
    if not valid_wiki(wiki):
        print(json.dumps({
            "status": "error",
            "error": "invalid-wiki-root",
            "wiki_root": str(wiki),
            "required": ["SCHEMA.md", "index.md", "log.md"],
        }, ensure_ascii=False, indent=2))
        return 2

    terms = query_terms(args.query)
    pages = formal_markdown(wiki)
    query_pages = ranked(
        [p for p in pages if p.relative_to(wiki).parts[0] == "queries"],
        wiki,
        terms,
        5,
        relative_cutoff=0.75,
    )
    templates = ranked([p for p in pages if "usage-template" in p.name.lower() or "使用模板" in read_text(p)], wiki, terms, 5)
    indexes = ranked(
        [p for p in pages if p.name.lower() == "index.md"],
        wiki,
        terms,
        10,
        relative_cutoff=0.45,
    )
    details = ranked([
        p for p in pages
        if p.relative_to(wiki).parts[0] not in {"queries"} and p.name.lower() not in {"index.md", "schema.md"}
    ], wiki, terms, args.limit, relative_cutoff=0.35)
    route_sources = query_pages + templates if query_pages or templates else indexes[:2]
    links = linked_pages(wiki, route_sources, args.limit)
    read_order = unique(query_pages + templates + links + indexes + details)[: args.limit]

    status = "ok" if read_order else "no-match"
    pack = {
        "status": status,
        "query": args.query,
        "wiki_root": str(wiki),
        "backend": "python-stdlib",
        "search_terms": terms,
        "query_pages": query_pages,
        "agent_templates": templates,
        "indexes": indexes,
        "linked_pages": links,
        "detail_pages": details,
        "recommended_read_order": read_order,
        "route_notes": [
            "Read query pages and their required links before broad indexes or detail pages.",
            "Search covers formal Markdown only; raw evidence is excluded by default.",
        ],
    }
    print(json.dumps(pack, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
