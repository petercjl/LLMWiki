---
name: llm-wiki-ingest
description: Unified and only LLM Wiki ingestion skill for the user's $WIKI_ROOT. Use for any source that should be compiled into the wiki, including Obsidian Clippings, webpages, books, EPUB/PDF, course transcripts, meeting transcripts, API docs, XMind files, spreadsheets, markdown docs, product/tool docs, PPT/courseware, and unknown source types. Enforces memory-first classification, fusion with existing knowledge, lossless knowledge-unit coverage, raw preservation, extraction notes, formal pages, index/log updates, Obsidian route audit, and audit handoff.
---

# LLM Wiki Ingest

## Purpose

This is the single entry skill for compiling sources into the wiki owner's LLM Wiki at `$WIKI_ROOT`.

Legacy standalone entries are intentionally removed. If the user names
`api-docs-wiki-ingest`, `wiki-clippings-ingest`, `book-to-llm-wiki`, or
`course-transcript-to-knowledge`, handle the request here with the relevant adapter.

Use this skill instead of source-specific ingest skills when the user asks to:

- process `$WIKI_ROOT/Clippings`
- ingest webpages, product docs, API docs, books, transcripts, local audio/video courses, XMind, spreadsheets, reports, Markdown files, PDFs, EPUBs, or mixed sources
- ingest PPT/courseware content as a source for durable knowledge
- make a source "入脑"
- compile a source into reusable wiki knowledge
- build extraction notes, coverage matrix, formal pages, index entries, and log entries

## Non-Negotiable Standard

Wiki ingestion is not summarization, abbreviation, or takeaway extraction.

Wiki ingestion is also not source filing. The wiki owner's wiki is a personal memory
system: new material must be absorbed into the existing knowledge structure
whenever possible. A course, book, transcript, meeting, web clipping, or report
is the acquisition path; the final formal knowledge belongs under the content
domain where the user will later look for it.

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

Identify the durable content domain before deciding file paths. The wiki owner's wiki is
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

For brand and visual-production overlap, do not merge the two domains merely
because both mention brand visuals. Brand strategy owns the "why": positioning,
mindshare, differentiation, memory assets, visual symbols, and visual-world
logic as brand assets. Visual production owns the "how": ecommerce images,
detail pages, shooting, layout, AI image/video workflows, style libraries,
prompt control, and repeatable production. When a source contains both, choose
one primary home by the question it answers and add a related-memory bridge to
the other domain.

For ecommerce knowledge, classify platform ownership before choosing the final
path. Platform-specific rules, tools, entry requirements, backend workflows, and
operations belong under the relevant platform area, such as Taobao/Tmall, JD,
Pinduoduo, Douyin, Xiaohongshu, or cross-border ecommerce. Platform-independent
merchant methods, consulting logic, channel strategy, settlement/accounting
interfaces, supply chain methods, and reusable ecommerce playbooks belong under
general ecommerce methods. ERP/API/tool knowledge belongs under the ecommerce
systems/tooling area unless the tool is clearly a platform-native feature.
The source type, such as course, book, webpage, or transcript, must not become
the final classification.

### 0.2 Mandatory Placement Proposal And User Confirmation

Every ingest has one deliberate confirmation gate before formal knowledge is
created or merged. This gate applies even when the Agent believes the placement
is obvious.

First preserve the raw source and complete enough extraction to understand what
the material actually teaches. Then inspect the Wiki's current domain tree,
indexes, query entries, and representative pages. Do not ask the user to design
the taxonomy from scratch. Present a concrete recommendation containing:

- a short description of the knowledge contained in the source
- the best existing category, if one is suitably specific
- the recommended final location and whether pages should be merged, extended,
  split, or created
- any minimal new category or subcategory that is needed
- why this placement will make future retrieval and Agent use clearer
- a split and cross-link proposal when one source contains distinct domains
- at most one or two meaningful alternatives when there is a real tradeoff

Then stop and wait for the user's explicit confirmation or correction. A batch
of closely related sources may share one confirmed placement plan, but silence
or prior confirmation of a different source is not approval.

Before confirmation, the Agent may archive raw material, inspect media, run
ASR/OCR, build source inventories, and write extraction notes. It must not create
or modify formal domain pages, query entries, or formal indexes.

If the Wiki is empty or its taxonomy is immature, say so and propose the
smallest useful initial hierarchy based on the knowledge's meaning and likely
future retrieval. Do not place material directly into a broad top-level folder
merely because that folder is generally related, and do not pre-create a large
tree of empty directories. If the Wiki already contains categories, use one
only when it is semantically and operationally specific enough for the current
knowledge; otherwise propose a minimal new subcategory and ask for confirmation.

