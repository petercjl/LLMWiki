---
name: llm-wiki-ingest
description: Unified and only LLM Wiki ingestion skill for Peter's /Users/pechen/wiki. Use for any source that should be compiled into the wiki, including Obsidian Clippings, webpages, books, EPUB/PDF, course transcripts, meeting transcripts, API docs, XMind files, spreadsheets, markdown docs, product/tool docs, PPT/courseware, and unknown source types. Enforces memory-first classification, fusion with existing knowledge, lossless knowledge-unit coverage, raw preservation, extraction notes, formal pages, index/log updates, Obsidian route audit, and audit handoff.
---

# LLM Wiki Ingest

## Purpose

This is the single entry skill for compiling sources into Peter's LLM Wiki at `/Users/pechen/wiki`.

Legacy standalone entries are intentionally removed. If the user names
`api-docs-wiki-ingest`, `wiki-clippings-ingest`, `book-to-llm-wiki`, or
`course-transcript-to-knowledge`, handle the request here with the relevant adapter.

Use this skill instead of source-specific ingest skills when the user asks to:

- process `/Users/pechen/wiki/Clippings`
- ingest webpages, product docs, API docs, books, transcripts, XMind, spreadsheets, reports, Markdown files, PDFs, EPUBs, or mixed sources
- ingest PPT/courseware content as a source for durable knowledge
- make a source "入脑"
- compile a source into reusable wiki knowledge
- build extraction notes, coverage matrix, formal pages, index entries, and log entries

## Non-Negotiable Standard

Wiki ingestion is not summarization, abbreviation, or takeaway extraction.

Wiki ingestion is also not source filing. Peter's wiki is a personal memory
system: new material must be absorbed into the existing knowledge structure
whenever possible. A course, book, transcript, meeting, web clipping, or report
is the acquisition path; the final formal knowledge belongs under the content
domain where Peter will later look for it.

Every meaningful source unit must be preserved at the knowledge-unit level. A meaningful source unit can be a heading, paragraph claim, table row, code block, API field, example, case, formula, diagram meaning, image with information, XMind node, transcript micro-segment, Q&A point, limitation, caveat, decision rule, operational step, or pricing/parameter value.

For each source unit, record exactly one disposition:

- `formalized`: represented in formal wiki pages.
- `merged`: integrated into another broader formal unit.
- `raw-only`: preserved only in raw because it is duplicate, decorative, legal/frontmatter noise, or low knowledge value.
- `omitted-with-reason`: intentionally omitted with a concrete reason.
- `unresolved`: requires user judgment, current-source verification, or missing context.

The final wiki may be longer than a summary. It should reconstruct implicit logic, add interpretation, relationship maps, decision criteria, examples, Agent-usable templates, caveats, and cross-links. Enrichment must never replace source coverage: first preserve the source's knowledge units, then enrich.

## Memory-First Placement And Fusion

Before planning formal pages, perform a classification and fusion gate.

### 0.1 Classify The Knowledge Domain

Identify the durable content domain before deciding file paths. Peter's wiki is
broad and may include, among others:

- ecommerce operations, including platform-specific knowledge such as Taobao,
  Douyin, Xiaohongshu, JD, Pinduoduo, and general ecommerce methods
- tax, finance, accounting, equity, incentives, and strategic finance
- visual production, ecommerce images, video, design systems, and aesthetics
- brand strategy, positioning, product strategy, and consumer mind
- AI application development, agents, tools, prompts, workflows, and automation
- personal interest knowledge such as Daoism, Buddhism, philosophy, health, or
  other long-lived learning areas

If the source crosses domains, split or cross-link by concept. Do not force all
formal output under the source's original course/book directory.

### 0.2 Search Existing Memory Before Creating Pages

Search existing pages for the source title, core concepts, synonyms, Chinese
terms, English terms, brands, platforms, tools, formulas, and cases.

For every planned formal page, choose one disposition:

- `merge-into-existing`: add, refine, or correct an existing page.
- `extend-existing-with-section`: add a new section to an existing page.
- `split-existing`: existing page is too broad; create a clearer subpage and
  update links.
- `create-new`: no suitable existing page exists.
- `source-package-only`: keep a source map, course map, or audit trail, but do
  not make it the main knowledge home.

When the choice is ambiguous or would reorganize important knowledge, ask Peter
to confirm the classification and merge plan before editing.

### 0.3 Human-Facing Chinese Names

Use Chinese titles and Chinese index labels by default for formal knowledge
pages, because Peter navigates and reviews the wiki in Chinese. English slugs
can remain in frontmatter (`slug`, `aliases`) or transitional filenames, but
new or renamed human-facing knowledge should be Chinese-readable. Avoid
creating a large English-only directory tree for Chinese knowledge.

