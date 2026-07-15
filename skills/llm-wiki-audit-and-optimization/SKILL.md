---
name: llm-wiki-audit-and-optimization
description: Audit and optimize an existing Markdown LLM Wiki for compilation depth, navigation and retrieval routes, and answer-readiness. Use when the user asks to check Wiki quality, verify a recent ingest, find why knowledge cannot be found or used correctly, diagnose a question-and-answer result, optimize or repair the Wiki, rebuild weak or shell pages, fix routes or taxonomy, or recompile existing source material. By default, continue from audit findings into evidence-backed optimization and re-audit; remain read-only only when the user explicitly says not to modify files.
---

# LLM Wiki Audit And Optimization

Check whether an LLM Wiki works as reusable memory, repair the defects that can
be supported by evidence, and prove that the repaired Wiki works better.

```text
audit -> issue inventory -> optimize -> re-audit -> report
```

Evaluate the full chain:

```text
answer quality = compilation quality × route quality × reasoning quality
```

- **Compilation**: source material became accurate, structured, traceable knowledge.
- **Route**: indexes, query entries, titles, and wikilinks lead to the right pages.
- **Reasoning**: pages contain enough conditions, evidence, and decision logic
  to support a useful answer.

## Permission And Boundaries

An ordinary audit, health-check, optimization, repair, or post-ingest QA request
authorizes the complete audit-and-optimize loop. Do not stop after listing fixes.
Apply every evidence-backed repair, including multi-file synthesis, source
recompilation, and taxonomy repair, then re-audit.

Remain read-only only when the user explicitly says “只检查”, “不要修改”,
“read-only”, or equivalent. In that branch, produce the audit and proposed fixes
without changing any file.

Never:

- modify or delete raw sources;
- invent evidence, claims, link targets, or completion status;
- change another Wiki because an optional tool points at it;
- install software without explaining the need and receiving confirmation;
- treat a successful write as a successful repair without verification.

Do not use this Skill to ingest unrelated new material or answer an ordinary
Wiki question. New sources belong to `llm-wiki-ingest`; normal queries belong to
`llm-wiki`.

## Input And Output

Input may be a whole-Wiki or scoped quality request, a recent ingest, a question
and answer to diagnose, an existing audit result, or a named defect.

Return one concise combined report containing:

- target Wiki, scope, and permission mode;
- runtime evidence and degraded branches;
- Compile / Route / Reason findings;
- P0 / P1 / P2 issue inventory;
- optimizations actually applied and exact changed files;
- before/after verification and representative query routes;
- raw-source preservation result;
- remaining blockers or unsupported recommendations.

Save a report file only when the user asks. Writing a requested report inside
the Wiki is not permission to rewrite unrelated knowledge.

## Portability And Dependencies

The core workflow requires filesystem list/search/read/write capabilities. The
bundled Python-standard-library helpers are:

- `scripts/placeholder_scan.py` for `SHELL`, `SKELETON`, and `THIN` detection;
- `scripts/wiki_cli_route_audit.py` for links, backlinks, orphans, dead ends,
  outlines, and selected routes.

Resolve scripts from the actual `SKILL.md` loaded for this run:

1. use its parent directory as the Skill root;
2. verify the sibling script exists before invoking it;
3. if the advertised path is inside an application archive such as `app.asar`,
   or the script is absent, search active workspace and Agent Skill registries
   for `llm-wiki-audit-and-optimization` containing both this `SKILL.md` and the
   requested script;
4. use the verified installed copy, not a guessed built-in or author path.

Probe the target machine for a working Python 3 launcher. On Windows, test
`python`, `py -3`, and other discoverable candidates instead of assuming
`python3`. If none works, perform equivalent checks with file tools and report
degraded verification. Do not install Python merely to audit.

Obsidian CLI is optional enrichment. Use it only when it works and its active
vault matches the resolved Wiki. Git, network access, `rg`, and a source-repo
checkout are not required.

Full recompilation of an existing source package may use the currently installed
`llm-wiki-ingest` Skill. Resolve it by logical Skill identity, read its current
contract, and use the relevant adapter. Never reach into an author path or copy
an obsolete ingestion contract. If it is absent, report the recompile branch as
blocked instead of improvising.

## Main Flow

### 1. Resolve Exactly One Wiki Root

Use the first valid source:

1. explicit user path;
2. current workspace instructions;
3. `WIKI_ROOT` in the target environment;
4. `WIKI_ROOT` in the target user's `.llmwiki/config.json`;
5. the target user's home `wiki` directory when it contains the expected files.

A valid Wiki contains `SCHEMA.md`, `index.md`, and `log.md`. If several or no
candidates are valid, list them and ask the user. Do not create or merge a Wiki.

### 2. Orient And Record The Before State

Read, when present:

1. Wiki `AGENTS.md`;
2. `SCHEMA.md`;
3. root `index.md`;
4. the latest 20-30 `log.md` entries;
5. target domain/topic indexes and query entries;
6. recent ingest handoff, coverage, omission, and semantic-validation notes.

Record the audit scope, permission mode, affected-file hashes or contents, and a
raw-source hash inventory when optimization may touch compiled knowledge.