Record the confirmed choice, confirmation evidence, final path, and disposition
in `formal-page-plan.md` and `audit-handoff.md`.

### 0.3 Search Existing Memory Before Creating Pages

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

The search results inform the mandatory placement proposal above. They do not
replace the user confirmation gate.

### 0.4 Human-Facing Chinese Names

Use Chinese titles and Chinese index labels by default for formal knowledge
pages, because the user navigates and reviews the wiki in Chinese. English slugs
can remain in frontmatter (`slug`, `aliases`) or transitional filenames, but
new or renamed human-facing knowledge should be Chinese-readable. Avoid
creating a large English-only directory tree for Chinese knowledge.

Top-level human-facing domain directories under `domains/` should also be
Chinese-readable by default, not only their child folders. Use English slugs as
aliases, tags, or metadata when useful, but do not leave the navigable domain
directory English-only.

When a folder or page belongs to an ordered learning/navigation sequence, add a
numeric prefix to the filename, such as `01-基础概念/`,
`02-业务模型/`, or `03-风险与例外.md`. The number is part of the
navigation contract, not decoration: choose it so the user can tell which file to
read first in Obsidian or any plain file browser.

### 0.5 Associative Fusion

Do not destroy an older knowledge structure merely because a new source overlaps
with it. If the old page still has its own context or curriculum value, preserve
it and connect the new durable page through:

- a "相关记忆" or "Related memory" section on the new page
- backlinks from old indexes where useful
- source/course package indexes that point to the durable domain pages
- short notes explaining how the old knowledge confirms, extends, or constrains
  the new synthesis

Use destructive merging only when two pages are genuinely duplicate theories and
the user has confirmed the merge.

### 0.5.1 Case Library Layer

Dense business, ecommerce, brand, finance, or visual courses often contain many
named cases. Do not leave important cases buried only inside theory chapters.
When a domain contains multiple reusable cases, create or update a domain case
library/index layer, such as `domains/品牌策略/90-样本/`.

A case library page should not replace the theory page. It should be a retrieval
layer that helps the user and agents answer "what case is this problem like?" Each
case entry should point back to the relevant theory page and preserve source
traceability.

For each durable case page, prefer this structure:

- case conclusion
- background problem
- strategic/action moves
- why it worked
- transferable method
- misuse boundary
- related theory pages

Case libraries should be organized by problem type as well as by module, so an
agent can route from a user question to the right example before reasoning.

### 0.6 Source Packages Are Secondary

Use `raw/` and `_meta/extraction-notes/` for source preservation and audit.
If a course/book needs a navigable source-oriented overview, place it in a
source/course package area such as `source-packages/`, `course-packages/`, or a
Chinese equivalent like `课程包/`. The package should point to the formal domain
pages; it should not become the only home of the knowledge.

## Cross-Platform Environment Resolution

Do not conclude that the Wiki or a required media tool is missing merely because
its command is absent from the current `PATH`.

At the start of the run:

1. Detect the current operating system and shell.
2. Resolve `WIKI_ROOT` from the current environment. If it is unset, read
   `~/.llmwiki/config.json` as data before using the default `~/wiki`. This JSON
   file is the cross-platform source of truth and does not depend on shell
   execution policy. Older installations may have only `config.env`,
   `config.ps1`, or `config.cmd`; read those files as plain text and parse their
   variable assignments instead of executing them.
3. Test whether `$WIKI_ROOT/TOOLS.md` exists before reading it. Its absence on an
   older Wiki is normal and must not produce a failed read call. When it exists,
   treat its verified executable and model paths as the primary tool inventory
   for this Wiki.
4. Resolve `LLMWIKI_MEDIA_BIN` and `WHISPER_MODEL` from the current environment
   or the platform config. Check the recorded absolute paths before probing
   `PATH`, package managers, or common install directories.
5. Use verified absolute executable paths for the current run. Do not change a
   shell profile, execution policy, persistent `PATH`, or install a duplicate
   tool merely to make a short command resolve.
6. If a recorded path is stale, report the exact path and failure, then follow
   the applicable adapter's missing-tool branch. Ask before installing or
   replacing software, and return to the ingest main line after repair.

On Windows PowerShell, read the JSON config without executing a script:

