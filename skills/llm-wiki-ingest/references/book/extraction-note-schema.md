# Extraction Note Schema

Use this reference when creating extraction notes for a book.

## Directory

```text
~/wiki/_meta/extraction-notes/<book-slug>-<year>/
├── source-profile.md
├── source-inventory.md
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

## `source-profile.md`

Record:

- book title
- author
- publisher
- publication date
- ISBN
- source format
- raw source path
- import date
- file hash
- table-of-contents quality
- known extraction issues
- time sensitivity and platform-rule risk

## `segment-plan.md`

Map original book structure:

| segment_id | level | title | source_file | role | process |
| --- | --- | --- | --- | --- | --- |

Recommended `role` values:

- `frontmatter`
- `part`
- `chapter`
- `appendix`
- `copyright`
- `toc`

Recommended `process` values:

- `keep`
- `merge`
- `omit`
- `outdated-review`

## `knowledge-architecture-plan.md`

Design formal output before writing pages:

| target_page | purpose | source_chapters | core_questions | related_existing_pages |
| --- | --- | --- | --- | --- |

Do not force one source chapter to one target page.

## `chapter-inventory.md`

For each source chapter:

| field | meaning |
| --- | --- |
| `source_id` | stable chapter ID |
| `source_title` | original title |
| `source_file` | source HTML/text file |
| `word_count` | rough text length |
| `knowledge_units` | concepts, rules, methods |
| `cases` | brands, products, examples |
| `tools_metrics` | platform tools, metrics, reports |
| `time_sensitivity` | low / medium / high |
| `target_pages` | candidate formal pages |

## `knowledge-unit-inventory.md`

`chapter-inventory.md` is only a navigation and planning layer. A book ingest is not complete until meaningful claims, examples, formulas, tables, diagrams, checklists, caveats, and platform rules have been broken into knowledge-unit rows.

Minimum columns:

| source_unit_id | chapter_id | source_location | source_unit | knowledge_role | evidence_or_example | time_sensitivity | target_pages |
| --- | --- | --- | --- | --- | --- | --- | --- |

Use stable hierarchical IDs for large books, for example `B01-C03-S02-U007`.

## `coverage-matrix.md`

Every source heading/chapter must be represented, but the final matrix should be knowledge-unit level, not merely chapter level.

Minimum columns must match the universal coverage contract:

| source_unit_id | source_location | source_unit | knowledge_role | target_pages | status | reason_or_notes |
| --- | --- | --- | --- | --- | --- | --- |

Book-specific columns should be added after the required columns:

| chapter_id | chapter_title | page_or_section |
| --- | --- | --- |

Use universal statuses only:

- `formalized`: represented in formal wiki pages.
- `merged`: integrated into a broader formal unit.
- `raw-only`: preserved in raw only because it is decorative, legal/frontmatter noise, duplicate, or low knowledge value.
- `omitted-with-reason`: intentionally omitted with a concrete reason.
- `unresolved`: requires user judgment, current verification, credentials, or missing context.

The bundled `scripts/book/generate_coverage_matrix.py` produces a chapter-level starter matrix using these columns. Expand it to knowledge-unit coverage before marking the ingest complete.

## `omission-audit.md`

Record all source material not represented as formal knowledge:

| source_id | title | omission_type | reason |
| --- | --- | --- | --- |

Common reasons:

- copyright page
- table of contents
- duplicated summary
- platform rule outdated
- low knowledge density
- reader comment/testimonial

## `source-to-page-map.json`

Use a JSON object:

```json
{
  "book": "Book Title",
  "raw_source": "raw/books/book-slug-year/source.epub",
  "mappings": [
    {
      "source_unit_id": "ch001",
      "source_title": "Chapter Title",
      "target_pages": ["domains/example/path/01-page.md"],
      "status": "merged"
    }
  ]
}
```
