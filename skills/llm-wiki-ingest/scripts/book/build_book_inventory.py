#!/usr/bin/env python3
"""Build a mechanical chapter inventory from an extracted raw book directory."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from book_epub_utils import write_json


KEYWORD_GROUPS = {
    "positioning-selection": ["定位", "选品", "类目", "人群", "需求", "卖点", "爆款", "新品"],
    "search-keywords": ["标题", "搜索", "关键词", "权重", "排名", "生意参谋"],
    "visual-conversion": ["主图", "详情页", "图片", "美工", "点击率", "转化率", "卖点策划"],
    "paid-channel": ["直通车", "钻展", "淘客", "直播", "达人", "内容营销", "推广", "渠道"],
    "customer-service": ["客服", "老客户", "复购", "售前", "售后", "服务", "微信"],
    "promotion-pricing": ["促销", "大促", "双11", "定价", "价格战", "优惠"],
    "supply-finance": ["供应链", "仓库", "发货", "财务", "成本", "库存"],
    "team-organization": ["招聘", "团队", "绩效", "管理", "文化", "人才", "股权"],
    "strategy-mindset": ["军规", "亲力亲为", "专注", "创新", "品牌", "风险", "成功密码"],
}

CASE_PATTERNS = [
    "淘宝",
    "天猫",
    "iPhone",
    "苹果",
    "可口可乐",
    "王老吉",
    "脑白金",
    "江小白",
    "香飘飘",
    "加多宝",
    "Facebook",
    "谷歌",
    "阿里巴巴",
    "腾讯",
    "小米",
]

TOOL_METRIC_PATTERNS = [
    "直通车",
    "钻展",
    "淘客",
    "生意参谋",
    "搜索",
    "点击率",
    "转化率",
    "收藏",
    "加购",
    "销量",
    "权重",
    "排名",
    "客单价",
    "复购率",
]

OUTDATED_SIGNALS = [
    "直通车",
    "钻展",
    "淘宝达人",
    "微淘",
    "双11",
    "生意参谋",
    "搜索权重",
    "刷单",
    "排名",
    "直播排名",
]


def read_chapter_meta(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    meta: dict[str, str] = {}
    body = text
    if text.startswith("---\n"):
        _, fm, body = text.split("---", 2)
        for line in fm.splitlines():
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            value = value.strip()
            if value.startswith('"') and value.endswith('"'):
                try:
                    value = json.loads(value)
                except json.JSONDecodeError:
                    value = value.strip('"')
            meta[key.strip()] = value
    meta["body"] = body.strip()
    return meta


def unique_hits(text: str, patterns: list[str]) -> list[str]:
    hits = []
    for pat in patterns:
        if pat and pat in text and pat not in hits:
            hits.append(pat)
    return hits


def classify(text: str, title: str) -> list[str]:
    haystack = title + "\n" + text[:4000]
    groups = []
    for group, keywords in KEYWORD_GROUPS.items():
        if any(keyword in haystack for keyword in keywords):
            groups.append(group)
    return groups or ["general"]


def time_sensitivity(text: str, title: str) -> str:
    haystack = title + "\n" + text[:4000]
    hits = unique_hits(haystack, OUTDATED_SIGNALS)
    if len(hits) >= 3:
        return "high"
    if hits:
        return "medium"
    return "low"


def infer_target_pages(groups: list[str], title: str) -> list[str]:
    mapping = {
        "strategy-mindset": "01-taobao-operator-strategic-mindset.md",
        "positioning-selection": "02-category-positioning-and-product-selection.md",
        "search-keywords": "04-search-title-and-keyword-operations.md",
        "visual-conversion": "05-main-image-detail-page-and-selling-point-planning.md",
        "paid-channel": "06-paid-traffic-and-channel-operations.md",
        "customer-service": "07-customer-service-private-domain-and-repurchase.md",
        "promotion-pricing": "08-promotion-pricing-and-major-campaigns.md",
        "supply-finance": "09-supply-chain-warehouse-and-finance.md",
        "team-organization": "10-team-organization-and-performance.md",
    }
    targets = [mapping[g] for g in groups if g in mapping]
    if "新品" in title or "推新品" in title or "产品开发" in title:
        targets.append("03-product-development-and-new-product-testing.md")
    if "成功密码" in title:
        targets.append("11-taobao-operation-success-model.md")
    return sorted(set(targets)) or ["knowledge-architecture-plan.md"]


def extract_knowledge_units(text: str, title: str) -> list[str]:
    candidates: list[str] = []
    for pattern in [
        r"[“\"]([^”\"]{2,24})[”\"]",
        r"([一二三四五六七八九十\d]+个[^，。\n]{2,18})",
        r"([^，。\n]{2,18}法则)",
        r"([^，。\n]{2,18}理论)",
        r"([^，。\n]{2,18}思维)",
        r"([^，。\n]{2,18}原则)",
    ]:
        for match in re.findall(pattern, text[:6000]):
            value = match.strip()
            if value and value not in candidates:
                candidates.append(value)
    if title and title not in candidates:
        candidates.insert(0, title)
    return candidates[:12]


def build_inventory(source_dir: Path) -> list[dict]:
    chapters_dir = source_dir / "chapters"
    if not chapters_dir.exists():
        raise SystemExit(f"Missing chapters directory: {chapters_dir}")
    rows: list[dict] = []
    for path in sorted(chapters_dir.glob("*.md")):
        meta = read_chapter_meta(path)
        title = meta.get("title") or path.stem
        body = meta.get("body", "")
        groups = classify(body, title)
        rows.append(
            {
                "source_id": meta.get("source_id", path.stem.split("-", 1)[0]),
                "source_title": title,
                "source_file": meta.get("source_file", ""),
                "chapter_file": str(path.relative_to(source_dir)),
                "char_count": len(body),
                "topic_groups": groups,
                "knowledge_units": extract_knowledge_units(body, title),
                "cases": unique_hits(body, CASE_PATTERNS),
                "tools_metrics": unique_hits(body, TOOL_METRIC_PATTERNS),
                "time_sensitivity": time_sensitivity(body, title),
                "target_pages": infer_target_pages(groups, title),
            }
        )
    return rows


def md_cell(value: object) -> str:
    if isinstance(value, list):
        value = ", ".join(str(v) for v in value)
    return str(value or "").replace("|", "\\|").replace("\n", " ")


def write_inventory_md(path: Path, source_dir: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Chapter Inventory",
        "",
        f"- Source directory: `{source_dir}`",
        f"- Chapters: {len(rows)}",
        "",
        "| source_id | source_title | source_file | char_count | topic_groups | knowledge_units | cases | tools_metrics | time_sensitivity | target_pages |",
        "| --- | --- | --- | ---: | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| "
            + " | ".join(
                md_cell(row[key])
                for key in [
                    "source_id",
                    "source_title",
                    "source_file",
                    "char_count",
                    "topic_groups",
                    "knowledge_units",
                    "cases",
                    "tools_metrics",
                    "time_sensitivity",
                    "target_pages",
                ]
            )
            + " |"
        )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a chapter inventory from extracted EPUB source.")
    parser.add_argument("source_dir", type=Path, help="Raw book source directory")
    parser.add_argument("--output", required=True, type=Path, help="Output chapter-inventory.md")
    parser.add_argument("--json-output", type=Path, help="Optional JSON output path")
    args = parser.parse_args()

    source_dir = args.source_dir.expanduser()
    output = args.output.expanduser()
    rows = build_inventory(source_dir)
    write_inventory_md(output, source_dir, rows)
    json_output = args.json_output.expanduser() if args.json_output else output.with_suffix(".json")
    write_json(json_output, {"source_dir": str(source_dir), "chapters": rows})
    print(f"Inventory written: {output}")
    print(f"Inventory JSON written: {json_output}")
    print(f"Chapters: {len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
