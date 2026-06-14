#!/usr/bin/env python3
"""Sync local AI agent SKILL.md files into Peter's LLM Wiki registry."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import os
import re
from dataclasses import dataclass
from pathlib import Path


DEFAULT_WIKI_ROOT = Path("/Users/pechen/wiki")
REGISTRY_REL = Path("domains/ai-agent-engineering/90-Skill注册表")


@dataclass(frozen=True)
class AgentSource:
    key: str
    label: str
    roots: tuple[Path, ...]
    output: str
    note: str


AGENT_SOURCES = (
    AgentSource(
        "codex",
        "Codex",
        (Path("/Users/pechen/.codex/skills"),),
        "03-Codex Skill注册页.md",
        "Codex local business skills and system skills.",
    ),
    AgentSource(
        "hermes",
        "Hermes",
        (Path("/Users/pechen/.hermes/skills"),),
        "04-Hermes Skill注册页.md",
        "Hermes main skills directory, excluding duplicated hermes-agent optional skill trees.",
    ),
    AgentSource(
        "lark-agent",
        "Lark Agent",
        (Path("/Users/pechen/.agents/skills"),),
        "05-Lark Agent Skill注册页.md",
        "Feishu/Lark agent skills.",
    ),
    AgentSource(
        "openclaw",
        "OpenClaw",
        (Path("/Users/pechen/.openclaw/workspace/skills"),),
        "06-OpenClaw Skill注册页.md",
        "OpenClaw workspace skills.",
    ),
    AgentSource(
        "sealseek",
        "SealSeek",
        (
            Path("/Users/pechen/.sealseek/skill_pool"),
            Path("/Users/pechen/.sealseek/workspace/skills"),
            Path("/Users/pechen/.sealseek/workspaces/default/skills"),
            Path("/Users/pechen/.sealseek/workspaces/default/active_skills"),
            Path("/Users/pechen/.sealseek/workspaces/default/customized_skills"),
            Path("/Users/pechen/.sealseek/backups"),
            Path("/Users/pechen/sealseek"),
            Path("/Users/pechen/hermes/xc-sealseek-aicoding-skill"),
        ),
        "07-SealSeek Skill注册页.md",
        "SealSeek multi-source skills: global skill_pool, workspace skills, default workspace, active/customized skills, local standalone skills, backups, and migration bundles.",
    ),
    AgentSource(
        "claude-code",
        "Claude Code",
        (Path("/Users/pechen/.claude/plugins/marketplaces/claude-plugins-official.bak"),),
        "08-Claude Code Skill注册页.md",
        "Claude Code plugin marketplace backup skills.",
    ),
)


CATEGORIES = {
    "knowledge-management": "知识库 / 知识管理 / LLM Wiki",
    "visual-and-content-production": "视觉 / 内容 / 课件生产",
    "ecommerce-and-brand": "电商 / 商品 / 品牌运营",
    "agent-engineering-and-tooling": "Agent 工程 / Skill / Plugin / MCP",
    "lark-feishu": "飞书 / Lark / 钉钉自动化",
    "software-engineering": "软件工程 / GitHub / 调试",
    "mlops-and-models": "MLOps / 模型 / 推理训练",
    "research": "研究 / 论文 / 情报",
    "other": "其他能力",
}

OWNERSHIP_LABELS = {
    "personal-project": "个人/项目自定义",
    "system-builtin": "系统/内置",
    "runtime-copy": "运行时副本",
    "archived-backup": "归档/备份",
    "generic-installed": "通用安装/不确定",
}

PERSONAL_REGISTRY_OUTPUT = "01-个人与项目Skill注册库.md"
CENTRAL_REGISTRY_OUTPUT = "02-跨Agent Skill注册库.md"

HERMES_PERSONAL_PATTERNS = re.compile(
    r"peter|sealseek|seal|openclaw|xicheng|xc-|玺承|taobao|tmall|淘宝|天猫|"
    r"ecommerce|电商|商品|店铺|主图|详情页|视觉|生图|gpt-image|gpt生图|"
    r"toapis|evolink|courseware|course-transcript|课程|html-ppt|static-html-courseware|"
    r"feishu|lark|飞书|"
    r"llm-wiki|wiki|knowledge|douyin|抖音|wechat|微信|baoyu|"
    r"reduce-paid-ratio|shopping-basket|conference|static-html|skill-sync|"
    r"skill-migration|aicoding|feature-doc",
    re.I,
)


SKIP_PARTS = {".venv", "node_modules", "runtime", "__pycache__"}

DEPRECATED_LLM_WIKI_ENTRIES = {
    "api-docs-wiki-ingest",
    "wiki-clippings-ingest",
    "book-to-llm-wiki",
    "course-transcript-to-knowledge",
}

SKIP_SOURCE_PARTS = {".llmwiki-source"}


@dataclass
class SkillEntry:
    agent: str
    source_key: str
    source_label: str
    name: str
    heading: str
    description: str
    path: Path
    rel: str
    kind: str
    category: str
    input_hint: str
    search: str
    digest: str
    ownership: str
    ownership_reason: str


def compact(text: str, max_len: int = 520) -> str:
    text = re.sub(r"\s+", " ", text or "").strip()
    if len(text) <= max_len:
        return text
    return text[: max_len - 1] + "…"


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    block = text[4:end].splitlines()
    out: dict[str, str] = {}
    current: str | None = None
    for raw in block:
        line = raw.rstrip()
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if match:
            current = match.group(1)
            value = match.group(2).strip()
            if (value.startswith('"') and value.endswith('"')) or (
                value.startswith("'") and value.endswith("'")
            ):
                value = value[1:-1]
            out[current] = "" if value in {"|", ">"} else value
        elif current and re.match(r"^\s+", line):
            out[current] = (out[current] + " " + line.strip()).strip()
    return out


def first_heading(text: str) -> str:
    match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    return match.group(1).strip() if match else ""


def first_useful_paragraph(text: str) -> str:
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            text = text[end + 4 :]
    for para in re.split(r"\n\s*\n", text):
        para = para.strip()
        if not para or para.startswith("#") or para.startswith("```"):
            continue
        clean = re.sub(r"\s+", " ", para)
        if len(clean) > 20:
            return clean
    return ""


def walk_skill_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    found: list[Path] = []
    for current, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_PARTS and d not in SKIP_SOURCE_PARTS]
        if any(part in SKIP_PARTS or part in SKIP_SOURCE_PARTS for part in Path(current).parts):
            continue
        if "SKILL.md" in files:
            found.append(Path(current) / "SKILL.md")
    return found


def category_for(rel: str, desc: str, name: str) -> str:
    text = f"{rel} {name} {desc}".lower()
    patterns = (
        ("knowledge-management", r"wiki|knowledge|obsidian|clipping|入脑|知识库"),
        ("visual-and-content-production", r"image|visual|design|creative|生图|图片|视觉|主图|详情页|ppt|deck|slide|courseware|xmind"),
        ("ecommerce-and-brand", r"ecommerce|taobao|tmall|sycm|生意参谋|商品|店铺|电商|brand|品牌|关键词|搜索词|市场排行|推广|对账"),
        ("agent-engineering-and-tooling", r"api|mcp|plugin|skill|agent|codex|claude|hermes|openclaw|sealseek|toolchain"),
        ("lark-feishu", r"lark|feishu|飞书|钉钉"),
        ("software-engineering", r"github|code|debug|test|repo|software|devops|代码"),
        ("mlops-and-models", r"mlops|model|training|inference|llm|huggingface"),
        ("research", r"research|paper|arxiv|blog|polymarket|论文|研究"),
    )
    for category, pattern in patterns:
        if re.search(pattern, text):
            return category
    return "other"


def input_hint(desc: str, name: str) -> str:
    text = f"{name} {desc}".lower()
    hints: list[str] = []
    checks = (
        (r"xlsx|excel|spreadsheet|csv|表格|workbook|对账", "Excel/CSV/表格文件、字段信息或数据分析需求"),
        (r"ppt|deck|slide|presentation|课件|幻灯片|xmind|脑图", "课程大纲、逐页内容、PPT/XMind/课件制作或修改需求"),
        (r"image|图片|图像|白底图|视觉|生图|主图|详情页", "图片路径、视觉目标、品类/风格/生成或编辑要求"),
        (r"api|endpoint|openapi|接口|文档", "API 文档 URL、接口规格、鉴权/参数/示例需求"),
        (r"wiki|knowledge|知识库|入脑|clipping|clip", "wiki 路径、资料来源、剪藏文件、知识库查询或维护需求"),
        (r"browser|chrome|网页|页面|plugin|extension|插件|接管|爬取", "已打开网页、浏览器页面、插件功能或页面 API 线索"),
        (r"lark|feishu|飞书|doc|base|sheet|calendar|mail|task|minutes|钉钉", "飞书/钉钉资源 URL/ID、文档/表格/日程/消息等操作需求"),
        (r"code|repo|github|git|debug|test|review|开发|代码", "代码仓库、文件路径、PR/Issue、调试或开发任务"),
        (r"mcp|server|tool", "MCP server、工具配置、连接或封装需求"),
        (r"agent|skill|plugin|claude|codex|hermes|openclaw|sealseek", "agent/skill/plugin 名称、目标能力、运行环境或迁移需求"),
        (r"audio|video|youtube|podcast|minutes|transcript|音频|视频|转录", "音视频链接/文件、转录稿、会议纪要或内容处理需求"),
        (r"taobao|tmall|sycm|生意参谋|ecommerce|电商|商品|店铺|淘宝|天猫|关键词|搜索词|市场排行|推广", "电商平台页面、商品/店铺/关键词数据、运营规则或视觉策划需求"),
    )
    for pattern, hint in checks:
        if re.search(pattern, text) and hint not in hints:
            hints.append(hint)
    if not hints:
        hints.append("用户任务描述；执行前打开 SKILL.md 查看完整输入契约")
    return "；".join(hints[:4])


def source_type(file_path: Path, source: AgentSource, rel: str) -> str:
    path_str = str(file_path)
    if source.key == "sealseek":
        mapping = (
            ("/.sealseek/skill_pool/", "global-skill-pool"),
            ("/.sealseek/workspace/skills/", "workspace-skills"),
            ("/.sealseek/workspaces/default/skills/", "default-workspace-skills"),
            ("/.sealseek/workspaces/default/active_skills/", "active-skills"),
            ("/.sealseek/workspaces/default/customized_skills/", "customized-skills"),
            ("/.sealseek/backups/", "backup"),
            ("/Users/pechen/sealseek/", "standalone-local"),
            ("/Users/pechen/hermes/xc-sealseek-aicoding-skill/", "migration-bundle"),
        )
        for needle, label in mapping:
            if needle in path_str:
                return label
    if rel.startswith(".system/"):
        return "system"
    if re.search(r"archive|backup|\.bak|_archived|原始备份", path_str, re.I):
        return "archived-or-backup"
    return "local"


def ownership_for(file_path: Path, source: AgentSource, kind: str, name: str, desc: str, rel: str) -> tuple[str, str]:
    if kind in {"archived-or-backup", "backup"}:
        return "archived-backup", "路径或来源类型显示为备份/归档，不作为日常优先使用 skill。"
    if source.key == "codex":
        if kind == "system":
            return "system-builtin", "Codex `.system` 内置 skill。"
        return "personal-project", "Codex 非 `.system` 本地 skill，按个人/项目自定义处理。"
    if source.key == "hermes":
        probe = f"{file_path} {rel} {name} {desc}"
        if HERMES_PERSONAL_PATTERNS.search(probe):
            return "personal-project", "Hermes skill 命中 Peter 项目/业务/知识库/电商/课程/视觉等定制关键词。"
        return "generic-installed", "Hermes 通用能力库 skill，未命中个人项目关键词；保留在全量库，不进入个人库。"
    if source.key == "lark-agent":
        return "system-builtin", "Lark/Feishu 通用工具 skill，视为底层工具能力。"
    if source.key == "openclaw":
        return "personal-project", "OpenClaw workspace skill，按项目自定义能力处理。"
    if source.key == "sealseek":
        if kind == "global-skill-pool":
            return "system-builtin", "SealSeek 全局 skill_pool，视为系统/底层通用能力。"
        if kind == "active-skills":
            return "runtime-copy", "SealSeek default workspace active_skills 运行时副本；全量保留，个人库优先使用源目录条目。"
        if kind in {"workspace-skills", "default-workspace-skills", "customized-skills", "standalone-local", "migration-bundle"}:
            return "personal-project", "SealSeek workspace/customized/standalone/migration skill，按个人/项目自定义处理。"
        return "generic-installed", "SealSeek 其他来源，归入通用安装/不确定。"
    if source.key == "claude-code":
        return "system-builtin", "Claude Code official plugin marketplace backup skill，视为系统/官方示例能力。"
    return "generic-installed", "未匹配到明确归属规则。"


def entry_for(file_path: Path, source: AgentSource) -> SkillEntry:
    text = file_path.read_text(encoding="utf-8", errors="replace")
    root = next((r for r in source.roots if file_path == r or r in file_path.parents), source.roots[0])
    rel = file_path.relative_to(root).as_posix()
    fm = parse_frontmatter(text)
    name = compact(fm.get("name") or file_path.parent.name, 120)
    desc = compact(fm.get("description") or first_useful_paragraph(text) or first_heading(text) or name, 720)
    heading = first_heading(text)
    kind = source_type(file_path, source, rel)
    category = category_for(rel, desc, name)
    ownership, ownership_reason = ownership_for(file_path, source, kind, name, desc, rel)
    search = compact(f"{name} {heading} {desc} {rel} {kind}".replace("`", " "), 900)
    digest = hashlib.sha1(text.encode("utf-8", errors="replace")).hexdigest()
    return SkillEntry(
        agent=source.label,
        source_key=source.key,
        source_label=kind,
        name=name,
        heading=heading,
        description=desc,
        path=file_path,
        rel=rel,
        kind=kind,
        category=category,
        input_hint=input_hint(desc, name),
        search=search,
        digest=digest,
        ownership=ownership,
        ownership_reason=ownership_reason,
    )


def is_deprecated_llm_wiki_entry(file_path: Path, entry: SkillEntry) -> bool:
    if entry.name in DEPRECATED_LLM_WIKI_ENTRIES:
        return True
    if file_path.parent.name in DEPRECATED_LLM_WIKI_ENTRIES:
        return True
    return any(part in DEPRECATED_LLM_WIKI_ENTRIES for part in file_path.parts)


def collect_entries() -> dict[str, tuple[AgentSource, list[SkillEntry]]]:
    collected: dict[str, tuple[AgentSource, list[SkillEntry]]] = {}
    for source in AGENT_SOURCES:
        seen: set[Path] = set()
        files: list[Path] = []
        for root in source.roots:
            for file_path in walk_skill_files(root):
                if file_path not in seen:
                    seen.add(file_path)
                    files.append(file_path)
        entries = []
        for p in sorted(files):
            entry = entry_for(p, source)
            if is_deprecated_llm_wiki_entry(p, entry):
                continue
            entries.append(entry)
        collected[source.key] = (source, entries)
    return collected


def yaml_header(title: str, tags: list[str], sources: list[Path], today: str) -> str:
    source_lines = "\n".join(f"  - {p}" for p in sources)
    return (
        f"---\n"
        f"title: {title}\n"
        f"type: concept\n"
        f"created: {today}\n"
        f"updated: {today}\n"
        f"domain: ai-agent-engineering\n"
        f"tags: [{', '.join(tags)}]\n"
        f"sources:\n{source_lines}\n"
        f"status: active\n"
        f"---\n"
    )


def entry_markdown(entry: SkillEntry) -> str:
    return (
        f"### `{entry.name}`\n\n"
        f"- Agent / 环境：{entry.agent}\n"
        f"- 归属分类：{OWNERSHIP_LABELS[entry.ownership]}\n"
        f"- 归属依据：{entry.ownership_reason}\n"
        f"- 来源类型：{entry.kind}\n"
        f"- 能力分类：{CATEGORIES[entry.category]}\n"
        f"- Skill 文件位置：`{entry.path}`\n"
        f"- 功能检索描述：{entry.description}\n"
        f"- 输入 / 触发方式：{entry.input_hint}\n"
        f"- 检索关键词：{entry.search}\n"
    )


def render_agent_page(source: AgentSource, entries: list[SkillEntry], today: str) -> str:
    title = "Codex Skill 注册页" if source.key == "codex" else f"{source.label} Skill 注册页"
    parts = [yaml_header(title, ["ai-agent", source.key, "skill", "registry"], list(source.roots), today)]
    parts.append(f"# {title}\n\n")
    parts.append(f"本页记录 {source.label} 环境中的 skill，用于 AI Agent 检索“是否已有类似 skill”并定位原始 SKILL.md。\n\n")
    parts.append("## 维护范围\n\n来源目录：\n\n")
    parts.extend(f"- `{root}`\n" for root in source.roots)
    parts.append(f"\n- 说明：{source.note}\n- 当前记录数量：{len(entries)}\n\n")
    ownership_counts: dict[str, int] = {}
    for entry in entries:
        ownership_counts[entry.ownership] = ownership_counts.get(entry.ownership, 0) + 1
    parts.append("归属分类统计：\n\n")
    parts.extend(
        f"- {OWNERSHIP_LABELS[ownership]}: {ownership_counts[ownership]}\n"
        for ownership in OWNERSHIP_LABELS
        if ownership in ownership_counts
    )
    parts.append("\n")
    if source.key == "sealseek":
        counts: dict[str, int] = {}
        for entry in entries:
            counts[entry.kind] = counts.get(entry.kind, 0) + 1
        parts.append("SealSeek 来源类型统计：\n\n")
        parts.extend(f"- {kind}: {counts[kind]}\n" for kind in sorted(counts))
        parts.append("\n")
    parts.append(
        "## 使用规则\n\n"
        "- 先用本页的名称、功能检索描述、输入方式和关键词判断是否存在类似 skill。\n"
        "- 日常优先检索 [[domains/ai-agent-engineering/90-Skill注册表/01-个人与项目Skill注册库|个人/项目 Skill 注册库]]；只有找不到时再回到全量库。\n"
        "- 找到候选后，必须打开 `Skill 文件位置` 中的 `SKILL.md` 阅读完整流程、依赖和约束。\n"
        "- skill 多数可以跨 Agent 迁移，但执行前要检查工具、路径、权限、环境变量和脚本依赖。\n\n"
    )
    parts.append("## 按能力分类快速索引\n\n")
    by_category: dict[str, list[SkillEntry]] = {}
    for entry in entries:
        by_category.setdefault(entry.category, []).append(entry)
    for category, label in CATEGORIES.items():
        items = by_category.get(category, [])
        if not items:
            continue
        parts.append(f"### {label}\n\n")
        for entry in items:
            desc = entry.description[:120] + ("…" if len(entry.description) > 120 else "")
            parts.append(f"- `{entry.name}` ({OWNERSHIP_LABELS[entry.ownership]} / {entry.kind})：{desc}\n")
        parts.append("\n")
    parts.append("## Skill 详情\n\n")
    for entry in entries:
        parts.append(entry_markdown(entry))
        parts.append("\n")
    return "".join(parts)


def render_central_page(collected: dict[str, tuple[AgentSource, list[SkillEntry]]], today: str) -> str:
    all_entries = [entry for _, entries in collected.values() for entry in entries]
    personal_entries = [entry for entry in all_entries if entry.ownership == "personal-project"]
    all_roots = [root for source, _ in collected.values() for root in source.roots]
    parts = [yaml_header("跨 Agent Skill 注册库", ["ai-agent", "skill", "registry", "toolchain", "knowledge-base"], all_roots, today)]
    parts.append("# 跨 Agent Skill 注册库\n\n")
    parts.append(
        "本页是所有 AI Agent skill 的统一检索入口。目标不是只记录“某个 agent 当前能不能直接调用”，"
        "而是帮助任何 Agent 回答：我们以前有没有写过类似 skill？它在哪个文件夹？是否可以复用、迁移或改造？\n\n"
    )
    ownership_counts: dict[str, int] = {}
    for entry in all_entries:
        ownership_counts[entry.ownership] = ownership_counts.get(entry.ownership, 0) + 1
    parts.append(
        f"当前覆盖 {len(collected)} 个 Agent / 环境，共 {len(all_entries)} 个 skill；"
        f"其中个人/项目自定义 {len(personal_entries)} 个。\n\n"
    )
    parts.append(
        "## 检索协议\n\n"
        "当用户问“有没有类似 skill”“以前是不是写过”“能不能复用某个能力”时，Agent 应按以下顺序处理：\n\n"
        "1. 日常先搜索 [[domains/ai-agent-engineering/90-Skill注册表/01-个人与项目Skill注册库|个人/项目 Skill 注册库]]。\n"
        "2. 如果个人库没有候选，再搜索本全量页和下方各 agent 注册页的 skill 名称、功能检索描述、输入方式、检索关键词。\n"
        "3. 找到候选 skill 后，打开对应 `SKILL.md` 文件位置，阅读完整设计内容。\n"
        "4. 判断可复用方式：直接使用、跨 Agent 迁移、抽取脚本/参考文件、合并重复 skill、或新建 skill。\n"
        "5. 不因 skill 位于其他 agent 环境就忽略它；大多数 skill 的流程、脚本、参考文件都可以跨环境复用。\n"
        "6. 执行或迁移前检查运行环境差异：工具名、MCP、浏览器、API key、文件路径、脚本依赖、权限和输出目录。\n\n"
    )
    parts.append("## 归属分类统计\n\n")
    parts.extend(
        f"- {OWNERSHIP_LABELS[ownership]}: {ownership_counts[ownership]}\n"
        for ownership in OWNERSHIP_LABELS
        if ownership in ownership_counts
    )
    parts.append("\n")
    parts.append("## Agent 分类入口\n\n")
    parts.append(
        f"- [[domains/ai-agent-engineering/90-Skill注册表/{PERSONAL_REGISTRY_OUTPUT.removesuffix('.md')}|个人/项目 Skill 注册库]]："
        f"{len(personal_entries)} 个个人或项目定制 skill，日常优先检索。\n"
    )
    for source, entries in collected.values():
        roots = "、".join(f"`{root}`" for root in source.roots)
        target = source.output.removesuffix(".md")
        parts.append(f"- [[domains/ai-agent-engineering/90-Skill注册表/{target}|{source.label} Skill 注册页]]：{len(entries)} 个 skill。来源：{roots}\n")
    parts.append("\n## 全局能力索引\n\n")
    by_category: dict[str, list[SkillEntry]] = {}
    for entry in all_entries:
        by_category.setdefault(entry.category, []).append(entry)
    for category, label in CATEGORIES.items():
        items = by_category.get(category, [])
        if not items:
            continue
        parts.append(f"### {label}\n\n")
        for entry in items:
            desc = entry.description[:150] + ("…" if len(entry.description) > 150 else "")
            parts.append(
                f"- `{entry.name}` ({entry.agent}, {OWNERSHIP_LABELS[entry.ownership]}, {entry.kind})："
                f"{desc} 位置：`{entry.path}`\n"
            )
        parts.append("\n")
    parts.append(
        "## 维护规则\n\n"
        "- 每个 agent 仍保留独立注册页，避免运行环境混乱。\n"
        "- 总入口页负责跨 Agent 检索，不负责替代原始 `SKILL.md`。\n"
        "- 新增、删除或迁移 skill 后，同步更新本页和对应 agent 注册页。\n"
        "- 不写入真实密钥、cookie、token、客户隐私数据。\n"
        "- 发现重复 skill 时，不要马上删除；先记录候选重复关系，再决定合并或保留。\n"
    )
    return "".join(parts)


def render_personal_page(collected: dict[str, tuple[AgentSource, list[SkillEntry]]], today: str) -> str:
    all_entries = [entry for _, entries in collected.values() for entry in entries]
    personal_entries = [entry for entry in all_entries if entry.ownership == "personal-project"]
    all_roots = [root for source, _ in collected.values() for root in source.roots]
    parts = [
        yaml_header(
            "个人/项目 Skill 注册库",
            ["ai-agent", "skill", "registry", "personal", "project"],
            all_roots,
            today,
        )
    ]
    parts.append("# 个人/项目 Skill 注册库\n\n")
    parts.append(
        "本页只收录 Peter 自己创建、让 Agent 为项目定制、或明显服务于 Peter 项目/业务流程的 skill。"
        "它是日常检索“以前有没有做过类似 skill”的优先入口。\n\n"
    )
    parts.append(
        "不收录 Codex/Claude/Lark/SealSeek 等 Agent 的系统内置 skill、底层工具 skill、运行时副本和备份条目；"
        "这些仍保留在 [[domains/ai-agent-engineering/90-Skill注册表/02-跨Agent Skill注册库|跨 Agent Skill 注册库]]。\n\n"
    )
    parts.append(f"当前个人/项目 skill 数量：{len(personal_entries)}。\n\n")
    parts.append("## 分类规则\n\n")
    parts.append(
        "- Codex 非 `.system` 本地 skill：视为个人/项目自定义。\n"
        "- OpenClaw workspace skill：视为项目自定义。\n"
        "- SealSeek workspace/default/customized/standalone/migration skill：视为个人/项目自定义；`skill_pool` 和 `active_skills` 不进入本页。\n"
        "- Hermes skill：命中 Peter 项目、电商、视觉、课程、LLM Wiki、Sealseek/OpenClaw/玺承等关键词时进入本页；否则归入通用安装/不确定。\n"
        "- Claude Code 官方 marketplace、Codex `.system`、Lark 通用工具 skill：作为系统/底层能力，只在全量库中保留。\n\n"
    )
    parts.append("## Agent 快速索引\n\n")
    by_agent: dict[str, list[SkillEntry]] = {}
    for entry in personal_entries:
        by_agent.setdefault(entry.agent, []).append(entry)
    for agent in sorted(by_agent):
        parts.append(f"### {agent}\n\n")
        for entry in by_agent[agent]:
            desc = entry.description[:140] + ("…" if len(entry.description) > 140 else "")
            parts.append(f"- `{entry.name}` ({entry.kind})：{desc} 位置：`{entry.path}`\n")
        parts.append("\n")
    parts.append("## 能力分类索引\n\n")
    by_category: dict[str, list[SkillEntry]] = {}
    for entry in personal_entries:
        by_category.setdefault(entry.category, []).append(entry)
    for category, label in CATEGORIES.items():
        items = by_category.get(category, [])
        if not items:
            continue
        parts.append(f"### {label}\n\n")
        for entry in items:
            desc = entry.description[:150] + ("…" if len(entry.description) > 150 else "")
            parts.append(f"- `{entry.name}` ({entry.agent}, {entry.kind})：{desc} 位置：`{entry.path}`\n")
        parts.append("\n")
    parts.append("## Skill 详情\n\n")
    for entry in personal_entries:
        parts.append(entry_markdown(entry))
        parts.append("\n")
    return "".join(parts)


def replace_section(text: str, header: str, body: str) -> str:
    pattern = re.compile(rf"(^## {re.escape(header)}\n)(.*?)(?=^## |\Z)", re.MULTILINE | re.DOTALL)
    replacement = f"## {header}\n\n{body.rstrip()}\n\n"
    if pattern.search(text):
        return pattern.sub(replacement, text)
    return text.rstrip() + "\n\n" + replacement


def update_index_pages(wiki_root: Path, today: str) -> list[Path]:
    touched: list[Path] = []
    main_index = wiki_root / "index.md"
    domain_index = wiki_root / "domains/ai-agent-engineering/index.md"
    registry_body = (
        "- [[domains/ai-agent-engineering/90-Skill注册表/01-个人与项目Skill注册库|个人/项目 Skill 注册库]]：只收录 Peter 自己创建、让 Agent 为项目定制、或明显服务于 Peter 项目/业务流程的 skill，是日常检索“有没有类似 skill”的优先入口。\n"
        "- [[domains/ai-agent-engineering/90-Skill注册表/02-跨Agent Skill注册库|跨 Agent Skill 注册库]]：统一检索 Codex、Hermes、Lark Agent、OpenClaw、SealSeek、Claude Code 的 skill，定位原始 `SKILL.md` 并判断复用或迁移可能。\n"
        "- [[domains/ai-agent-engineering/90-Skill注册表/03-Codex Skill注册页|Codex Skill 注册页]]：Codex 本地业务 skill 与系统 skill 的检索描述、输入方式、关键词和文件位置。\n"
        "- [[domains/ai-agent-engineering/90-Skill注册表/04-Hermes Skill注册页|Hermes Skill 注册页]]：Hermes 主 skill 目录的检索描述、输入方式、关键词和文件位置。\n"
        "- [[domains/ai-agent-engineering/90-Skill注册表/05-Lark Agent Skill注册页|Lark Agent Skill 注册页]]：飞书/Lark 相关 skill 的检索描述、输入方式、关键词和文件位置。\n"
        "- [[domains/ai-agent-engineering/90-Skill注册表/06-OpenClaw Skill注册页|OpenClaw Skill 注册页]]：OpenClaw workspace skill 的检索描述、输入方式、关键词和文件位置。\n"
        "- [[domains/ai-agent-engineering/90-Skill注册表/07-SealSeek Skill注册页|SealSeek Skill 注册页]]：SealSeek 多来源 skill 的检索描述、输入方式、关键词和文件位置，覆盖 skill_pool、workspace、active/customized、standalone 和迁移包。\n"
        "- [[domains/ai-agent-engineering/90-Skill注册表/08-Claude Code Skill注册页|Claude Code Skill 注册页]]：Claude Code plugin marketplace skill 的检索描述、输入方式、关键词和文件位置。"
    )
    main_body = (
        "- [[domains/ai-agent-engineering/index|AI Agent 工程知识域]]：LLM Wiki、Skill、工具链、自动化工作流与多 Agent 工程方法。\n"
        "- [[domains/ai-agent-engineering/01-知识系统/01-LLM Wiki个人知识库运行闭环|LLM Wiki 个人知识库运行闭环]]：用 Ingest / Query / Lint 三个动作，把知识库从“资料堆”变成持续复利的个人知识系统。\n"
        "- [[domains/ai-agent-engineering/03-Skill设计/01-LLM Wiki Skill同源包|LLM Wiki Skill 同源包]]：Codex 维护、GitHub 分发、SealSeek/Hermes 安装使用的 LLM Wiki skill 收敛规则与发布入口。\n"
        "- [[domains/ai-agent-engineering/03-Skill设计/02-无限画板Skill写作知识库/index|无限画板 Skill 写作知识库]]：从历史无限画板 skill 中沉淀出的写作规则、工具规范、任务范式、prompt 模板、反坑清单和质量检查。\n"
        "- [[domains/ai-agent-engineering/05-工具链/01-OpenAI图像生成API集成指南|OpenAI 图像生成 API 集成指南]]：Image API 与 Responses API 的选择、参数、编辑、流式、错误处理和成本判断。\n"
        f"{registry_body}"
    )
    if main_index.exists():
        text = main_index.read_text(encoding="utf-8")
        text = re.sub(r"> Last updated: \d{4}-\d{2}-\d{2}", f"> Last updated: {today}", text)
        new_text = replace_section(text, "AI Agent Engineering", main_body)
        if new_text != text:
            main_index.write_text(new_text, encoding="utf-8")
            touched.append(main_index)
    if domain_index.exists():
        text = domain_index.read_text(encoding="utf-8")
        new_text = replace_section(text, "Skill 注册表", registry_body)
        if new_text == text:
            new_text = replace_section(text, "Skill 设计", registry_body)
        if new_text != text:
            domain_index.write_text(new_text, encoding="utf-8")
            touched.append(domain_index)
    return touched


def prepend_log(wiki_root: Path, today: str, collected: dict[str, tuple[AgentSource, list[SkillEntry]]], touched: list[Path]) -> Path | None:
    log_path = wiki_root / "log.md"
    if not log_path.exists():
        return None
    counts = ", ".join(f"{source.label} {len(entries)}" for source, entries in collected.values())
    total = sum(len(entries) for _, entries in collected.values())
    personal_total = sum(
        1
        for _, entries in collected.values()
        for entry in entries
        if entry.ownership == "personal-project"
    )
    touched_rel = [str(p.relative_to(wiki_root)) for p in touched if p.is_relative_to(wiki_root)]
    entry = (
        f"## [{today}] compile | 同步跨 Agent Skill 注册库\n"
        f"- Updated: `domains/ai-agent-engineering/90-Skill注册表/02-跨Agent Skill注册库.md`\n"
        f"- Updated: `domains/ai-agent-engineering/90-Skill注册表/01-个人与项目Skill注册库.md`\n"
        f"- Updated: agent-specific skill registry pages under `domains/ai-agent-engineering/90-Skill注册表/`\n"
        f"- Updated: `index.md`\n"
        f"- Updated: `domains/ai-agent-engineering/index.md`\n"
        f"- Notes: 扫描系统中 Codex、Hermes、Lark Agent、OpenClaw、SealSeek、Claude Code 的 `SKILL.md`，当前总计 {total} 个 skill，其中个人/项目自定义 {personal_total} 个；{counts}。Touched: {', '.join(touched_rel)}。\n\n"
    )
    text = log_path.read_text(encoding="utf-8")
    marker = re.search(r"^## \[\d{4}-\d{2}-\d{2}\]", text, re.MULTILINE)
    if marker:
        new_text = text[: marker.start()] + entry + text[marker.start() :]
    else:
        new_text = text.rstrip() + "\n\n" + entry
    log_path.write_text(new_text, encoding="utf-8")
    return log_path


def write_if_changed(path: Path, content: str, dry_run: bool) -> bool:
    old = path.read_text(encoding="utf-8") if path.exists() else None
    if old == content:
        return False
    if not dry_run:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return True


def sync(wiki_root: Path, dry_run: bool, no_log: bool) -> tuple[dict[str, tuple[AgentSource, list[SkillEntry]]], list[Path]]:
    today = dt.date.today().isoformat()
    registry_dir = wiki_root / REGISTRY_REL
    collected = collect_entries()
    touched: list[Path] = []
    central = render_central_page(collected, today)
    central_path = registry_dir / CENTRAL_REGISTRY_OUTPUT
    if write_if_changed(central_path, central, dry_run):
        touched.append(central_path)
    personal = render_personal_page(collected, today)
    personal_path = registry_dir / PERSONAL_REGISTRY_OUTPUT
    if write_if_changed(personal_path, personal, dry_run):
        touched.append(personal_path)
    for source, entries in collected.values():
        page = render_agent_page(source, entries, today)
        path = registry_dir / source.output
        if write_if_changed(path, page, dry_run):
            touched.append(path)
    if not dry_run:
        touched.extend(update_index_pages(wiki_root, today))
        if not no_log:
            log_path = prepend_log(wiki_root, today, collected, touched)
            if log_path:
                touched.append(log_path)
    return collected, touched


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync local AI agent skills into the LLM Wiki registry.")
    parser.add_argument("--wiki-root", default=str(DEFAULT_WIKI_ROOT), help="Wiki root directory.")
    parser.add_argument("--dry-run", action="store_true", help="Print what would change without writing files.")
    parser.add_argument("--no-log", action="store_true", help="Do not append log.md.")
    args = parser.parse_args()
    collected, touched = sync(Path(args.wiki_root).expanduser(), args.dry_run, args.no_log)
    total = 0
    ownership_counts: dict[str, int] = {}
    for source, entries in collected.values():
        total += len(entries)
        for entry in entries:
            ownership_counts[entry.ownership] = ownership_counts.get(entry.ownership, 0) + 1
        print(f"{source.label}: {len(entries)}")
    print(f"Total: {total}")
    print("Ownership:")
    for ownership, label in OWNERSHIP_LABELS.items():
        if ownership in ownership_counts:
            print(f"- {label}: {ownership_counts[ownership]}")
    if args.dry_run:
        print("Dry run: no files written.")
    print("Touched pages:")
    for path in touched:
        print(f"- {path}")


if __name__ == "__main__":
    main()
