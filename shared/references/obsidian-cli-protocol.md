# Obsidian CLI Protocol for LLM Wiki

Use Obsidian CLI as a route and health layer for `$WIKI_ROOT`. It complements direct filesystem edits; it does not replace deterministic scripts or source coverage records.

## Safety

- Default wiki path: `$WIKI_ROOT` or `~/wiki` when unset.
- Before trusting CLI results, compare `obsidian vault info=path` with the target wiki path.
- If the active vault is not the target wiki, report degraded mode and fall back to filesystem search or parsing.
- Do not use CLI write operations for batch ingestion unless the user explicitly asks for Obsidian-driven edits.

## Before Ingest

Run search probes before creating new formal pages:

```bash
obsidian search query="<source title>" limit=30 format=json
obsidian search:context query="<core concept>" limit=20 format=json
obsidian files folder="raw/transcripts"
obsidian files folder="domains/<domain>/learning-paths"
```

Use the results to decide whether to update an existing page, extend an existing learning path, or create a new artifact.

## After Ingest

Run route checks on newly created or updated entry pages:

```bash
obsidian unresolved counts
obsidian orphans total
obsidian deadends total
obsidian backlinks path="<new-page>.md" counts
obsidian links path="<new-page>.md"
obsidian outline path="<new-page>.md" format=json
```

Interpret global `orphans` and `deadends` carefully. A large global number is not automatically a failure for the current ingest; the current target pages matter most.

## Query Use

For user questions, do not jump straight to a directory. Build a query pack:

1. Search `queries/`.
2. Search for `Agent 使用模板`.
3. Search domain and learning-path indexes.
4. Expand promising pages with `links`, `backlinks`, and `outline`.
5. Read the selected entry/template pages before reading many chapter pages.

See `query-pack-protocol.md`.
