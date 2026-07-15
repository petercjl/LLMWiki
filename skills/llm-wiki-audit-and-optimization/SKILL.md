---
name: llm-wiki-audit-and-optimization
description: Audit an existing Markdown LLM Wiki for compilation depth, navigation and retrieval routes, and answer-readiness. Use when the user asks to check Wiki quality, verify a recent ingest, find why knowledge cannot be found or used correctly, diagnose a question-and-answer result, or propose prioritized Wiki improvements. Audits are read-only by default; repairs belong to the repair/recompile workflow unless the user explicitly requests a bounded optimization.
---

# LLM Wiki Audit And Optimization

Check whether an LLM Wiki works as reusable memory rather than merely containing
organized Markdown files. Audit the full chain:

```text
answer quality = compilation quality × route quality × reasoning quality
```

- **Compilation**: source material became accurate, structured, traceable knowledge.
- **Route**: indexes, query entries, titles, and wikilinks lead to the right pages.
- **Reasoning**: the pages contain enough conditions, evidence, and decision logic
  to support a useful answer.

## Scope And Boundaries

Use this Skill for:

- a whole-Wiki, domain, topic, or learning-path health check;
- post-ingest QA;
- diagnosis of a question and an AI answer against the Wiki;
- a prioritized optimization plan;
- small route fixes only when the user explicitly asks to apply them.

Do not use it to ingest a new source. Do not silently rewrite or reorganize the
Wiki during an audit. Deep repair, recompilation, and broad reorganization belong
to `llm-wiki-recompile-runner` after the audit identifies the defects.

## Input And Output

Input:

- an audit request;
- optionally, an explicit Wiki path, target scope, recent ingest, question, or
  answer to diagnose.

Output:

- a concrete audit report in the current conversation;
- inspected paths and runtime evidence;
- Compile / Route / Reason findings;
- P0 / P1 / P2 fixes and the exact files they affect;
- whether the audit changed any files.

The default audit is read-only. Save the report as a Markdown file only when the
user asks. Do not treat writing an audit report as permission to edit the Wiki.

## Portability And Dependencies

The core audit requires only access to the target Markdown Wiki and the Agent's
file-list, text-search, and file-read capabilities.

The two bundled helpers use only the Python 3 standard library:

- `scripts/placeholder_scan.py` performs a complete mechanical shell/thin-page scan.
- `scripts/wiki_cli_route_audit.py` checks wikilinks, backlinks, outlines, orphan
  signals, dead ends, and unresolved links.

Resolve a working Python 3 launcher on the target computer by running a version
probe. Reuse that launcher for both scripts. On Windows, do not assume `python3`
works merely because it exists; test `python`, `py -3`, and other discoverable
Python commands until one actually runs Python 3. Never hard-code an author's
Python path.

Python is optional: if no working Python 3 exists, perform the same checks with
the Agent's file tools and record that the deterministic helpers were unavailable.
Do not install software during an audit unless the user separately authorizes it.

Obsidian CLI is optional enrichment. The route helper first performs filesystem
checks and uses Obsidian CLI signals only when the command works and its active
vault matches the target Wiki. Git, `rg`, network access, an LLMWiki source
checkout, and a specific Agent product are not required.

Treat the resolved Wiki files as the authoritative evidence. Do not call an
Agent product's generic memory search during this workflow. Prefer the bundled
helpers and direct file reads over improvised inline scripts. If an extra check
truly requires an inline command, use syntax supported by the current shell; in
Windows PowerShell, do not use Unix heredoc syntax.

## Main Flow

### 1. Resolve Exactly One Wiki Root

Use the first valid source in this order:

1. the path explicitly provided by the user;
2. the current workspace's durable instructions;
3. `WIKI_ROOT` from the target environment;
4. `WIKI_ROOT` in the target user's `~/.llmwiki/config.json`;
5. the target user's `wiki` directory under their own home directory, but only
   when it contains the expected Wiki files.

A valid Wiki contains `SCHEMA.md`, `index.md`, and `log.md`. Never use a path
copied from the Skill author's computer. If several candidates are valid or none
is valid, list what was found and ask the user which Wiki to audit.

### 2. Orient Before Judging

Read, when present:

1. the Wiki's `AGENTS.md`;
2. `SCHEMA.md`;
3. `index.md`;
4. the latest 20-30 entries of `log.md`;
5. the target domain/topic index;
6. relevant query entries and recent ingest handoff/coverage notes.

Never judge a Wiki from filenames alone.

### 3. Set The Audit Scope

Choose the smallest mode that answers the request:

- **Health audit**: whole Wiki, domain, topic, or learning path.
- **Post-ingest audit**: the formal pages, raw source, extraction notes, routes,
  and coverage created by one ingest.
- **Answer-chain audit**: a user question, an AI answer, and the Wiki route that
  should have supported it.

For a whole-Wiki audit, mechanically scan every formal Markdown page, then inspect
all root/domain/query entry pages and representative detail pages from each
populated area. For a narrower audit, inspect every flagged page plus at least
2-4 representative formal pages.

### 4. Run The P0 Shell And Thin-Page Gate

Run the bundled scan first:

```text
<python> <skill-dir>/scripts/placeholder_scan.py "<target-path>" --json
```

The scanner excludes raw sources, extraction metadata, audit reports, hidden
application folders, and root operating files. It checks 100% of the remaining
formal pages for:

- empty bodies;
- known placeholder or template phrases;
- duplicate normalized bodies across different pages;
- suspiciously thin non-index pages.

Interpret the results:

- `SHELL`: `compile-placeholder`, P0;
- `SKELETON`: an empty or duplicate index scaffold. It is not evidence that an
  ingest failed. Review whether it is clearly marked as unpopulated and whether
  exposing it in navigation could mislead retrieval; classify the route impact
  as P1 or P2 instead of blocking the compiled areas;
