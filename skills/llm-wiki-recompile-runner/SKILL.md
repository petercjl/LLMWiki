---
name: llm-wiki-recompile-runner
description: Repair an existing Markdown LLM Wiki after an audit finds broken routes, stale indexes or status, skeleton/thin/shell pages, incomplete coverage, or source-shaped knowledge that needs reorganization. Use when the user asks to fix the audit findings, repair the Wiki, rebuild weak pages, or recompile existing source material. Select the smallest safe repair mode, preserve raw sources, and verify the repaired routes and content before reporting completion.
---

# LLM Wiki Recompile Runner

## Purpose

Turn confirmed Wiki defects into a bounded repair, then prove that the repair
worked. This skill owns repair planning, editing, verification, and the final
repair report. It does not run a new general audit and does not ingest unrelated
new material.

Use the smallest mode that solves the finding:

1. **Routing/status repair** — fix broken links, missing entry routes, stale
   indexes, and incorrect completion labels.
2. **Formal synthesis repair** — rebuild thin or shell formal pages from
   complete extraction notes and preserved raw evidence.
3. **Full source recompile** — rerun the current ingestion workflow when the
   extraction package itself is incomplete or invalid.
4. **Memory reorganization** — move, split, merge, or fuse existing knowledge
   so it is retrievable by durable topic rather than only by source or course.

Do not use this skill to create reports, answer an ordinary Wiki question, or
add a new source that has not been ingested before.

## Input And Output

Accept any of the following:

- an audit result in the current conversation;
- an audit report file;
- a user-named broken page, route, domain, or source package;
- a direct request such as “按刚才的检查结果修复”。

If the target Wiki or defect list is ambiguous, ask one short clarifying
question. Do not invent defects.

Successful output has two parts:

- the repaired Wiki files;
- a concise report listing the repair mode, changed files, verification results,
  remaining issues, and anything that still needs user judgment.

## Portability And Dependencies

Core routing and status repairs require only filesystem read/write/search.
They do not require Git, network access, Obsidian, or package installation.

This skill bundles its own optional verification scripts under `scripts/`:

- `placeholder_scan.py` checks formal pages for `SHELL`, `SKELETON`, and `THIN`;
- `wiki_cli_route_audit.py` checks links, backlinks, orphans, dead ends, and
  selected page routes. It uses filesystem checks when Obsidian CLI is missing
  or points at another vault.

Never call a script by reaching into another Skill's directory. To run a bundled
script, first discover a working Python interpreter on the current machine:

1. try the platform's normal launchers (`python`, `py`, then `python3` where
   available);
2. if those fail, inspect PATH and common installed-runtime locations;
3. verify the candidate with a version command;
4. if no interpreter works, perform the equivalent file checks manually and
   report the degraded verification. Do not install software unless the user
   confirms it.

Obsidian CLI is optional. Never treat its absence as a reason to skip filesystem
verification or to switch to another Wiki.

Full source recompile may use the currently installed `llm-wiki-ingest` Skill.
Resolve it by Skill identity at runtime and read its current instructions; never
assume an author path or copy an old ingestion contract into this skill. If that
Skill is unavailable, stop before recompilation and explain what is missing.

## Resolve The Wiki Root

Before any edit, resolve exactly one Wiki root:

1. an explicit path in the user's request;
2. the current system/workspace instructions;
3. `WIKI_ROOT` if set;
4. an already registered Obsidian vault whose root contains `index.md` plus
   `domains/`, `queries/`, or `_meta/`;
5. a conventional `wiki` directory under the current user's home.

Confirm the chosen root by checking its marker files. Do not create a new Wiki,
merge multiple roots, or silently repair a similarly named directory.

## Main Workflow

### 1. Orient And Preserve Scope

Read, when present:

- root `AGENTS.md`, `SCHEMA.md`, and `index.md`;
- the recent part of `log.md`;
- the audit finding or report;
- affected indexes, pages, query entries, raw references, and extraction notes.

Translate the findings into a repair list. Every edit must map to one listed
finding. Record the pre-edit content or hashes of affected files. Never modify
raw source files.

### 2. Choose One Repair Mode

| Finding | Mode | Evidence Needed |
| --- | --- | --- |
| broken link, missing route, stale index/status | Routing/status repair | affected pages and intended existing target |
| thin/shell formal page, complete notes | Formal synthesis repair | extraction notes plus source evidence |
| incomplete notes, missing coverage, failed semantic validation | Full source recompile | preserved raw source plus current ingestion workflow |
| duplicated, source-shaped, misplaced knowledge | Memory reorganization | existing pages, routes, provenance, proposed destination |

