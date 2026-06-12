# SealSeek / Hermes Install Notes

Codex is the source maintainer. SealSeek and Hermes should install from:

```text
git@github.com:petercjl/LLMWiki.git
```

Do not copy legacy standalone entries. Install only the published directories under `skills/`:

- `llm-wiki`
- `llm-wiki-ingest`
- `llm-wiki-audit-and-optimization`
- `llm-wiki-recompile-runner`
- `ai-agent-skill-registry-sync`

Removed standalone entries:

- `api-docs-wiki-ingest`
- `wiki-clippings-ingest`
- `book-to-llm-wiki`
- `course-transcript-to-knowledge`

If an existing SealSeek or Hermes environment has the removed entries, delete them before installing this package so metadata does not trigger stale workflows.
