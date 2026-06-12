#!/usr/bin/env python3
import argparse
import datetime as dt
import json
import re
from pathlib import Path


KIND_TITLES = {
    "interface_notes": "接口说明",
    "scenarios": "调用场景",
    "request_urls": "请求地址",
    "common_request_params": "公共请求参数",
    "business_request_params": "业务请求参数",
    "response_params": "响应参数",
    "common_response_params": "公共响应参数",
    "business_response_params": "业务响应参数",
    "errors": "错误码",
    "examples": "示例",
}

CATEGORY_SLUGS = {
    "订单类": "order",
    "库存类": "stock",
    "货品类": "goods",
    "基础类": "base",
    "售后类": "aftersales",
    "采购类": "purchase",
}


def md_escape(value):
    text = "" if value is None else str(value)
    return text.replace("|", "\\|").replace("\n", " ").strip()


def slugify(text, fallback):
    if text in CATEGORY_SLUGS:
        return CATEGORY_SLUGS[text]
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", str(text).lower()).strip("-")
    return slug or fallback


def table_to_md(rows):
    if not rows:
        return ""
    width = max(len(r) for r in rows)
    normalized = []
    for row in rows:
        normalized.append([md_escape(c) for c in list(row) + [""] * (width - len(row))])
    out = []
    out.append("| " + " | ".join(normalized[0]) + " |")
    out.append("| " + " | ".join(["---"] * width) + " |")
    for row in normalized[1:]:
        out.append("| " + " | ".join(row) + " |")
    return "\n".join(out)


def endpoint_sort_key(endpoint):
    return (
        str(endpoint.get("category") or ""),
        str(endpoint.get("service") or endpoint.get("operationId") or endpoint.get("apiName") or ""),
    )


def endpoint_name(endpoint):
    return endpoint.get("service") or endpoint.get("operationId") or endpoint.get("path") or endpoint.get("apiName") or "unnamed-endpoint"


def write_category_page(path, category, endpoints, args, source):
    today = dt.date.today().isoformat()
    title = f"{args.title_prefix} {category} API 使用手册".strip()
    tags = ", ".join(args.tags)
    lines = [
        "---",
        f"title: {title}",
        "type: concept",
        f"created: {today}",
        f"updated: {today}",
        f"domain: {args.domain}",
        f"tags: [{tags}]",
        "sources:",
        f"  - {source}",
        "status: active",
        "---",
        "",
        f"# {title}",
        "",
        "## 用途",
        "",
        f"本页整理 {args.title_prefix} {category} 的具体接口使用方法，面向后续写代码、创建 Codex/Hermes skill、生成数据导出脚本或自动化工作流。",
        "",
        "## 本类接口",
        "",
    ]

    index_rows = [["服务名", "接口名", "描述", "文档 URL"]]
    for e in endpoints:
        index_rows.append([
            endpoint_name(e),
            e.get("apiName") or e.get("docTitle") or "",
            e.get("description") or "",
            e.get("docUrl") or "",
        ])
    lines.append(table_to_md(index_rows))
    lines.extend(["", "## 接口详情", ""])

    for e in endpoints:
        name = endpoint_name(e)
        api_name = e.get("apiName") or e.get("docTitle") or ""
        lines.extend([
            f"### {name}：{api_name}" if api_name else f"### {name}",
            "",
            "| 项目 | 内容 |",
            "|---|---|",
            f"| 分类 | {md_escape(e.get('category') or category)} |",
            f"| 服务名 | `{md_escape(name)}` |",
            f"| 方法 | {md_escape(e.get('method') or '')} |",
            f"| 路径/PHP 文件 | {md_escape(e.get('path') or e.get('phpFile') or '')} |",
            f"| 描述 | {md_escape(e.get('description') or '')} |",
            f"| 客户端路径 | {md_escape(e.get('clientPath') or '')} |",
            f"| 文档 URL | {md_escape(e.get('docUrl') or '')} |",
            "",
        ])

        tables = e.get("tables") or []
        used = False
        for table in tables:
            rows = table.get("rows") or []
            if not rows:
                continue
            kind = table.get("kind") or f"table_{table.get('index', '')}"
            heading = KIND_TITLES.get(kind, kind)
            lines.extend([f"#### {heading}", "", table_to_md(rows), ""])
            used = True

        for ex in e.get("examples") or []:
            title = ex.get("title") or "示例"
            language = ex.get("language") or "text"
            body = ex.get("body") or ex.get("content") or ""
            if body:
                lines.extend([f"#### {title}", "", f"```{language}", str(body).strip(), "```", ""])
                used = True

        if not used and e.get("fullText"):
            excerpt = str(e["fullText"]).strip()
            if len(excerpt) > args.fulltext_excerpt:
                excerpt = excerpt[: args.fulltext_excerpt].rstrip() + "\n\n[截断：完整正文见 raw source]"
            lines.extend(["#### 原始正文摘录", "", "```text", excerpt, "```", ""])

    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Compile normalized API scrape JSON into category Markdown manuals.")
    parser.add_argument("--input", required=True, help="Normalized scrape JSON path.")
    parser.add_argument("--output-dir", required=True, help="Directory for generated category manuals.")
    parser.add_argument("--title-prefix", required=True, help="Provider/product title prefix.")
    parser.add_argument("--domain", default="ecommerce-ops", help="Wiki domain frontmatter value.")
    parser.add_argument("--source", required=True, help="Raw source path to write in frontmatter.")
    parser.add_argument("--tags", nargs="*", default=["api"], help="Frontmatter tags without brackets.")
    parser.add_argument("--fulltext-excerpt", type=int, default=2500, help="Fallback excerpt length when no tables/examples exist.")
    args = parser.parse_args()

    data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    endpoints = data.get("endpoints") or []
    grouped = {}
    for endpoint in sorted(endpoints, key=endpoint_sort_key):
        category = endpoint.get("category") or "uncategorized"
        grouped.setdefault(category, []).append(endpoint)

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for idx, (category, items) in enumerate(grouped.items(), start=1):
        slug = slugify(category, f"category-{idx}")
        path = out_dir / f"{slug}-apis.md"
        write_category_page(path, category, items, args, args.source)
        written.append(str(path))

    print(json.dumps({"category_count": len(grouped), "endpoint_count": len(endpoints), "files": written}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