When a folder or page belongs to an ordered learning/navigation sequence, add a
numeric prefix to the filename, such as `01-基础概念/`,
`02-业务模型/`, or `03-风险与例外.md`. The number is part of the
navigation contract, not decoration: choose it so Peter can tell which file to
read first in Obsidian or any plain file browser.

### 0.4 Associative Fusion

Do not destroy an older knowledge structure merely because a new source overlaps
with it. If the old page still has its own context or curriculum value, preserve
it and connect the new durable page through:

- a "相关记忆" or "Related memory" section on the new page
- backlinks from old indexes where useful
- source/course package indexes that point to the durable domain pages
- short notes explaining how the old knowledge confirms, extends, or constrains
  the new synthesis

Use destructive merging only when two pages are genuinely duplicate theories and
Peter has confirmed the merge.

### 0.5 Source Packages Are Secondary

Use `raw/` and `_meta/extraction-notes/` for source preservation and audit.
If a course/book needs a navigable source-oriented overview, place it in a
source/course package area such as `source-packages/`, `course-packages/`, or a
Chinese equivalent like `课程包/`. The package should point to the formal domain
pages; it should not become the only home of the knowledge.

## Required Orientation

Before editing the wiki:

1. Read `/Users/pechen/wiki/AGENTS.md`.
2. Read `/Users/pechen/wiki/SCHEMA.md`.
3. Read `/Users/pechen/wiki/index.md`.
4. Read recent `/Users/pechen/wiki/log.md`.
5. Search existing wiki pages for source title, product names, concepts, APIs, brands, model IDs, and major keywords.
6. When available, run Obsidian CLI search probes for source title and core concepts. Use `<LLMWiki repo>/shared/scripts/wiki_cli_search.py` or the commands in `<LLMWiki repo>/shared/references/obsidian-cli-protocol.md`.
7. Run `git -C /Users/pechen/wiki status --short` and avoid reverting unrelated work.

If the task will create or modify more than 10 wiki files, present a short execution plan before editing unless the user already approved a batch run.

## Source Adapter Selection

Read `references/source-adapter-map.md`, then load only the relevant adapter:

| Source | Adapter |
| --- | --- |
| Obsidian Web Clipper / webpage / Clippings | `adapters/web-clipping.md` |
| API docs / developer docs / endpoint docs | `adapters/api-docs.md` |
| EPUB/PDF/book manuscript | `adapters/book.md` |
| course/audio/meeting transcript | `adapters/transcript.md` |
| XMind or mind map | `adapters/xmind.md` |
| spreadsheet/CSV/report/table-heavy source | `adapters/spreadsheet-report.md` |
| PPT/courseware/slide-derived source | `adapters/markdown-doc.md` plus transcript adapter when paired with spoken content |
| local Markdown/doc/manual | `adapters/markdown-doc.md` |
| unknown or mixed source | `adapters/unknown-source.md` |

If more than one adapter applies, use the most specific one first. For example, an API doc captured through Obsidian Clipper uses `web-clipping.md` for raw queue handling and `api-docs.md` for knowledge modeling.

For book/EPUB tasks, `adapters/book.md` is the authority. It has book-specific references under `references/book/` and deterministic EPUB scripts under `scripts/book/`. Do not fall back to the removed `book-to-llm-wiki` entry.

For API docs, use `adapters/api-docs.md`, `references/api-docs/`, and `scripts/api/compile_api_reference.py`.

For Obsidian Clippings or web captures, use `adapters/web-clipping.md` and `references/web-clipping/`.

For course/audio transcript reconstruction, use `adapters/transcript.md` and `references/transcript/`.

## Universal Workflow

### 1. Source Intake

Create a source profile with:

- source title and slug
- source path or URL
- source type and adapter
- publication/update/capture date
- language
- domain placement candidate and alternative candidates
- existing pages found during memory search
- proposed fusion disposition: merge, extend, split, create, or source-package-only
- sensitivity check
- time-sensitivity/current-doc check requirement
- expected formal artifacts

### 2. Raw Preservation

Archive raw source under the correct `raw/` path before formal writing:

```text
raw/webpages/<provider-or-topic>/
raw/api/<provider>/
raw/books/<book-slug>-<year>/
raw/transcripts/
raw/data/
raw/assets/
```

Do not edit raw after archiving except mechanical filename/path fixes before logging.

### 3. Source Inventory

Build an inventory of all source units before writing final pages.

For small sources, the inventory may be inside `coverage-checklist.md`.
For large sources, create:

