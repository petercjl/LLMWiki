# Cross-Agent Install Notes

Codex is the source of truth for this LLM Wiki skill package.

Source repository:

```text
git@github.com:petercjl/LLMWiki.git
```

Codex source path:

```text
/Users/pechen/.codex/skills/.llmwiki-source
```

Published skill directories live under `skills/`. Other agents should install from GitHub and copy the desired skill directories into their own skill locations.

Do not maintain divergent SealSeek or Hermes source copies. If a skill needs changes, update the Codex source repo, push to GitHub, then let other agents pull and reinstall.

Active published skills:

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

Their capabilities are now handled by `llm-wiki-ingest` adapters.
