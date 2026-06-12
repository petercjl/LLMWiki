# Wiki Placement Rules

Use this reference when deciding where a book's formal pages should live.

## Orientation

Read these files before editing:

- `~/wiki/AGENTS.md`
- `~/wiki/SCHEMA.md`
- `~/wiki/index.md`
- recent `~/wiki/log.md`

Search existing pages before creating new ones.

## Placement

Use Peter's one-vault, multi-domain structure:

- `domains/ecommerce-ops/`: ecommerce operations, Taobao/Tmall, store operations, traffic, service, supply chain, finance, team management.
- `domains/visual-production/`: images, detail pages, visual production, AI image/video workflows.
- `domains/brand-strategy/`: positioning, mindshare, brand expression, hero-product strategy.
- `domains/ai-agent-engineering/`: AI agents, LLM Wiki, skills, tools, automation.
- `shared/`: cross-domain frameworks such as consumer psychology, business frameworks, knowledge management.
- `projects/`: project-specific context.
- `entities/`: people, companies, brands, products, tools.
- `raw/`: immutable source material.
- `inbox/`: temporary inputs.

If a book spans several domains, create one primary learning path in the dominant domain and cross-link to shared pages. Do not split a book into multiple domains unless the formal knowledge would otherwise become confusing.

## Frontmatter

Use the wiki schema:

```yaml
---
title: 页面标题
type: concept | entity | project | playbook | comparison | query | decision | source-summary
created: YYYY-MM-DD
updated: YYYY-MM-DD
domain: ecommerce-ops | visual-production | brand-strategy | ai-agent-engineering | shared | project | entity | meta
tags: [tag1, tag2]
sources:
  - raw/books/example/source.epub
status: active
---
```

For a book learning path index, use `type: source-summary`.

For chapter synthesis pages, usually use `type: concept` or `type: playbook`.

## Indexing

After creating formal pages, update:

- the domain index, e.g. `domains/ecommerce-ops/index.md`
- the root `index.md`
- `log.md`

Add one concise line per formal page to the root index only when the page is a top-level entry or part of a learning path section. Avoid dumping large unsorted lists.

## Source Paths

Use relative source paths from wiki root:

```yaml
sources:
  - raw/books/book-slug-year/source.epub
  - _meta/extraction-notes/book-slug-year/coverage-matrix.md
```

Formal pages should cite chapter IDs or source files in a short "来源与边界" section.
