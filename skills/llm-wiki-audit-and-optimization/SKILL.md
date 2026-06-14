---
name: llm-wiki-audit-and-optimization
description: Audit and optimize an LLM Wiki's compile-routing-reasoning quality. Use after a wiki/domain/learning path is built, or when a question-answer result needs diagnosis against the wiki, to find whether issues come from compilation, routing, or reasoning and to patch the knowledge base.
version: 1.1.1
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [llm-wiki, audit, knowledge-base, compile, routing, reasoning, qa]
    category: research
    related_skills: [llm-wiki]
---

# LLM Wiki Audit and Optimization

## Overview

Use this skill to review whether an LLM Wiki has really become a usable knowledge engine, rather than a pile of organized markdown files.

This skill audits the full chain:

1. **Compile** — whether raw sources were transformed into durable, structured, evidence-backed knowledge pages.
2. **Route** — whether an Agent can find the right pages through indexes, learning paths, wikilinks, and usage templates.
3. **Reason** — whether answers generated from the wiki actually follow the right pages, cases, evidence, and decision logic.

The goal is not only to report problems. When appropriate, propose or directly apply concrete wiki optimizations: better indexes, clearer module boundaries, stronger agent-use templates, missing evidence anchors, case-transfer rules, or new queries/playbooks.

## When to Use

Use this skill when the user asks things like:

- “检查这个 LLM Wiki 的编译质量。”
- “审阅一下 品牌策略 这个知识库是否好用。”
- “这个知识库已经建好了，帮我看编译/路由有没有问题。”
- “这是我的问题和 AI 答案，帮我判断是知识库问题、路由问题还是推理问题。”
- “这个回答不太对，帮我反查 LLM Wiki 链路。”
- “帮我优化这个知识库，让它更适合 Agent 调用。”

Use after `llm-wiki-ingest` or other ingestion workflows have created pages and the user wants quality review.

Do **not** use this as the primary ingest skill. If the task is to process a new source into the wiki, first use the relevant ingest skill, then use this skill as QA/optimization.

## Core Mental Model

Traditional RAG optimizes “retrieve the right chunks.”

LLM Wiki optimizes “compile sources into good knowledge before the query happens.”

Therefore, if an LLM Wiki answer is poor, first inspect:

1. **Compilation quality** — did the wiki compile the source into correct, deep, structured knowledge?
2. **Routing quality** — did the question find the right domain, learning path, chapter, case, and template pages?
3. **Reasoning quality** — did the answer use those pages correctly and fit the user's actual situation?

A useful shorthand:

```text
Answer quality = Compile quality × Route quality × Reason quality
```

## Required Orientation

Before auditing a wiki, orient yourself:

1. Read `~/wiki/AGENTS.md` if present.
2. Read `~/wiki/SCHEMA.md`.
3. Read `~/wiki/index.md`.
4. Read recent `~/wiki/log.md`.
5. For a domain audit, read the domain index, e.g. `domains/品牌策略/index.md`.
6. For a learning-path audit, read the path `index.md` and 2-4 representative chapter pages, including the final Agent/template page if present.
7. Search for key terms if the target is large.

Never judge a wiki only from a file listing. The audit must inspect structure, content, and routing artifacts.

## Operating Modes

## Mode A — Domain / Wiki Compile-Route Audit

Use when the user asks to audit a whole wiki, domain, or learning-path after it was built.

Examples:

- Audit `/Users/pechen/wiki/domains/品牌策略`.
- Audit one learning path such as `brand-differentiation-perception-system`.
- Review a newly ingested transcript set after formal pages were created.

### Steps

1. **Map the target**
   - Target path
   - Domain
   - Number of markdown pages
   - Index pages
   - Learning paths
   - Agent-use/template pages

