# Route Audit Protocol

Route audit checks whether compiled wiki knowledge is findable and usable by future agents.

## Mechanical Checks

For each target entry page:

- It is listed from a relevant index or query page.
- It has incoming links from at least one useful route page.
- It has outgoing wikilinks to related concepts, chapters, templates, or evidence.
- Its outline has meaningful sections, not only a title.
- Its wikilinks resolve or unresolved links are explained.

## Report Fields

- `target_paths`
- `cli_status`
- `unresolved_summary`
- `target_reports`
- `global_signals`
- `warnings`
- `recommended_fixes`

## Severity

- P0: target page is not reachable from any index/query/template, or formal pages are shell/thin.
- P1: target is reachable but lacks usage template, outgoing links, or clear outline.
- P2: tags/properties/index wording could improve discovery.

Route audit does not replace compile audit. A page can be well routed but poorly compiled.
