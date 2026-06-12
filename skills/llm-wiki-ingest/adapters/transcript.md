# Transcript Adapter

Use for course transcripts, meeting transcripts, Feishu Minutes, audio/video transcription output, interviews, and Q&A sessions.

This adapter absorbs the previous `course-transcript-to-knowledge` workflow. Use it inside `llm-wiki-ingest`; do not maintain a separate transcript skill.

## Non-Negotiable Standard

The goal is not a summary. Reconstruct the course or spoken material into a searchable, reusable, Agent-callable knowledge system. Remove classroom chronology and oral noise, but do not shrink knowledge.

For dense course material, especially business, ecommerce, brand, visual-production, or AI-agent methodology courses:

- preserve reasoning chains, cases, frameworks, numbers, examples, Q&A, caveats, and implied decision rules
- reconstruct implicit logic and causal chains
- convert source-specific classroom identities into neutral formal knowledge
- mark uncertain transcript-derived claims as `待确认`
- preserve evidence anchors or classify omissions with reasons

Load `references/transcript/checklist-v1.2.0.md` before processing long or noisy transcripts.

## Intake

Record:

- source path, title, speaker(s), date, duration
- transcript type: course, meeting, interview, workshop, Q&A
- timestamp availability
- transcript quality issues
- repeated filler/noise pattern
- source language and desired formal language

## Inventory

Segment by semantic micro-units, not only by timestamps.

For transcripts over 30k characters or longer than about 60 minutes, use a hierarchical segmented pipeline:

1. segment plan by chapter summary, timestamps, or 10-20 minute blocks
2. micro-segment plan for each dense idea, case action, decision criterion, or Q&A insight
3. per micro-segment reconstruction with `cleaned_text`, `plain_meaning`, `expanded_analysis`, and `knowledge_form`
4. coverage matrix and omission audit before formal completion

Track:

- timestamp range when available
- speaker
- original topic
- reconstructed topic
- claim, method, example, objection, decision, action item, question
- whether source language should be preserved, normalized, or removed

Spoken material often contains incomplete logic. Reconstruct implied context, but keep source-grounded claims distinct from enrichment.

## Formal Output

Choose:

- course knowledge system or learning path
- meeting decision/action record
- concept pages
- operating playbooks
- FAQ or objection-handling pages
- source-summary page

Remove filler and disfluency from formal pages, but do not remove knowledge. Merge repetition with explicit coverage references.

Prefer a sequential learning path for substantial courses. A course may have a short source/course index for traceability, but main output should be durable formal theory pages, concept pages, playbooks, or Agent-use templates.

Formal pages must not expose internal processing headings such as `cleaned_text`, `plain_meaning`, `expanded_analysis`, or `knowledge_form`.

Batch transcript ingestion discipline:

- inspect all files first
- preserve separate raw transcript for each file
- create separate extraction notes and coverage records per file
- write separate formal outputs unless the user explicitly asks for later synthesis
- update index/log only after all files meet minimum quality

## Validation

No major timestamp block may be coverage-empty. Check that questions, examples, objections, and action decisions were not lost because they appeared conversational rather than structured.

For dense business or brand courses, omission audit must sample named anchors, cases/brands, numbers, methods/frameworks, and late-session examples or conclusions. If a numeric anchor supports evidence, preserve it or explicitly explain omission.