### 3. Select The Audit Mode

- **Health audit**: whole Wiki, domain, topic, or learning path.
- **Post-ingest audit**: one source package, formal pages, routes, and coverage.
- **Answer-chain audit**: a user question, an AI answer, and the supporting route.
- **Finding-led optimization**: an existing audit or explicit defect list.

For a whole-Wiki audit, mechanically scan all formal Markdown pages and inspect
all root/domain/query entries plus representative detail pages. For a narrower
scope, inspect every flagged page and at least 2-4 representative formal pages.

### 4. Run The Mechanical Gate

Run:

```text
<python> <skill-root>/scripts/placeholder_scan.py "<target-path>" --json
```

Interpret:

- `SHELL`: P0 failed compilation;
- `SKELETON`: unpopulated index scaffold; inspect status and route impact;
- `THIN`: manual depth review, normally P1;
- `OK`: mechanical pass only, not semantic proof.

If Python is unavailable, use the helper's precise markers and logic through
file tools. Do not use ambiguous bare markers such as `占位`, `TODO`, or `TBD`.

### 5. Audit Compilation

Compare formal pages with source evidence and extraction notes where available.
Check transformation depth, reasoning, conditions, caveats, cases, numbers,
evidence anchors, transfer rules, traceability, domain placement, and actionability.

Use labels when applicable:

- `compile-placeholder`
- `compile-shallow`
- `compile-scattered`
- `compile-omission`
- `compile-biased`

### 6. Audit Routes

Run with Wiki-relative targets:

```text
<python> <skill-root>/scripts/wiki_cli_route_audit.py \
  "<entry-or-target-1.md>" "<entry-or-target-2.md>" \
  --wiki "<wiki-root>"
```

Review unresolved links, backlinks, orphans, dead ends, outlines, missing
index/query entry points, conflicting routes, and unclear titles. Filesystem
results remain authoritative when Obsidian CLI is unavailable or untrusted.

Use labels when applicable:

- `route-missing-index`
- `route-broken-link`
- `route-orphan`
- `route-dead-end`
- `route-boundary-conflict`
- `route-template-gap`

### 7. Audit Reasoning Readiness

For a supplied question and answer, identify the expected pages and compare them
with visible grounding. For a general audit, derive 2-3 ordinary questions from
the relevant indexes and query entries. Check whether the route supports a
conclusion, decision logic, important conditions, uncertainty, and a next action.

Use labels when applicable:

- `reasoning-wrong-module`
- `reasoning-case-misuse`
- `reasoning-unsupported-claim`
- `input-insufficient`

### 8. Build The Issue Inventory

- **P0**: makes the Wiki unsafe or unusable.
- **P1**: materially reduces retrieval or answer quality.
- **P2**: improves clarity, maintenance, or convenience.

Every issue must name evidence, affected paths, and a concrete repair. Separate
true defects from unsupported preferences.

### 9. Optimize Unless Explicitly Read-Only

If the request is read-only, skip edits and continue to Step 11 with proposed
fixes clearly labeled as unapplied.

Otherwise read `references/optimization-workflow.md` completely, select the
smallest repair mode for every finding, and apply all evidence-backed P0/P1/P2
repairs. Do not pause merely because the repair spans many files or changes
taxonomy. Preserve provenance and remain inside the resolved Wiki.

If a repair lacks source evidence, needs unavailable ingestion capability, or
requires a new software installation, leave that individual item blocked and
continue with other safe repairs.

### 10. Re-Audit Until Stable

After edits:

1. reread every changed file;
2. rerun the mechanical scan and route audit;
3. rerun the representative question routes;
4. compare raw hashes and planned versus actual changed files;
5. repair and rerun again while a targeted, evidence-backed check still fails.

Stop only when all supported repairs pass or the exact remaining blocker is
documented. Do not loop on subjective refinements without a failed gate.

### 11. Report

Use `templates/compile-route-audit-report.md` for health/post-ingest/finding-led
work and `templates/question-answer-chain-audit.md` for answer-chain diagnosis.
Make completed repairs visibly different from blocked or unapproved suggestions.

## QA Gate

Before completion, verify:

- one valid Wiki root was used;
- orientation and all formal pages in mechanical scope were checked;
- representative knowledge was read, not only counted;
- Compile / Route / Reason were addressed or explicitly blocked;
- explicit read-only requests caused zero Wiki writes;
- otherwise, all evidence-backed findings entered the optimization loop;
- helper paths were verified from the installed Skill;
- raw sources remained unchanged;
- only the resolved Wiki and planned files changed;
- final claims match the post-repair checks.

## Failure Handling

### Missing Or Ambiguous Wiki

List candidates and ask the user. Do not create one.

### Bundled Helper Fails

Report the exact path, command, and error; then use equivalent file checks. Do
not download a replacement or improvise a persistent script. Return to the same
main-flow step.

### Missing Evidence

Repair routes and status that have direct evidence, but do not synthesize claims
or mark content complete. Report the unsupported item as blocked.

### Scope Too Large For Deep Reading

Complete the 100% mechanical and route-entry checks, document a representative
semantic sample, optimize confirmed findings, and state residual sampling risk.