Do not turn a small navigation defect into a full content rewrite. Do not add a
few generic paragraphs to disguise a `SHELL` page.

### 3. Apply The Confirmation Gate

Proceed directly when the user already requested a specific, low-risk repair
and it changes only a small set of links, indexes, or status text.

First show a file-level plan and wait for confirmation if the repair:

- deletes or moves files;
- changes top-level or major categories;
- merges distinct theories or sources;
- rewrites knowledge claims;
- affects more than 10 files;
- starts a full source recompile whose scope was not already explicit.

### 4A. Routing And Status Repair

For each confirmed finding:

1. locate the existing target page; never create a fake target merely to make a
   broken link disappear;
2. use a stable Wiki-relative link that resolves from the source page;
3. add the missing entry to the narrowest useful index or query page;
4. change status only when the underlying content supports the new status;
5. avoid changing knowledge prose;
6. append a short `log.md` entry if the Wiki's own rules require repair logging.

Re-read every changed file. Then run the bundled route audit on the affected
pages, or perform equivalent link resolution and route checks manually.

### 4B. Formal Synthesis Repair

Use only when extraction notes and source evidence are complete enough to trace
the rebuilt claims.

1. map every weak formal page to its knowledge units and source evidence;
2. rebuild reasoning, decisions, boundaries, examples, and evidence anchors;
3. preserve provenance and existing valid links;
4. record omissions instead of silently dropping uncertain material;
5. keep source/classroom wording out of durable formal pages unless it is itself
   necessary knowledge.

If the notes cannot support the repair, switch to full source recompile rather
than improvising content.

### 4C. Full Source Recompile

1. identify the original source and its existing extraction package;
2. confirm that raw material is present and unchanged;
3. load the current installed ingestion Skill and follow its current adapter,
   semantic-validation, coverage, and audit-handoff contracts;
4. recompile one source package at a time;
5. keep the old package until the replacement passes all gates;
6. update routes and status only after the replacement is verified.

Do not depend on historical extraction filenames. The installed ingestion
Skill's current contract is authoritative.

### 4D. Memory Reorganization

Before editing, prepare a migration table:

| Existing page | Current role | Proposed durable home | Merge, move, split, or link | Provenance kept at | Confirmation needed |
| --- | --- | --- | --- | --- | --- |

Prefer linking when two pages provide distinct context. Merge only true
duplicates. Keep raw material and extraction notes in place. When retiring a
source-shaped route, leave a useful provenance pointer instead of an unexplained
dead end.

## Verification Gates

A repair is not complete because files were written. Verify all applicable
gates:

1. **Targeted finding:** every promised defect is resolved or explicitly left
   open with a reason.
2. **Links and routes:** repaired links resolve; intended entry pages reach the
   target; no new unresolved link, orphan, or dead end was introduced.
3. **Content depth:** repaired formal pages are not `SHELL` or `THIN`; skeleton
   indexes are reported separately from failed content compilation.
4. **Evidence:** rebuilt claims remain traceable to notes or raw evidence; noisy
   ASR/OCR sources retain passed semantic validation.
5. **Preservation:** raw source hashes or contents are unchanged.
6. **Scope:** only planned files changed; unrelated categories and content were
   not rewritten.
7. **Retrieval:** test at least one ordinary question or navigation route that
   previously failed.

If any applicable gate fails, repair the cause and rerun the check. Do not call
the task complete while a targeted check still fails.

## Final Report

Report in plain language:

- what was repaired and which mode was used;
- exactly which files changed;
- the before/after verification result;
- whether raw sources stayed unchanged;
- unresolved P0/P1/P2 issues outside the agreed scope;
- whether the repaired area is ready for normal Wiki queries.

Do not bury failures in a long execution diary. Distinguish completed repairs
from recommendations that still need approval.

## Non-Negotiable Rules

- Never modify or delete raw sources.
- Never fabricate evidence, links, targets, or completion status.
- Never change major taxonomy silently.
- Never use author-specific absolute paths, tool locations, or historical
  personal cases as defaults.
- Never let an optional CLI choose the target Wiki implicitly.
- Never treat one successful file write as successful repair.
- When verification fails, fix and rerun or report the exact blocker.
