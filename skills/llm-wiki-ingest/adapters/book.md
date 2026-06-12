# Book Adapter

Use for EPUB, PDF, scanned books, manuscripts, and long-form reports where the source is chaptered or paginated.

This adapter absorbs the previous `book-to-llm-wiki` workflow. For books, use this adapter inside `llm-wiki-ingest`; do not maintain a separate source-specific ingest path.

## Required References And Scripts

Load these only when doing a book task:

- `references/book/extraction-note-schema.md`
- `references/book/formal-page-patterns.md`
- `references/book/qa-checklist.md`
- `references/book/wiki-placement-rules.md`

For EPUB files, prefer these scripts:

```bash
python3 <skill>/scripts/book/inspect_epub.py /path/to/book.epub --output source-profile.json
python3 <skill>/scripts/book/extract_epub_source.py /path/to/book.epub --output-dir ~/wiki/raw/books/<book-slug>-<year>
python3 <skill>/scripts/book/build_book_inventory.py ~/wiki/raw/books/<book-slug>-<year> --output ~/wiki/_meta/extraction-notes/<book-slug>-<year>/chapter-inventory.md
python3 <skill>/scripts/book/generate_coverage_matrix.py ~/wiki/_meta/extraction-notes/<book-slug>-<year>/chapter-inventory.md --output ~/wiki/_meta/extraction-notes/<book-slug>-<year>/coverage-matrix.md
python3 <skill>/scripts/book/validate_book_ingest.py --wiki-root ~/wiki --raw-dir ~/wiki/raw/books/<book-slug>-<year> --notes-dir ~/wiki/_meta/extraction-notes/<book-slug>-<year> --formal-dir ~/wiki/domains/<domain>/learning-paths/<path>
```

The scripts are mechanical helpers. They do not replace source reading, knowledge-unit extraction, synthesis, or audit handoff.

## Intake

Record:

- title, author, edition, publisher, year
- ISBN, language, OPF/NCX paths when available
- file path and format
- table of contents
- spine order, page/chapter count, HTML/image counts
- OCR quality and missing-page risk
- source file hash when feasible
- copyright handling constraints
- target wiki domains and expected learning paths
- time sensitivity and platform-rule risk

For EPUB, run `scripts/book/inspect_epub.py` first and archive the generated profile.

## Inventory

Create both chapter-level and knowledge-unit inventories. Book ingestion is incomplete if it only has chapter summaries.

For each chapter:

- chapter title and page/section range
- headings and subheadings
- concepts, claims, frameworks, examples, cases
- definitions, taxonomies, rules, formulas, lists
- diagrams/tables and their meanings
- exercises, checklists, workflows
- author caveats and scope conditions
- platform/time-bound advice
- candidate target formal pages

For large books, use hierarchical IDs:

```text
B01-C03-S02-U007
```

Book extraction notes should normally include:

```text
_meta/extraction-notes/<book-slug>-<year>/
├── source-profile.md
├── segment-plan.md
├── knowledge-architecture-plan.md
├── chapter-inventory.md
├── knowledge-unit-inventory.md
├── coverage-matrix.md
├── omission-audit.md
├── source-to-page-map.json
├── formal-page-plan.md
└── audit-handoff.md
```

## Formal Output

Books usually need multiple artifacts:

- source-summary page for bibliographic context
- learning path or chapter map
- concept pages for durable ideas
- playbooks/checklists for methods
- case pages or example libraries when examples are important
- comparison/decision pages for frameworks
- Agent usage template page for applied learning paths

Do not compress a chapter into a one-paragraph summary. Preserve every claim-level unit or deliberately mark it.

Do not mechanically create one formal page per chapter. Group by concept unity, method unity, Agent routing usefulness, source density, and existing wiki pages.

Formal pages should include:

- problem framing
- core model
- operating process or checklist
- decision criteria
- cases/evidence anchors
- applicability and outdated-risk notes
- related wikilinks
- Agent usage guidance

For platform books, separate stable method from time-bound tactic. Old platform rules should be preserved as historical context or abstracted into durable method, not silently written as current rules.

## Raw Handling

Archive under:

```text
raw/books/<book-slug>-<year>/
```

For EPUB sources, the raw directory should contain:

- `source.epub`
- `source-profile.json`
- `metadata.md`
- `toc.md`
- `manifest.md`
- `chapters/`
- `assets/` when assets are extracted or needed

Never edit the raw archive after ingestion.

## Validation

Run `scripts/book/validate_book_ingest.py`, then run the universal ingest validator and placeholder scan.

Every table-of-contents entry must map to at least one coverage row. Sample every chapter for named examples, formulas, diagrams, tables, tools, metrics, cases, caveats, and exercises; formal pages must contain them or explain disposition.

Do not mark complete if:

- only raw source exists
- only extraction notes exist
- formal pages are copied chapter summaries
- no coverage matrix exists
- old platform tactics are written as current rules
- indexes/log were skipped
- Agent usage template is missing for a learning path
