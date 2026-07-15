# SealSeek / Hermes Install Notes

Codex is the source maintainer. SealSeek and Hermes should install from:

```text
git@github.com:petercjl/LLMWiki.git
```

Do not copy legacy standalone entries. Install only the published directories under `skills/`:

- `llm-wiki`
- `llm-wiki-bootstrap`
- `llm-wiki-ingest`
- `llm-wiki-audit-and-optimization`

Removed standalone entries:

- `ai-agent-skill-registry-sync`
- `llm-wiki-recompile-runner` (merged into `llm-wiki-audit-and-optimization`)

Merged legacy entries:

- `api-docs-wiki-ingest`
- `wiki-clippings-ingest`
- `book-to-llm-wiki`
- `course-transcript-to-knowledge`

If an existing SealSeek or Hermes environment has the removed entries, delete them before installing this package so metadata does not trigger stale workflows.

## SealSeek System Store Migration

Remove the `llm-wiki-recompile-runner` card from the system Skill catalog and
publish the current `llm-wiki-audit-and-optimization` directory in its place.
The combined Skill owns audit, evidence-backed optimization, repair,
recompilation orchestration, and post-repair verification. Existing user
registrations for the retired Skill should be invalidated or removed during the
catalog migration so new conversations receive only the four active Wiki Skills.