2. **Placeholder / shell-page scan (RUN THIS FIRST — fast, mechanical, high-ROI)**

   Before any human-judgment reading, run a mechanical scan for **compile shells**:
   pages that look ingested (correct title, frontmatter, agent-template scaffold) but
   whose body is template boilerplate with the real knowledge missing. This is the most
   common silent failure of batch ingestion — a whole learning path can pass a naive
   audit because the file count, titles, and indexes all look right while every body is
   a clone of the same placeholder.

   Why it must run first: human reading samples a few pages and is easily fooled by good
   titles/structure. A diff-based scan inspects 100% of pages in seconds and catches the
   exact thing sampling misses.

   Detection signals (any one is enough to flag a page as a suspected shell):
   - **Duplicate-body fingerprint**: two or more pages share a normalized body
     (whitespace-collapsed, frontmatter/title stripped). Identical bodies across
     different chapters ≈ template boilerplate, not real knowledge.
   - **Known boilerplate phrases** still present in formal pages, e.g.
     `本节用于把课程中的口头经验重构成稳定的方法框架`,
     `请基于本节方法，分析当前品牌/产品/视觉材料是否存在同类问题`,
     `内容待补充`, `（占位）`, `占位内容`, `TODO:`, `TBD`, `<!-- placeholder`.
     Use the precise marker forms above, NOT bare words — see the marker-precision
     pitfall below for why `占位` / `TBD` / `TODO` alone must never be used.
   - **Thin body**: formal chapter page (not an index) whose body after stripping
     frontmatter/title/headings is below ~500 bytes, or whose only substantive content
     is a single one-sentence conclusion with no reasoning chain, case, or evidence.
   - **No evidence anchors**: a chapter that should carry cases/numbers (per its title)
     contains zero brand names, numbers, or contrasts.

   Run the helper script:

   ```bash
   python3 <skill-root>/scripts/placeholder_scan.py <target_dir>
   ```

   It prints, per page: byte size, normalized-body hash, duplicate-group id, boilerplate
   hits, and a SHELL/THIN/OK verdict. Treat any SHELL or large duplicate group as P0.

   **Marker-precision pitfall (false positives bite both ways).** When extending the
   boilerplate marker list (`BOILERPLATE_CJK` / `BOILERPLATE_ASCII` in the script), never
   add bare ambiguous tokens. Two failure modes, both observed in practice:
   - A bare CJK word collides with real prose: `占位` fires inside `心智占位`
     ("occupy mind-share"), wrongly flagging a good brand-strategy page. Use a marker
     FORM that cannot occur in prose — `（占位）`, `占位内容`, `此处占位` — not `占位`.
   - A bare ASCII token matches as a substring: `TBD` fires inside `JTBD`
     (Jobs-to-be-Done), `TODO` inside longer identifiers. ASCII markers must be matched
     on word boundaries (`\bTBD\b`) or with required punctuation (`TODO[:：]`), which is
     why the script keeps CJK markers (plain substring) and ASCII markers (regex word
     boundary) in separate lists. Validate any new marker by running the scan on a path
     you KNOW is fully compiled and confirming it still reads OK — a precise probe must
     produce zero false positives on good pages, not just catch the shells.

   If the script is unavailable, do the same scan manually:
   - `search_files` for each known boilerplate phrase across the target; a phrase that
     hits N pages means N suspected shells.
   - List pages by byte size; cluster the suspiciously-small, equal-sized ones.

   Record the shell inventory (which paths, how many pages, which course/source they came
   from) before continuing — it reframes the rest of the audit (a shell path's routing and
   reasoning scores are moot until it is recompiled).

3. **Compile audit**
   Check whether sources became durable knowledge:
   - Are pages formal knowledge, not cleaned transcript summaries?
   - Are core concepts, frameworks, cases, evidence anchors, and decision criteria preserved?
   - Do pages contain reasoning chains, not only conclusions?
   - Are major cases transformed into transfer rules?
   - Are important numbers and proof points preserved or classified as omissions?
   - Are raw sources and extraction notes traceable?

4. **Route audit**
   Check whether an Agent can find the right knowledge:
   - Does the main/domain index show a clear map?
   - Are learning paths ordered and readable?
   - Are module boundaries clear?
   - Are chapter titles human-readable and problem-oriented?
   - Are there Agent-use templates or diagnostic entry points?
   - Are there duplicate or overlapping pages that confuse routing?

5. **Reasoning readiness audit**
   Check whether pages support actual decision-making:
   - Can the wiki answer “which module should I use for this problem?”
   - Are applicability conditions clear?
   - Are non-transferable caveats clear?
   - Are cases connected to decisions, not only described?
   - Are outputs/action templates available?

6. **Score and classify issues**
   Use the report template in `templates/compile-route-audit-report.md`.

7. **Optimization plan**
   Provide prioritized fixes:
   - P0: blocks trustworthy use
   - P1: materially improves answer quality
   - P2: nice-to-have structure/readability improvements

8. **Patch when requested or obviously low-risk**
   If the user asked to optimize, edit wiki files directly and verify.

## Mode B — Question + Answer Chain Audit

Use when the user provides:

1. A question/query.
2. An AI answer.
3. The target wiki/domain/path.

The goal is to answer:

> Did this answer fail because the knowledge was compiled badly, routed badly, or reasoned badly?

### Steps

1. **Parse the user question**
   Identify:
   - Task type: diagnosis, planning, comparison, decision, generation, critique.
   - Required domain/module.
   - Expected output type.
   - Business constraints present/missing.

2. **Inspect the answer**
   Check:
   - What claims did it make?
   - What framework did it appear to use?
   - What cases/examples did it cite or imply?
   - Did it produce an actionable result?

