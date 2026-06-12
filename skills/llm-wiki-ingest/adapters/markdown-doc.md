# Markdown Document Adapter

Use for local Markdown manuals, README-like docs, exported notes, specifications, plans, and already-structured `.md` sources outside the formal wiki.

## Intake

Record:

- source path
- title
- author/source if known
- created/updated date if known
- whether it is raw source, draft formal page, or external documentation
- target wiki domain

## Inventory

Preserve:

- frontmatter values
- headings
- paragraphs
- lists
- tables
- code blocks
- links
- images or embedded assets
- admonitions and TODOs

Existing Markdown structure is not proof of formal quality. Still compile it into wiki schema, link structure, and Agent-usable pages.

## Formal Output

Choose:

- cleaned formal page
- source-summary page
- concept/playbook split
- project or entity page

If the source is already close to formal, avoid unnecessary rewrites; add missing frontmatter, sources, links, coverage records, and index/log entries.

## Validation

Check all original headings against coverage. Check code blocks and tables were preserved or explicitly dispositioned.