```powershell
$configPath = Join-Path $env:USERPROFILE '.llmwiki\config.json'
$config = Get-Content -Raw -LiteralPath $configPath | ConvertFrom-Json
$wikiRoot = [string]$config.WIKI_ROOT
$mediaBin = [string]$config.LLMWIKI_MEDIA_BIN
$model = [string]$config.WHISPER_MODEL
```

Do not change PowerShell execution policy to load Wiki configuration. Do not use
Bash heredocs, `export`, or CMD-only command chaining in PowerShell. Assign an
`if` result to a variable before building a hashtable; Windows PowerShell 5 does
not accept `(if (...) {...})` as a value expression.
For video/audio ingestion, read
`references/transcript/video-course-ingest.md` before declaring `ffmpeg`,
`ffprobe`, OCR, or ASR unavailable.

### Python Launcher Gate

Before the first bundled Python script, read
`references/python-launcher-resolution.md`. Resolve a working Python launcher on
the target computer by running its mandatory probe. Command discovery alone is
not proof: Windows Store aliases must be rejected when the probe fails.

Record the verified executable plus any prefix arguments, such as the `-3` in
`py -3`, and reuse that same launcher for every Python script in the ingest.
Never hard-code an author-machine path and never switch to `python3` merely
because an example command uses that spelling.

## Required Orientation

Before editing the wiki:

1. Read `$WIKI_ROOT/AGENTS.md`.
2. Read `$WIKI_ROOT/SCHEMA.md`.
3. Read `$WIKI_ROOT/index.md`.
4. Read recent `$WIKI_ROOT/log.md`.
5. Search existing wiki pages for source title, product names, concepts, APIs, brands, model IDs, and major keywords.
6. Run the bundled `scripts/wiki_cli_search.py` with the verified Python launcher to probe the source title and core concepts. Pass the resolved Wiki root with `--wiki`. The script falls back to a Python filesystem search when Obsidian CLI or `rg` is unavailable. If it still cannot run, record the exact error and perform the equivalent filesystem search before returning to the main flow.
7. If `$WIKI_ROOT/.git` exists, run `git -C $WIKI_ROOT status --short` and avoid
   reverting unrelated work. If the Wiki is not a Git repository, skip Git;
   Git is not required for ingestion and must not be installed or initialized
   just for this step.

If the task will create or modify more than 10 wiki files, present a short execution plan before editing unless the user already approved a batch run.

## Source Adapter Selection

Read `references/source-adapter-map.md`, then load only the relevant adapter:

| Source | Adapter |
| --- | --- |
| Obsidian Web Clipper / webpage / Clippings | `adapters/web-clipping.md` |
| API docs / developer docs / endpoint docs | `adapters/api-docs.md` |
| EPUB/PDF/book manuscript | `adapters/book.md` |
| course/audio/video/meeting transcript or local audio/video course | `adapters/transcript.md` |
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
- placement confirmation status, confirmed path, and confirmation evidence
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

Do not begin this step until the mandatory placement proposal has been explicitly
confirmed. Use the confirmed location and disposition as the boundary for the
formal page plan. If extraction reveals that the confirmed plan is materially
wrong, return to the user with a revised recommendation instead of silently
changing the taxonomy.

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

### 5.1 Query Entry Gate

Every ingest must decide whether the new or updated knowledge needs a `queries/`
entry page. This is the Agent routing layer: future users should not need to
remember how many formal markdown files were created for a topic.

Create or update a query entry page when any of these are true:

- The knowledge supports a recurring task, diagnosis, planning workflow,
  generation workflow, comparison, troubleshooting flow, or skill creation.
- The formal knowledge spans more than one page or directory.
- A future Agent would need a specific reading order, boundary conditions, or
  output structure to use the knowledge correctly.
- The topic is likely to be invoked by natural language rather than by an exact
  page title.

The query entry page should be small and operational. It should contain:

- trigger phrases / when to use it
- ordered reading list of core pages
- optional pages to read only in specific branches
- answer or execution boundaries
- standard diagnostic / planning / output steps

It is a formal page and must use all frontmatter fields required by
`references/formal-page-standards.md`, including both `created:` and `updated:`.

If no query page is needed, record `query-entry: not-needed` plus the reason in
the formal page plan or audit handoff. Do not silently omit the decision.

### 6. Formal Compilation

Formal pages must:

