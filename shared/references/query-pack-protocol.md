# Query Pack Protocol

A query pack is the routing bundle an agent builds before answering from the LLM Wiki.

## Inputs

- User question.
- Optional target domain or project.
- Wiki path, default `$WIKI_ROOT` or `~/wiki` when unset.

## Required Output

Return or internally use:

- `queries`: matching files under `queries/`.
- `agent_templates`: matching pages with `Agent 使用模板` or `agent-usage-template`.
- `indexes`: matching domain, project, or learning-path index pages.
- `detail_pages`: concept, playbook, API, or chapter candidates.
- `recommended_read_order`: concise ordered list of pages to read.
- `route_notes`: why these pages are likely relevant and what may still be missing.

## Routing Preference

Prefer this order:

1. `queries/` entry pages.
2. Agent-use templates.
3. Domain/project/learning-path indexes.
4. Playbooks and concept pages.
5. Detailed chapters or source summaries.

If a result exists only in raw or extraction notes, use it as evidence but do not treat it as final formal knowledge.

## Failure Signals

- No query or template page exists for a recurring task.
- Search finds many detail pages but no index or template.
- Candidate pages have no backlinks from an index.
- Candidate pages have no outgoing links or no clear usage section.
