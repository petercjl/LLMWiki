# Unknown or Mixed Source Adapter

Use when the source type is unclear or combines multiple source types.

## Triage

First classify the source:

- What file formats are present?
- Is the primary knowledge textual, tabular, hierarchical, visual, code/API, or conversational?
- Does it contain multiple separable sources?
- Is any source dynamic, time-sensitive, or login-gated?
- Are there credentials or sensitive data?

Then choose the nearest specific adapter for each component.

## Minimum Handling

Always create:

- raw archive
- source profile
- source inventory
- coverage matrix
- omission audit
- audit handoff

If parsing fails, preserve the source and mark unresolved units rather than pretending ingestion is complete.

## Formal Output

Create only enough formal structure to make the known knowledge usable. Defer uncertain parts with explicit `unresolved` rows.

## Validation

The final report must say which adapter assumptions were used and what remains unknown.
