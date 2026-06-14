# Formal Page Standards

Formal pages are compiled knowledge, not source summaries.

## Required Frontmatter

Follow `/Users/pechen/wiki/SCHEMA.md`:

```yaml
---
title: 页面标题
type: concept | entity | project | playbook | comparison | query | decision | source-summary
created: YYYY-MM-DD
updated: YYYY-MM-DD
domain: 电商运营 | 财税与经营财务 | 视觉制作 | 品牌策略 | AI Agent工程 | shared | project | entity | meta
tags: [tag]
sources:
  - raw/...
  - _meta/extraction-notes/.../coverage-matrix.md
status: active
---
```

## Content Requirements

Use the artifact shape that fits the source. A strong formal page usually includes:

- orientation: what problem this page helps solve
- definitions and core claims
- structured facts, not only prose
- examples/cases integrated into reasoning
- rules, formulas, thresholds, parameters
- workflows, checklists, code/templates when applicable
- applicability conditions
- limitations and caveats
- time-sensitive/source-date notes
- related pages via `[[wikilinks]]`
- source and coverage notes
- Agent-use instructions when future tasks are likely

## Enrichment Rules

Allowed and encouraged:

- make implicit logic explicit
- add decision tables
- convert cases into transfer rules
- compare alternatives
- add task prompts/templates
- mark outdated-risk
- link to existing concepts

Not allowed:

- replacing source coverage with generic commentary
- dropping examples because they seem obvious
- leaving code/API fields only in raw
- copying long copyrighted source passages
- creating disconnected fact dumps

## Page Granularity

Avoid both extremes:

- too thin: one source section becomes a tiny page without routing value
- too huge: all source knowledge buried in one mega-page

Use learning paths, capability maps, reference manuals, playbooks, and query pages when the source supports repeated Agent tasks.
