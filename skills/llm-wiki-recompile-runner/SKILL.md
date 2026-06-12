---
name: llm-wiki-recompile-runner
description: Orchestrate repair of existing LLM Wiki domains or learning paths that contain shell/thin pages. Use after an audit finds placeholder pages, incomplete extraction notes, stale index status, or raw transcripts that need to be recompiled into usable formal knowledge pages. Coordinates llm-wiki-audit-and-optimization and llm-wiki-ingest transcript adapter, then verifies post-ingest quality.
---

# LLM Wiki Recompile Runner

## Purpose

Repair an existing LLM Wiki domain or learning path whose files exist but are not yet usable knowledge.

This skill is a runner, not the compiler itself:

- Use `llm-wiki-audit-and-optimization` to locate shell/thin/routing defects.
- Use `llm-wiki-ingest` with `adapters/transcript.md` to recompile raw transcripts into formal pages.
- Use this skill to sequence the work, track coverage, and decide when a path is ready for downstream skills.

## Use When

Use this skill when the user says:

- “这个知识库有 shell page，先修知识库。”
- “先审计，再从 raw transcript 重新编译。”
- “把这个 domain 收尾到可以给 Agent 调用。”
- “暂停业务 skill，先把知识库处理好。”
- “用 skill 处理知识库，而不是在对话里临时修。”

Do not use this for brand/report generation. This skill stops at knowledge-base repair and verification.

## Required Inputs

At least one of:

- Target domain path, e.g. `/Users/pechen/wiki/domains/brand-strategy`
- Target learning path
- A shell inventory from `placeholder_scan.py`

Useful optional inputs:

- Raw transcript path under `/Users/pechen/wiki/raw/transcripts`
- Extraction note path under `/Users/pechen/wiki/_meta/extraction-notes`
- Downstream use case, e.g. “brand planning report skill”

## Workflow

### 1. Orient

Before editing the wiki:

1. Read `/Users/pechen/wiki/AGENTS.md` if present.
2. Read `/Users/pechen/wiki/SCHEMA.md`.
3. Read `/Users/pechen/wiki/index.md`.
4. Read recent `/Users/pechen/wiki/log.md`.
5. Read the target domain `index.md`.

### 2. Mechanical Shell Audit

Run:

```bash
python3 <llm-wiki-audit-and-optimization-skill>/scripts/placeholder_scan.py <target_path>
```

Classify results:

- `SHELL`: P0. Do not use as source for downstream tasks.
- `THIN`: manual depth audit required.
- `OK`: still needs sampling if downstream use is high-stakes.

Record:

- total pages
- shell count
- thin count
- OK count
- shell pages grouped by learning path

### 3. Match Shell Paths To Sources

For each shell learning path, find:

- formal page directory
- raw transcript path
- extraction notes path
- existing index files
- source references in frontmatter

If raw transcript is missing, stop and report the blocker.

If extraction notes are missing or only contain empty planning files, treat the path as needing full recompile, not a light patch.

### 4. Decide Repair Mode

Use one of three modes:

| Mode | Use When | Action |
| --- | --- | --- |
| Full recompile | Formal pages are shell and extraction notes are empty/incomplete | Re-run `llm-wiki-ingest` transcript adapter from raw transcript |
| Formal synthesis repair | Extraction notes are complete but formal pages are shallow | Re-synthesize formal pages from extraction notes |
| Routing/status repair | Pages are complete but index/status/routes are stale | Patch indexes, links, and agent-use templates |

Do not “patch around” shell pages by adding a few paragraphs. Shell pages usually indicate the raw-to-formal pipeline failed.

### 5. Recompile One Learning Path At A Time

For each learning path:

1. Use `llm-wiki-ingest` transcript adapter rules.
2. Preserve raw transcript unchanged.
3. Create or rebuild extraction notes:
   - `segment-plan.md`
   - `micro-segment-plan.md`
   - `coverage-matrix.md`
   - `segment-knowledge-inventory.md`
   - `micro-segments/` for large transcripts
4. Rebuild formal learning-path pages.
5. Remove classroom/source language from formal pages.
6. Preserve cases, numbers, decision criteria, and transfer rules.
7. Update the learning-path `index.md`.

### 5.1 Transcript With Built-In Summary

Some Get/Feishu transcript files already contain `智能总结`, `章节概要`, `金句精选`, and
then the full `原文`. In this case:

- Use `章节概要` as the first-pass segment plan.
- Delete classroom/logistics segments from the formal knowledge plan, but record them as omitted in coverage notes.
- Treat `智能总结` as a map, not as the final source of truth.
- Verify important concepts, cases, numbers, and claims against the full `原文` before writing formal pages.
- If the existing extraction notes only repeat generic planning language and do not contain micro-segments, rebuild them. Do not treat a four-file empty note set as complete.
- For very large transcripts, it is acceptable to make one micro-segment per durable knowledge unit or formal chapter when the built-in summary is already chapterized, as long as the coverage matrix records what was kept, merged, or omitted.

For large transcript paths, do not try to repair multiple paths in one pass unless the user explicitly accepts staged execution.

### 6. Post-Ingest QA

After each learning path repair:

1. Run `placeholder_scan.py` on the repaired path.
2. Read 2-4 representative pages, including an Agent-use/template page.
3. Verify:
   - no shell pages
   - formal pages have reasoning chains
   - cases and evidence anchors are integrated into the method
   - extraction notes can trace source coverage
   - page titles and section headings are human-readable
   - downstream agents can route to the path

If the path still has shell pages, do not proceed to downstream business skill work.

### 7. Domain Status Update

Only after a path passes QA:

- Update domain index status.
- Update wiki index if relevant.
- Append `/Users/pechen/wiki/log.md`.
- Note what raw transcript and extraction notes were used.

For partially repaired domains, mark each learning path separately. Do not mark the whole domain complete if any P0 shell path remains.

## Output

Return:

- repaired paths
- remaining P0/P1/P2 issues
- raw transcript sources used
- extraction notes created or reused
- verification commands and results
- whether the domain is ready for downstream skill creation

## Rules

- Do not continue downstream report/brand/planning skill implementation while required source knowledge paths still have P0 shell pages.
- Do not overwrite raw transcripts.
- Do not delete existing formal pages unless replacing shell output with a complete recompile.
- Do not present internal extraction notes as user-facing knowledge.
- If the repair is too large for one turn, finish one learning path completely and leave a clear continuation record.

## Brand Strategy Current Known Case

As of 2026-06-06, `/Users/pechen/wiki/domains/brand-strategy` has been repaired from the
previous 31-page shell baseline.

The latest mechanical audit result is:

```text
Scanned: 88 markdown pages
SHELL: 0   THIN: 0   OK: 88
```

The repaired learning paths were:

- `brand-visual-memory-perception-and-visualization-system`
- `ecommerce-brand-mindshare-product-power-and-hero-product-strategy`
- `brand-big-single-product-and-product-planning-marketing`

If future audits find new shell pages, treat this section as a historical baseline, not as a
current defect inventory.
