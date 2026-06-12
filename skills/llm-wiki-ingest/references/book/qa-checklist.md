# QA Checklist

Use this checklist before declaring a book ingest complete.

## Mechanical Checks

- Raw source directory exists.
- `source.epub` or source file exists.
- `metadata.md`, `toc.md`, `manifest.md`, and `source-profile.json` exist for EPUB sources.
- Extraction notes directory exists.
- `chapter-inventory.md` exists.
- `coverage-matrix.md` exists.
- Every source chapter appears in coverage matrix.
- Formal directory exists.
- Formal pages have YAML frontmatter.
- Formal pages have `sources`.
- Target domain index is updated.
- Root `index.md` is updated.
- `log.md` has an ingest entry.

## Shell/Thin Page Checks

Run:

```bash
python3 <llm-wiki-audit-and-optimization-skill>/scripts/placeholder_scan.py <formal_path>
```

Expected:

- `SHELL: 0`
- `THIN: 0`, or any thin page is justified, such as a short index.

## Content Checks

Sample at least:

- learning path index
- 2-3 method pages
- Agent usage template
- coverage matrix

Confirm:

- Pages are not book summaries.
- Pages contain models, operating rules, cases, boundaries, and Agent guidance.
- Platform-specific facts have time boundaries.
- Important cases/numbers/tools were not silently dropped.
- Existing wiki pages are linked where relevant.
- Duplicate pages were not created for existing concepts.

## Failure Conditions

Do not mark complete if:

- only raw source exists
- only extraction notes exist
- formal pages are copied chapter summaries
- no coverage matrix exists
- old platform tactics are written as current rules
- indexes/log were skipped
- Agent usage template is missing for a learning path