- `THIN`: manual depth review required, normally P1 unless essential knowledge
  is missing;
- `OK`: passed mechanical checks only, not proof of semantic quality.

If a path contains P0 shells, do not give its route or reasoning readiness a
normal score. Report that those later scores are blocked until recompilation.

If Python is unavailable, search all formal pages for the precise placeholder
markers named in the helper, compare suspiciously small files, and compare
normalized bodies. Do not use bare ambiguous markers such as `占位`, `TODO`, or
`TBD`; they can collide with real terms such as `心智占位` and `JTBD`.

### 5. Audit Compilation Quality

Read representative formal pages and, when available, compare them with the raw
source, extraction notes, coverage matrix, and omission audit. Check:

- the page is knowledge, not a transcript cleanup or generic summary;
- concepts preserve why/how, conditions, caveats, and decision order;
- important cases, numbers, contrasts, and evidence anchors are retained;
- cases have transfer rules rather than being decorative examples;
- claims are traceable to sources;
- domain placement and page boundaries make sense;
- the page supports a real action, diagnosis, comparison, or decision.

Use these labels where applicable:

- `compile-placeholder`
- `compile-shallow`
- `compile-scattered`
- `compile-omission`
- `compile-biased`

### 6. Audit Routes

Select entry and target pages that represent the real path a future Agent should
follow: root index, domain/topic index, query entry, and one or more detail pages.
Run the bundled helper with Wiki-relative paths:

```text
<python> <skill-dir>/scripts/wiki_cli_route_audit.py \
  "<entry-or-target-1.md>" "<entry-or-target-2.md>" \
  --wiki "<wiki-root>"
```

Review both the per-page report and global filesystem signals:

- unresolved wikilinks;
- missing backlinks and orphan pages;
- dead-end pages with no useful outgoing route;
- missing or thin outlines;
- missing index/query/template entry points;
- duplicate or conflicting routes;
- titles or descriptions that do not say when a page should be used.

The absence of Obsidian CLI is not a route-audit failure. Record that CLI signals
were unavailable and use the helper's filesystem results. Do not abandon the
audit or search for another checkout of the script.

Use these labels where applicable:

- `route-missing-index`
- `route-broken-link`
- `route-orphan`
- `route-dead-end`
- `route-boundary-conflict`
- `route-template-gap`

### 7. Audit Reasoning Readiness

For a supplied question and answer:

1. classify the task and expected output;
2. identify the Wiki pages that should have been used;
3. compare the expected route with the answer's visible grounding;
4. identify unsupported claims, wrong modules, misused cases, or missing user
   inputs.

For a general health or post-ingest audit, derive 2-3 ordinary user questions
from the relevant indexes/query entries. Follow the Wiki route for each question
and check whether the resulting pages can support:

- a direct conclusion;
- the decision logic or action steps;
- important conditions and uncertainty;
- a useful next action.

This is a route-and-readiness simulation, not permission to add new knowledge.

Use these labels where applicable:

- `reasoning-wrong-module`
- `reasoning-case-misuse`
- `reasoning-unsupported-claim`
- `input-insufficient`

### 8. Prioritize Findings

- **P0**: makes the Wiki unsafe or unusable, such as shell pages, missing source
  for essential claims, or no route to the only relevant knowledge.
- **P1**: materially reduces retrieval or answer quality.
- **P2**: improves clarity, maintenance, or convenience.

Every issue must name an affected path and a concrete repair. Avoid vague advice
such as “结构还可以加强”.

### 9. Produce The Report

Use `templates/compile-route-audit-report.md` for health and post-ingest audits.
Use `templates/question-answer-chain-audit.md` for answer-chain diagnosis.

Always include:

- target Wiki and scope;
- dependencies actually used and degraded branches, if any;
- pages and source notes inspected;
- shell/thin scan summary;
- what already works;
- Compile / Route / Reason findings;
- 2-3 representative question routes for a general audit;
- P0 / P1 / P2 fixes;
- whether files changed.

### 10. Keep Audit And Repair Separate

Stop after the report unless the user explicitly asked to optimize. When an
explicit optimization request is limited to small navigation fixes, show the
files to be changed, patch them, update navigation/logging when needed, and
reread the result.

For shell pages, missing source coverage, multi-page rewrites, major category
changes, or broad reorganization, hand the report to `llm-wiki-recompile-runner`.
Do not disguise a deep repair as a few convenient edits.

## QA Gate

Before reporting completion, verify:

- exactly one valid Wiki root was used;
- orientation files were read;
- the mechanical scan covered all formal pages in scope;
- Python and Obsidian were treated as optional and no software was installed;
- representative content was read, not only counted;
- Compile / Route / Reason were all addressed or explicitly blocked by P0;
- general audits exercised 2-3 realistic question routes;
- every finding names evidence and a path;
- priorities are clear;
- the audit did not modify the Wiki unless the user explicitly requested it.

## Failure Handling

### Wiki Root Missing Or Ambiguous

Report the candidates checked and ask the user to choose. Do not create a Wiki.

### Bundled Helper Fails

Report the actual command and error, then perform the equivalent checks with file
tools. Do not download a replacement helper or look for the author's repository.
After an optional-tool or ad hoc check fails, return to the current main-flow
step and still produce the report; do not detour into generic memory search.

### Raw Source Or Extraction Notes Missing

Continue the route and reasoning checks, but label compilation depth or
traceability as unverified. Do not infer source coverage from polished prose.

### Scope Is Too Large For Meaningful Reading

Complete the 100% mechanical scan, inspect all navigation/query entries, and use
a documented representative sample for semantic review. State the sampling rule
and residual risk instead of pretending every page was deeply read.
