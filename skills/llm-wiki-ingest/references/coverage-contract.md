# Coverage Contract

Coverage is the hard quality gate for `llm-wiki-ingest`.

## Source Unit

A source unit is the smallest meaningful piece of source knowledge that could be lost:

- heading or section
- paragraph claim
- table or table row
- code block
- API endpoint, parameter, response field, error code
- image/video/audio with information
- XMind node
- transcript micro-segment
- case/example
- formula/number/price/threshold
- limitation/caveat
- prompt/template
- UI path or operational step

## Required Status Values

| Status | Meaning |
| --- | --- |
| `formalized` | Appears in a formal wiki page. |
| `merged` | Integrated into a broader formal unit. |
| `raw-only` | Preserved in raw, not useful enough for formal pages; reason required. |
| `omitted-with-reason` | Omitted intentionally; reason required. |
| `unresolved` | Needs user judgment, current verification, credentials, or source access. |

## Coverage Matrix Columns

Minimum columns:

```md
| source_unit_id | source_location | source_unit | knowledge_role | target_pages | status | reason_or_notes |
| --- | --- | --- | --- | --- | --- | --- |
```

Add adapter-specific columns:

- XMind: `node_path`, `depth`, `parent_id`, `markers`, `links`
- API docs: `endpoint`, `method`, `request_fields`, `response_fields`, `examples`
- Book: `chapter_id`, `chapter_title`, `page_or_section`
- Transcript: `time_range`, `speaker`, `micro_segment_id`
- Spreadsheet: `sheet`, `range`, `columns`, `metric_units`

## Omission Rules

Never use vague reasons like:

- "not important"
- "minor"
- "summary only"
- "already covered"

Acceptable reasons:

- duplicate of source unit X and merged into page Y
- decorative image with no additional information
- navigation/frontmatter/noise
- raw credentials or sensitive data removed
- obsolete platform UI, preserved raw-only with date
- legal/copyright risk, summarized as concept only
- user confirmation required

## Completion Test

An ingest is incomplete if:

- future Agent must reopen raw to recover a code example, API field, case, formula, parameter, or limitation
- a source heading has no coverage row
- examples are listed but not interpreted for reuse
- raw-only items have no reason
- formal pages are only summaries
- coverage matrix exists but target pages do not contain the referenced knowledge
