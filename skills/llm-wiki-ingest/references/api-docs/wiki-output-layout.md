# Wiki Output Layout

## Paths

Default location for business API docs:

```text
/Users/pechen/wiki/domains/电商运营/30-ERP与系统工具/<provider-slug>/
```

For non-ecommerce APIs, choose the domain by purpose:

- AI/tooling APIs: `domains/AI Agent工程/05-工具链/api/<provider-slug>/`
- Visual production APIs: `domains/visual-production/api/<provider-slug>/`
- Brand/research APIs: `domains/brand-strategy/api/<provider-slug>/`
- Cross-domain APIs: `shared/api/<provider-slug>/`
- Project-specific APIs: `projects/<project>/api/<provider-slug>/`

Raw sources:

```text
/Users/pechen/wiki/raw/api/<provider-slug>/
```

## Recommended Formal Tree

```text
domains/<domain>/30-ERP与系统工具/<provider-slug>/
├── index.md
├── auth-call-contract.md
├── capability-map.md
├── skill-building-guide.md
├── reference/
│   ├── <category>-apis.md
│   └── ...
└── playbooks/
    └── <business-task>.md
```

Query pages:

```text
queries/<provider-slug>-api-skill-creation.md
queries/<provider-slug>-<business-task>.md
```

## Naming

- Use Chinese-readable page and folder names by default for human-facing wiki paths.
- Keep stable provider slugs in aliases or metadata when useful for API search.
- Keep provider slug stable across raw and formal folders.
- Category page filenames can be English business slugs such as `stock-apis.md`, `order-apis.md`, `goods-apis.md`.

## Frontmatter

Use `/Users/pechen/wiki/SCHEMA.md`.

Typical API page:

```yaml
---
title: Provider API 首页
type: concept
created: YYYY-MM-DD
updated: YYYY-MM-DD
domain: 电商运营
tags: [api, provider]
sources:
  - raw/api/provider/provider-full-scrape-YYYY-MM-DD.json
status: active
---
```

Use `type: playbook` for task recipes and `type: query` for query pages.

## Index and Log

Update `/Users/pechen/wiki/index.md` with all formal pages.

Append `/Users/pechen/wiki/log.md` with source, created/updated files, endpoint count, categories, auth status, and remaining gaps.
