# LLM Wiki Skill Migration Notes

Date: 2026-06-12

## Published Skill Set

The active LLM Wiki package now publishes five skills:

- `llm-wiki`
- `llm-wiki-bootstrap`
- `llm-wiki-ingest`
- `llm-wiki-audit-and-optimization`
- `llm-wiki-recompile-runner`

`ai-agent-skill-registry-sync` is no longer published from this repository. It is a separate agent-operations utility, not part of the LLM Wiki runtime package.

## Merged Legacy Entries

`api-docs-wiki-ingest` was merged into:

- `skills/llm-wiki-ingest/adapters/api-docs.md`
- `skills/llm-wiki-ingest/references/api-docs/`
- `skills/llm-wiki-ingest/scripts/api/compile_api_reference.py`

`wiki-clippings-ingest` was merged into:

- `skills/llm-wiki-ingest/adapters/web-clipping.md`
- `skills/llm-wiki-ingest/references/web-clipping/`

`book-to-llm-wiki` was merged into:

- `skills/llm-wiki-ingest/adapters/book.md`
- `skills/llm-wiki-ingest/references/book/`
- `skills/llm-wiki-ingest/scripts/book/`

`course-transcript-to-knowledge` was merged into:

- `skills/llm-wiki-ingest/adapters/transcript.md`
- `skills/llm-wiki-ingest/references/transcript/`

## Obsidian CLI Layer

Shared protocols and scripts now live under `shared/`:

- `shared/references/obsidian-cli-protocol.md`
- `shared/references/query-pack-protocol.md`
- `shared/references/route-audit-protocol.md`
- `shared/scripts/wiki_cli_search.py`
- `shared/scripts/wiki_cli_route_audit.py`
- `shared/scripts/wiki_cli_health.py`

The CLI layer is advisory and mechanical. It improves discovery and route validation but does not replace source coverage, formal compilation, or deterministic filesystem scripts.
