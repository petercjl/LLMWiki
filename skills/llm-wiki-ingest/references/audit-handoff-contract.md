# Audit Handoff Contract

Every ingest should produce:

```text
_meta/extraction-notes/<source-slug>/audit-handoff.md
```

This file lets `llm-wiki-audit-and-optimization` audit completeness and Agent usability without rediscovering the whole job.

## Template

```md
---
title: <source title> audit handoff
type: source-summary
created: YYYY-MM-DD
updated: YYYY-MM-DD
domain: meta
tags: [llm-wiki, audit-handoff]
sources:
  - raw/...
status: active
---

# <Source Title> Audit Handoff

## Source

- Adapter:
- Raw path:
- Original URL/path:
- Capture date:
- Current-doc verification:

## Outputs

- Source profile:
- Source inventory:
- Knowledge-unit inventory:
- Coverage matrix:
- Omission audit:
- Formal page plan:
- Formal pages:

## Coverage Summary

- Source units:
- formalized:
- merged:
- raw-only:
- omitted-with-reason:
- unresolved:

## Expected Agent Use

- Future questions this source should support:
- Pages an Agent should read first:
- Query/playbook entries:

## Known Risks

- Time-sensitive claims:
- Sensitive data removed:
- Weak source areas:
- User confirmation needed:

## Self-Validation

- Placeholder scan:
- Representative term search:
- Index/log check:
- Remaining gaps:
```

## Audit Skill Responsibilities

The audit skill should use the handoff to check:

1. Completeness: coverage matrix matches raw/source inventory and formal pages.
2. Compilation quality: pages are not summaries, shells, or fact dumps.
3. Routing quality: indexes and titles lead agents to the right page.
4. Reasoning readiness: pages contain decision rules, examples, caveats, and templates.

## Failure Labels

Suggested audit labels:

- `coverage-missing-source-unit`
- `coverage-unjustified-raw-only`
- `compile-summary`
- `compile-fact-dump`
- `compile-missing-example`
- `compile-missing-code-or-field`
- `route-missing-index`
- `route-no-agent-entry`
- `agent-usability-low`