```text
_meta/extraction-notes/<source-slug>/
├── source-profile.md
├── source-inventory.md
├── knowledge-unit-inventory.md
├── coverage-matrix.md
├── omission-audit.md
├── formal-page-plan.md
└── audit-handoff.md
```

Use `references/coverage-contract.md` for required columns and dispositions.

### 4. Knowledge Unit Extraction

Extract all meaningful source units into reusable knowledge units:

- concepts and definitions
- claims and reasoning chains
- rules, formulas, thresholds, parameters
- APIs, request/response fields, code examples
- cases, examples, screenshots, diagrams, media prompts
- workflows, procedures, checks, failure modes
- limitations, caveats, context constraints
- open questions and verification needs

### 5. Knowledge Architecture

Plan formal pages by future Agent usability, not by source shape alone.

Choose artifact types:

- domain index update
- concept page
- tool/entity card
- capability map
- rule matrix
- playbook/checklist
- learning path
- API reference manual
- source-summary
- query entry page
- decision page
- troubleshooting page

Do not create many thin pages. Do not create one giant page that prevents routing. Use as many pages as needed for complete, coherent, Agent-usable knowledge.

### 6. Formal Compilation

Formal pages must:

- include YAML frontmatter matching `/Users/pechen/wiki/SCHEMA.md`
- cite raw source and extraction notes in `sources`
- use `[[wikilinks]]`
- preserve all meaningful source knowledge or link to coverage records
- integrate examples/cases into reasoning, not append disconnected fact lists
- include decision rules, templates, checklists, or code snippets when useful
- mark time-sensitive claims and outdated-risk
- be readable by future agents without reopening raw for normal use

Read `references/formal-page-standards.md` before writing formal pages.

### 7. Index, Log, and Cleanup

Update:

- domain/project/shared index where relevant
- `/Users/pechen/wiki/index.md`
- `/Users/pechen/wiki/log.md`

Only delete a queue item such as a Clippings file after:

- raw source exists
- formal knowledge exists or source is explicitly raw-only
- coverage/omission record exists
- index/log are updated

### 8. Audit Handoff

Every ingest must create or update:

```text
_meta/extraction-notes/<source-slug>/audit-handoff.md
```

Use `references/audit-handoff-contract.md`. This file is the interface with `llm-wiki-audit-and-optimization`.

### 9. Self-Validation

Before final response:

1. Run `scripts/validate_ingest_contract.py` with source slug or paths when possible.
2. Run placeholder scan on formal output when available:

```bash
python3 <llm-wiki-audit-and-optimization-skill>/scripts/placeholder_scan.py <formal_path>
```

3. Run Obsidian route audit when the shared LLMWiki repo is available:

```bash
python3 /Users/pechen/.codex/skills/.llmwiki-source/shared/scripts/wiki_cli_route_audit.py <new-entry-page.md>
```

If the active Obsidian vault is not `/Users/pechen/wiki`, treat the script's degraded filesystem checks as partial route validation and say so.

4. `rg` representative source terms across formal pages.
5. Verify every `formalized` source unit has a target page.
6. Verify every raw-only or omitted source unit has a reason.

## Audit Skill Coordination

After ingest, `llm-wiki-audit-and-optimization` should be able to run without rediscovering the whole job.

The ingest skill must hand off:

- raw source path
- adapter used
- formal pages created/updated
- source inventory path
- coverage matrix path
- omission audit path
- audit handoff path
- known unresolved items
- expected future Agent use cases

The audit skill checks two primary concerns:

1. **Completeness**: whether source knowledge was fully represented or explicitly classified.
2. **Agent usability**: whether compiled pages are easy for future AI agents to route to, read, and apply.

## Output Report

End with:

- source processed
- adapter(s) used
- raw files created/moved
- extraction notes created
- formal pages created/updated
- index/log updates
- coverage result
- validation result
- audit handoff path
- any unresolved items

Keep the chat report concise; do not paste full formal pages.

## Migration Policy For Removed Entries

Older source-specific entries have been removed as standalone skills. Their capabilities live here:

- `wiki-clippings-ingest` -> `llm-wiki-ingest` + `web-clipping` adapter
- `book-to-llm-wiki` -> `llm-wiki-ingest` + `book` adapter
- `course-transcript-to-knowledge` -> `llm-wiki-ingest` + `transcript` adapter
- `api-docs-wiki-ingest` -> `llm-wiki-ingest` + `api-docs` adapter
- `llm-wiki-recompile-runner` remains a separate repair orchestrator and calls this skill's adapters.

Do not recreate compatibility wrapper skills. If a user names an older entry, route the task to this skill and the matching adapter.