3. **Find the expected route**
   From the wiki, determine which pages should have been used:
   - Domain index
   - Learning path index
   - Core chapters
   - Case pages
   - Agent-use templates
   - Relevant queries/playbooks

4. **Compare actual vs expected route**
   Classify:
   - Correct route
   - Partial route
   - Wrong route
   - No visible wiki route / generic answer

5. **Assess knowledge grounding**
   Determine whether the answer is:
   - Strongly grounded in wiki pages
   - Weakly grounded / uses only generic concepts
   - Ungrounded / model free-play
   - Contradicts the wiki

6. **Diagnose failure source**
   Assign one or more:
   - `compile-gap`: needed knowledge not compiled or too shallow
   - `route-gap`: knowledge exists but indexes/templates do not guide the agent there
   - `reasoning-gap`: right knowledge was available/routed but applied incorrectly
   - `input-gap`: user question lacked key business constraints
   - `template-gap`: no Agent-use template exists for the task

7. **Recommend fixes**
   Output both answer-level and wiki-level fixes.

Use `templates/question-answer-chain-audit.md`.

## Mode C — Obsidian Route Audit

Use when the user asks whether a wiki, domain, learning path, or newly ingested page is findable by agents, or after `llm-wiki-ingest` completes formal pages.

This mode is mechanical and route-focused. It does not replace compile-quality reading.

### Steps

1. Orient with `AGENTS.md`, `SCHEMA.md`, `index.md`, and recent `log.md`.
2. Identify target entry pages: query page, domain index, learning-path index, Agent-use template, or new formal pages.
3. Run the shared route audit helper when available:

```bash
python3 /Users/pechen/.codex/skills/.llmwiki-source/shared/scripts/wiki_cli_route_audit.py <target-page.md>
```

4. If Obsidian CLI is unavailable or active vault does not match `/Users/pechen/wiki`, use the helper's degraded filesystem report and state that global Obsidian signals were not trusted.
5. Inspect:
   - unresolved links
   - target backlinks
   - outgoing wikilinks
   - outline availability
   - whether target appears in relevant `index.md`, `queries/`, or Agent usage template pages
6. Classify route issues:
   - P0: target has no route from index/query/template or is a shell/thin page
   - P1: target is reachable but lacks outgoing links, usage template, or clear outline
   - P2: tag/property/index wording could improve discovery
7. Recommend or patch route fixes when requested.

## Mode D — Post-Ingest QA

Use after a new source was ingested into the wiki.

Check:

- Raw source exists.
- Extraction notes exist.
- Formal pages exist.
- Index/log updated.
- Coverage/omission audit exists.
- Human-facing titles are readable.
- Important evidence anchors are integrated into reasoning, not appended as fact lists.
- Agent-use template exists when the topic is meant to support future tasks.

This mode is especially important after batch transcript ingestion.

## Mode D — Long-Term Wiki Health Audit

Use periodically when a wiki grows large.

Check:

- Orphan pages.
- Broken wikilinks.
- Missing index entries.
- Duplicate/overlapping pages.
- Domain boundary drift.
- Outdated pages.
- Stale Agent-use templates.
- Raw sources that never made it into formal pages.

This mode overlaps with general `llm-wiki` linting but is more focused on usefulness for AI answer generation, not just structural hygiene.

## Compile Audit Checklist

Score each 1-5.

0. **No placeholder shells (gate, pass/fail not 1-5)** — Did the step-2 scan find zero duplicate-body groups, zero leftover boilerplate phrases, and no thin formal pages? If this fails, the path's other scores are not meaningful until recompiled.
1. **Source-to-knowledge transformation** — Is the output more than a cleaned source summary?
2. **Depth of reasoning** — Does it preserve why/how, not only conclusions?
3. **Evidence preservation** — Are key cases, numbers, contrasts, and proof points retained?
4. **Case transferability** — Are cases turned into applicability rules?
5. **Module boundaries** — Does each page/learning path have a clear responsibility?
6. **Decision process** — Does the wiki show what to judge first, second, and third?
7. **Template readiness** — Are there prompts/checklists/output formats for agents?
8. **Traceability** — Can claims trace back to source/raw/extraction notes?
9. **Noise removal** — Has source/classroom/platform noise been removed from formal pages?
10. **Actionability** — Can this knowledge support a real task, not just reading?

## Routing Audit Checklist

Check:

- Main index has target domain with meaningful one-line descriptions.
- Domain index groups pages into task-relevant modules.
- Learning path index exists and has ordered chapter links.
- If the domain contains many reusable cases, a case library/index exists and
  maps problem types to cases.