- include YAML frontmatter matching `$WIKI_ROOT/SCHEMA.md`
- cite raw source and extraction notes in `sources`
- use `[[wikilinks]]`
- preserve all meaningful source knowledge or link to coverage records
- integrate examples/cases into reasoning, not append disconnected fact lists
- include decision rules, templates, checklists, or code snippets when useful
- mark time-sensitive claims and outdated-risk
- be readable by future agents without reopening raw for normal use

Read `references/formal-page-standards.md` before writing formal pages.
The coverage matrix is also a machine-validated contract. Copy the exact
English column names from `references/coverage-contract.md`; do not translate,
rename, or omit them. Adapter-specific columns may be added after the required
columns.

### 7. Index, Log, and Cleanup

Update:

- domain/project/shared index where relevant
- `queries/` entry page when the Query Entry Gate says one is needed
- `$WIKI_ROOT/index.md`
- `$WIKI_ROOT/log.md`

Only delete a queue item such as a Clippings file after:

- raw source exists
- formal knowledge exists or source is explicitly raw-only
- coverage/omission record exists
- index/log are updated
- query entry is created/updated, or the no-query reason is recorded

### 8. Audit Handoff

Every ingest must create or update:

```text
_meta/extraction-notes/<source-slug>/audit-handoff.md
```

Use `references/audit-handoff-contract.md`. This file is the interface with `llm-wiki-audit-and-optimization`.
Include the proposed placement, the user's confirmed choice, the confirmation
evidence, and any taxonomy alternative that was rejected.

### 9. Self-Validation

Before final response:

1. Run the platform validation entry point below. It discovers and runtime-tests
   Python on the target computer, rejects broken command aliases, and invokes
   the bundled validator with fixed parameter names. Repeat raw/formal inputs as
   needed. A formal input may be a Markdown file or a directory.

```text
Windows PowerShell:
& <skill-dir>/scripts/run_ingest_validation.cmd --wiki-root <wiki-root> --notes-dir <notes-dir> --raw <raw-path> --formal <formal-path>

macOS/Linux:
<skill-dir>/scripts/run_ingest_validation.sh --wiki-root <wiki-root> --notes-dir <notes-dir> --raw <raw-path> --formal <formal-path>
```

The bundled validator is self-contained. It checks required extraction notes,
the exact coverage contract, target-page existence, formal frontmatter,
placeholder/boilerplate markers, thin non-index pages, and duplicate formal
bodies. It also checks the audit-handoff contract, knowledge-inventory versus
coverage dispositions, durable source-inventory paths, and required raw plus
extraction-note citations in formal pages. Do not call another Skill's
placeholder scanner as a required ingest dependency.

Choose `.cmd` or `.sh` by the shell that is actually executing the validation,
not by the operating system where the Wiki files originated. Include every
newly created or modified formal page in validation. If a query entry or parent
index sits outside the main formal directory, pass it as an additional formal
input instead of assuming the directory scan includes it.

2. Treat any non-zero validation exit as a repair instruction, not as an optional
   warning. Fix the reported artifacts, rerun the same command with the same
   inputs, and repeat until it exits `0`. Never replace a failed
   validator with a manual file listing or claim complete/100% coverage while
   validation is failing. If the environment cannot run the validator after the
   launcher discovery procedure, record an incomplete result and stop before a
   success claim.

3. Run the route audit helper bundled with this Skill using the same verified
   Python launcher:

```bash
<python> <skill-dir>/scripts/wiki_cli_route_audit.py <new-entry-page.md> --wiki "<wiki-root>"
```

Do not search for a development checkout or depend on `LLMWIKI_SKILL_SOURCE`.
If the bundled script cannot run, record the exact error in `audit-handoff.md`,
perform its filesystem checks manually, and clearly mark Obsidian global signals
as unavailable.

If the active Obsidian vault is not `$WIKI_ROOT`, treat the script's degraded filesystem checks as partial route validation and say so.

4. Search representative source terms across formal pages with `rg`,
   `Select-String`, or an equivalent filesystem search available on the current
   platform. Do not require `rg` merely for this check.
5. Verify every `formalized` source unit has a target page. For each row, verify
   the target page contains the actual claim, rule, example, parameter, or
   operation represented by that source unit; file existence alone is not
   enough. Use distinctive source terms as anchors and correct inaccurate target
   mappings before completion.
6. Verify every raw-only or omitted source unit has a reason.
7. Verify `formal-page-plan.md` and `audit-handoff.md` record an explicit
   placement confirmation and that no formal domain page, query entry, or formal
   index was written before that confirmation.

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
- confirmed placement, confirmation evidence, and final fusion disposition
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
- query entries created/updated, or no-query reason
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
