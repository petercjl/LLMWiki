---
name: llm-wiki
description: Query and perform routine navigation maintenance on an existing Markdown LLM Wiki. Use when the user asks a question that should be answered from their Wiki, wants to find existing knowledge, compare compiled pages, trace which Wiki pages support an answer, or make small explicit updates to indexes and query entry pages. Delegate new-source ingestion and all quality audit, optimization, repair, and recompilation work to the corresponding LLM Wiki skills.
---

# LLM Wiki Query And Routine Maintenance

Use an existing Markdown LLM Wiki as compiled memory. Find the best route through
the Wiki, read the relevant formal pages, and answer from that evidence instead of
searching raw files at random or relying on general model memory.

## Scope

This Skill owns:

- answering questions from existing Wiki knowledge;
- locating the best query page, usage template, index, and detail pages;
- comparing or synthesizing already compiled knowledge;
- small, explicitly requested navigation maintenance such as repairing an index
  entry or saving a valuable recurring query route.

Use the other LLM Wiki Skills for work outside this boundary:

- new files, webpages, books, videos, audio, meetings, or other source material:
  use `llm-wiki-ingest`;
- compile, route, retrieval, or answer-quality audit, followed by optimization,
  repair, reorganization, or recompilation: use
  `llm-wiki-audit-and-optimization`;
- first-time Wiki and tool setup: use `llm-wiki-bootstrap`.

Do not silently perform one of those larger workflows inside a normal query.

## Input And Output

Input:

- a user question or routine-maintenance request;
- optionally, an explicit Wiki directory.

Output for a query:

- a direct answer in the current conversation;
- the Wiki pages used as evidence;
- any important uncertainty or missing-knowledge gap;
- an optional next action only when it is useful.

A query is read-only by default. Do not edit the Wiki merely because the answer is
valuable. Write a query page, index update, or log entry only when the user asks to
save or maintain it.

## Main Flow

### 1. Resolve One Wiki Root

Use the first valid source in this order:

1. the path explicitly provided by the user;
2. the current workspace's durable instructions;
3. `WIKI_ROOT` from the target environment;
4. `WIKI_ROOT` in the target user's `~/.llmwiki/config.json`;
5. the target user's `wiki` directory under their own home directory, but only if
   it contains the expected Wiki files.

Do not use a path copied from the Skill author's computer. Resolve home-directory
defaults on the machine where the Skill is running. A valid Wiki should contain
`SCHEMA.md`, `index.md`, and `log.md`. If several candidates are valid or none is
valid, report what was found and ask the user which one to use.

### 2. Orient Before Answering

Read, when present:

1. the Wiki's `AGENTS.md` for its operating rules;
2. `SCHEMA.md` for structure and evidence conventions;
3. `index.md` for the current knowledge map;
4. the latest 20-30 entries of `log.md` for recent changes.

Do this in every new conversation. Do not start from a raw transcript or the first
filename that appears relevant.

### 3. Build A Query Pack

Resolve a working Python 3 runtime on the target machine, then run the bundled,
read-only helper:

```text
<python> <skill-dir>/scripts/wiki_cli_search.py "<user question>" --wiki "<wiki-root>"
```

The helper uses only the Python standard library. It does not require `rg`, Git,
Obsidian CLI, an Obsidian plugin, a database, or network access. It searches formal
Markdown knowledge and returns a recommended read order:

```text
query pages -> required linked pages -> relevant indexes -> other detail pages
```

If Python is unavailable, manually follow the same order with the current Agent's
file-list, text-search, and file-read capabilities. Report the missing runtime, but
do not install software during a query unless the user separately authorizes it.

### 4. Read The Route, Not The Whole Vault

Read the most relevant query entry first when one exists. Follow its required
pages and then use the relevant domain/project index to find supporting details.
Expand only the links needed to answer the question.

Prefer formal knowledge under `queries/`, `domains/`, `shared/`, `projects/`,
`concepts/`, `comparisons/`, `entities/`, and `decisions/`. Consult `raw/` or
extraction notes only when the user asks for source verification or the formal
pages expose an unresolved evidence gap.

### 5. Answer From Wiki Evidence

Give the conclusion first. Then explain the reasoning at the level the user needs.
For operational questions, prefer a short checklist, decision rule, comparison,
or next-step plan over a long page-by-page summary.

Name the Wiki pages used. Use their human-facing titles or relative paths. Clearly
separate:

- what the Wiki directly supports;
- what is a synthesis across several pages;
- what the Wiki does not yet establish.

Do not fill a Wiki gap with an uncited model assumption and present it as Wiki
knowledge. If the answer requires current external facts, say that the Wiki alone
is insufficient and ask whether the user wants a separate current-source check.

### 6. Keep Query And Writeback Separate

After answering, stop unless the user requested a change. When explicit writeback
is requested:

1. show which file or route will change;
2. preserve the Wiki's schema and naming conventions;
3. never modify anything under `raw/`;
4. update affected indexes and append a concise log entry;
5. reread the changed files and report them.

If the proposed change becomes a new-source ingest, broad audit, or multi-page
repair, return to the scope boundary and use the appropriate Skill.

## Failure Handling

### Wiki Root Is Missing Or Ambiguous

List the valid candidates checked and ask the user to choose. Do not create a new
Wiki or guess another person's home path.

### Query Helper Fails

Report the actual command error. Continue with the manual query-pack order if file
listing, search, and read capabilities are available. Do not replace the bundled
helper with an improvised downloaded tool during a normal query.

### No Relevant Knowledge Is Found

Say that the current Wiki does not yet answer the question. Mention the routes and
terms checked. Suggest what source or knowledge type could fill the gap, but do not
pretend a general-model answer came from the Wiki.

### A Recommended Link Is Broken

Use the relevant index and filename search to find a likely target. Treat the broken
route as a maintenance finding; do not silently rewrite it without permission.

## QA Gate

Before reporting completion, verify:

- exactly one Wiki root was used;
- `AGENTS.md` (when present), `SCHEMA.md`, `index.md`, and recent `log.md` were
  used for orientation;
- the query pack or its manual equivalent was completed;
- every material claim is supported by the named Wiki pages or labeled as a
  synthesis/uncertainty;
- the answer is useful for the user's task rather than a dump of search results;
- no Wiki file changed during a read-only query;
- any explicit writeback preserved `raw/`, updated navigation/logging as needed,
  and was reread after writing.

## Portability Contract

The portable core requires only:

- access to the target user's Markdown Wiki;
- file listing, text search, and file reading;
- optionally, Python 3 for the bundled query-pack helper.

The core does not require a specific Agent product, home-directory name, shell,
Obsidian CLI path, Git remote, browser profile, private repository, plugin, or
author-machine checkout. Obsidian can be used as the human reading interface, but
it is not a hidden prerequisite for querying the Wiki.
