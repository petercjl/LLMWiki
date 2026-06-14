# Placement Rules

Read `/Users/pechen/wiki/SCHEMA.md` first. These are practical defaults.

## Formal Knowledge

| Knowledge role | Path |
| --- | --- |
| ecommerce operations, merchant rules, platform operations | `domains/ecommerce-ops/` |
| ecommerce API docs | `domains/ecommerce-ops/api/<provider>/` |
| brand strategy, category positioning, brand cases | `domains/brand-strategy/` |
| visual production, AI image/video generation, creative workflows | `domains/visual-production/` |
| AI agents, skills, tools, model APIs, automation workflows | `domains/AI Agent工程/` |
| cross-domain methods | `shared/` |
| project-specific context | `projects/` |
| people, companies, tools, models, platforms | `entities/` |
| reusable query entry | `queries/` |

## Raw Sources

| Source role | Path |
| --- | --- |
| webpage/clipping | `raw/webpages/<provider-or-topic>/` |
| API documentation | `raw/api/<provider>/` |
| book | `raw/books/<book-slug>-<year>/` |
| transcript | `raw/transcripts/` |
| data/report | `raw/data/` |
| source assets | `raw/assets/<source-slug>/` |

## Extraction Notes

Always:

```text
_meta/extraction-notes/<source-slug>/
```

## Naming

- Use Chinese-readable human-facing domain and page paths by default.
- Keep English slugs in aliases, tags, or metadata when useful for search or compatibility.
- Use ordered prefixes for learning paths: `01-...md`.
- Avoid raw source titles as formal page names unless the page is a source summary.

## Index Rules

- Every formal page appears in `/Users/pechen/wiki/index.md`.
- Domain pages appear in the domain index.
- Internal extraction notes do not need main index entries unless they are formal source-summary pages intended for retrieval.
