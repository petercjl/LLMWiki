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

Use the user's one-vault, multi-domain structure:

- `domains/电商运营/`: ecommerce operations. Classify platform-first: general methods under `01-通用电商方法/`, Taobao/Tmall under `02-淘宝天猫/`, JD under `03-京东/`, Pinduoduo/Douyin/Xiaohongshu under their platform areas, cross-border under `20-跨境电商/`, and ERP/API/tooling under `30-ERP与系统工具/`.
- `domains/视觉制作/`: images, detail pages, visual production, AI image/video workflows.
- `domains/品牌策略/`: positioning, mindshare, brand expression, hero-product strategy.
- `domains/AI Agent工程/`: AI agents, LLM Wiki, skills, tools, automation.
- `shared/`: cross-domain frameworks such as consumer psychology, business frameworks, knowledge management.
- `projects/`: project-specific context.
- `entities/`: people, companies, brands, products, tools.
- `raw/`: immutable source material.
- `inbox/`: temporary inputs.

If a book spans several domains, create one primary source/course package only
when it is useful for provenance, then place formal knowledge in the durable
content domain. For ecommerce books, do not leave everything under
`learning-paths/`; split platform-specific chapters and platform-independent
methods into the relevant ecommerce areas when that improves retrieval.

## Frontmatter

Use the wiki schema:

```yaml
---
title: 页面标题
type: concept | entity | project | playbook | comparison | query | decision | source-summary
created: YYYY-MM-DD
updated: YYYY-MM-DD
domain: 电商运营 | 财税与经营财务 | 视觉制作 | 品牌策略 | AI Agent工程 | shared | project | entity | meta
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

- the domain index, e.g. `domains/电商运营/index.md`
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
