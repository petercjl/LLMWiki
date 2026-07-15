# Semantic Validation Contract

Use this contract whenever source text was produced or materially reconstructed
by ASR, OCR, subtitle extraction, speech-to-text, or another noisy extraction
step. The semantic gate happens after raw extraction and before knowledge-unit
extraction, placement proposal, or formal writing.

## Required Artifact

Create `_meta/extraction-notes/<source-slug>/semantic-validation.md` and keep the
raw transcript or OCR output unchanged.

The file must begin with these fields:

```text
# Semantic Validation

- Status: passed
- Raw evidence preserved: yes
- Validation scope: <ASR, OCR, subtitles, or mixed>
- Evidence sources: <filename, visual frames, existing wiki, repeated context, domain source, selective re-ASR>
- Systematic variant search: passed
- Formal text checked against normalized anchors: passed
```

`Status` may be `passed`, `not-required`, or `incomplete`. A machine-extracted
source cannot finish with `not-required` or `incomplete`.

Add this exact table:

```text
## High-Risk Anchor Inventory

| anchor_id | source_location | anchor_type | raw_form | normalized_form | evidence | confidence | disposition | formal_handling |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A01 | 00:12-00:18 | platform-or-product | 极创 | 即创 | filename + slide title + existing wiki | high | corrected | use 即创 |
```

Allowed `confidence` values are `high`, `medium`, and `low`. Allowed
`disposition` values are:

- `accepted-as-is`: the extracted form is supported and may be used.
- `corrected`: the normalized form is supported by evidence and replaces the
  extracted form only in interpreted notes and formal pages.
- `unresolved`: evidence is insufficient; mark the claim `待确认`, exclude the
  uncertain term from operational instructions, or require current-source
  verification.
- `excluded-from-formal`: the item is corrupted, decorative, or too unreliable
  to use; preserve it only as raw evidence.

## Mandatory High-Risk Scan

Inventory every detected candidate in these groups:

- platform, product, tool, brand, organization, and person names
- feature names, UI labels, backend fields, menu paths, and command names
- metrics, percentages, money, dates, durations, limits, thresholds, and counts
- negations, comparisons, causal claims, compliance language, and risk boundaries
- ordered operating steps whose meaning would change if one verb or object were wrong

This is not a spelling sweep. Prioritize terms that can change retrieval,
decisions, operations, compliance, or numeric conclusions.

## Evidence And Correction Rules

Use at least two independent signals for a correction when practical. Evidence
may include the source filename, clear slide or subtitle text, repeated spoken
context, an existing trusted wiki page, an authoritative domain source, or a
selective re-ASR of the affected time range. Domain plausibility alone is not
enough for a low-confidence platform label, metric, limit, or compliance claim.

Search the whole raw transcript for every confirmed systematic variant. Record
one row that states the affected range or occurrence count, then ensure every
interpreted occurrence uses the normalized form. Do not rewrite the raw ASR or
OCR artifact.

If a term remains ambiguous, do not rerun the entire source by default. Recheck
the relevant frame, subtitle, neighboring context, or short audio segment. Use
a stronger model only for the affected segment when the decision value justifies
the cost. If it still cannot be resolved, keep it `unresolved`.

## Pass Gate

Set `Status: passed` only when:

1. the high-risk anchor inventory is non-empty for a machine-extracted source;
2. every detected high-risk candidate has a disposition and evidence;
3. confirmed systematic variants were searched across the full raw transcript;
4. unresolved items have explicit safe formal handling;
5. knowledge-unit extraction and formal pages use normalized terms rather than
   unsupported raw forms;
6. raw ASR/OCR evidence remains unchanged.

The validator enforces this artifact contract. It cannot determine semantic
truth by itself; the Agent remains responsible for the evidence-based judgment.
