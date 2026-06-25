# LLM Wiki Skills

Codex-maintained source package for LLM Wiki skills.

Source of truth:

```text
$LLMWIKI_SKILL_SOURCE
git@github.com:petercjl/LLMWiki.git
```

Published skills are under `skills/`:

- `llm-wiki`
- `llm-wiki-bootstrap`
- `llm-wiki-ingest`
- `llm-wiki-audit-and-optimization`
- `llm-wiki-recompile-runner`

Non-published entries:

- `ai-agent-skill-registry-sync`

Standalone legacy entries have been merged into `llm-wiki-ingest` adapters and are not published:

- `api-docs-wiki-ingest`
- `wiki-clippings-ingest`
- `book-to-llm-wiki`
- `course-transcript-to-knowledge`

Install into Codex from this source repo:

```bash
python3 shared/scripts/sync_to_codex.py --delete-obsolete
```

SealSeek and Hermes should install from GitHub instead of maintaining divergent local source copies.