- Page titles are Chinese/human-readable and problem-oriented.
- Agent-use template pages are easy to find.
- Related pages and wikilinks guide cross-domain use.
- Similar pages are not duplicated without relationship notes.
- There is a clear path from broad user task to relevant chapter(s).

Common routing defects:

- `index.md` lists files but does not explain when to use them.
- Pages are over-fragmented, causing the Agent to read too little context.
- Pages are under-fragmented mega-pages, causing the Agent to miss the right section.
- Learning paths have no final Agent-use template.
- Titles are raw slugs, not business-readable concepts.

## Reasoning Audit Checklist

For a question/answer pair:

- Was the user question classified into the right problem type?
- Were the correct wiki modules selected?
- Did the answer follow the wiki's decision order?
- Did it use relevant cases as analogies rather than decorations?
- Did it preserve important conditions and caveats?
- Did it cite or name the supporting wiki pages when useful?
- Did it hallucinate outside the wiki when the task required wiki grounding?
- Did it ask for missing business inputs when the answer depends on them?
- Did it produce a useful next action, not only analysis?

## Diagnosis Labels

Use these labels in reports:

- `compile-shallow` — pages are too summary-like.
- `compile-placeholder` — pages are template/boilerplate shells: real knowledge never landed in the body (duplicate bodies, leftover scaffold phrases, thin one-line content). Always P0 — these pages are worse than missing because indexes and titles make them look complete, so an Agent will route to them and free-play. Detect with the step-2 placeholder scan.
- `compile-scattered` — knowledge exists but lacks a coherent structure.
- `compile-omission` — important anchors/cases/evidence are missing.
- `compile-biased` — content is placed under the wrong module or distorted.
- `route-missing-index` — page exists but is not discoverable from index.
- `route-boundary-conflict` — two modules overlap in confusing ways.
- `route-template-gap` — no Agent-use template for a common task.
- `reasoning-wrong-module` — answer used the wrong knowledge module.
- `reasoning-case-misuse` — answer used a case analogy incorrectly.
- `reasoning-unsupported-claim` — answer made claims not supported by the wiki.
- `input-insufficient` — the user question lacks required business context.

## Output Rules

A good audit report should be concrete and path-based.

Always include:

- Target path.
- Pages inspected.
- What is already good.
- Issues by Compile / Route / Reason.
- Prioritized fixes.
- Whether direct patches were applied.
- If no patch was applied, exact files/sections to edit next.

Avoid vague statements like “结构还可以加强.” Instead say:

> `domains/品牌策略/index.md` lists learning paths but does not yet classify them by user problem type. Add a “按品牌策划问题调用” section mapping 感知问题 / 大单品问题 / 拓品问题 to the relevant pages.

## Direct Optimization Rules

If the user asks to optimize, make low-risk patches directly:

- Add missing index descriptions.
- Add a “When to use this page” section.
- Add or strengthen an Agent-use template.
- Add a route map from problem type to pages.
- Add missing evidence anchors if source/extraction notes are available.
- Add wikilinks between sibling modules.
- Split or flag pages that are too broad.

Do not silently rewrite large knowledge pages unless the user asked for deep restructuring. For major rewrites, provide a plan first.

## Verification Checklist

Before final reply:

- [ ] Orientation files read.
- [ ] Placeholder/shell scan run (step 2) — duplicate-body groups, boilerplate phrases, and thin pages checked across 100% of target pages.
- [ ] Target pages inspected, not just listed.
- [ ] Compile / Route / Reason all addressed.
- [ ] If a question-answer pair was given, expected route compared to actual answer.
- [ ] Issues labeled with diagnosis labels.
- [ ] Prioritized fixes listed.
- [ ] Any patches verified with `read_file` or search.
- [ ] If wiki files changed, `index.md` / `log.md` update considered when appropriate.
- [ ] If committing is appropriate, stage only relevant files.

## Relationship to Other Skills

- Use `llm-wiki` for general wiki ingest/query/lint.
- Use `llm-wiki-ingest` to build knowledge pages from course transcripts, API docs, web clippings, books, and mixed sources.
- Use `douyin-link-to-knowledge` to ingest Douyin videos.
- Use this skill after those build skills to audit whether the result is actually useful for AI tasks.

## Minimal User Prompts

Whole-domain audit:

> 请用 llm-wiki-audit-and-optimization 审查 `/Users/pechen/wiki/domains/品牌策略` 的编译和路由质量。

Question-answer audit:

> 请用 llm-wiki-audit-and-optimization 检查下面这个问题和回答，判断问题出在编译、路由还是推理。

Post-ingest audit:

> 请用 llm-wiki-audit-and-optimization 检查刚才这次课程入库是否真正编译成可调用知识。
