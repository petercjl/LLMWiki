# Source Adapter Map

Use this file before choosing an adapter.

## Selection Rules

Choose by source knowledge shape, not only file format.

| Signal | Adapter |
| --- | --- |
| File is under `/Users/pechen/wiki/Clippings` or Obsidian Web Clipper metadata exists | `web-clipping.md` |
| Endpoint docs, SDK docs, API reference, auth/signature docs, model API console page | `api-docs.md` |
| EPUB, PDF book, manuscript, long published book-like source | `book.md` |
| Course transcript, meeting transcript, lecture, Feishu Minutes, ASR text | `transcript.md` |
| `.xmind`, mind map, topic tree, node hierarchy | `xmind.md` |
| Spreadsheet, CSV, Excel, data report, table-heavy market report | `spreadsheet-report.md` |
| Local Markdown documentation, manual, README, spec | `markdown-doc.md` |
| Mixed or no known shape | `unknown-source.md` |

## Multi-Adapter Cases

- Web clipping of API docs: use `web-clipping` for queue/raw handling, then `api-docs` for knowledge modeling.
- Web clipping of product/tool page: use `web-clipping` plus `markdown-doc` or `api-docs` depending on whether endpoint/call details exist.
- Book with diagrams/tables: use `book`; record diagrams/tables as source units.
- XMind exported into Markdown: use `xmind` if node hierarchy is still recoverable; otherwise `markdown-doc`.
- Spreadsheet report with charts: use `spreadsheet-report`; chart meanings are source units.

## Adapter Output Contract

Every adapter must produce:

- raw archive path
- source profile
- source inventory
- knowledge-unit inventory
- coverage matrix
- omission audit
- formal page plan
- audit handoff

If an adapter cannot produce one of these because the source is tiny, it must still create a compact coverage checklist and audit handoff.
