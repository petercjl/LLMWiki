# Image Knowledge Contract

Use this contract whenever a source contains screenshots, diagrams, charts,
figures, scanned tables, or other images. Images are first-class evidence, but
the portable Wiki retrieval layer remains text-routed unless a separate
multimodal index is explicitly available.

## Separation Of Responsibilities

Keep source acquisition separate from Wiki ingestion:

- A CLI, browser controller, API client, document exporter, or CDP session may
  supply source bytes and structure.
- `llm-wiki-ingest` owns preservation, classification, semantic anchoring,
  coverage, formal-page placement, and validation after the source is acquired.
- Never make one acquisition tool, browser profile, debugging port, or
  author-machine path a prerequisite for the Wiki method.

## Image Classes

Classify every archived image:

| image_class | Meaning | Normal handling |
| --- | --- | --- |
| `knowledge` | Diagram, chart, visual relation, or image-only claim | Analyze, formalize, embed, and caption |
| `procedural` | UI path, control location, or ordered operation | Analyze, formalize near the step, and caption |
| `evidence` | Supports a textual claim or preserves source fidelity | Archive; embed when it materially improves verification |
| `duplicate` | Repeats recoverable text without additional visual value | Archive; raw-only or merge with reason |
| `decorative` | Logo, cover ornament, avatar, separator, or background | Archive when useful; raw-only with reason |
| `sensitive` | Contains credentials, personal data, account details, or secrets | Do not formalize unredacted; record safe disposition |
| `unresolved` | Cannot yet be interpreted or safely classified | Preserve and mark unresolved |

## Durable Assets

Archive source images under a stable Wiki-relative path such as:

```text
raw/assets/<source-slug>/01.png
raw/assets/<source-slug>/02.png
```

Do not rely on expiring CDN URLs or authenticated hotlinks as the only copy.
Preserve original bytes when lawful and authorized. Do not edit an archived
original merely to improve presentation; create a derived asset separately if
redaction, cropping, or annotation is necessary.

## Required Image Inventory

When archived images are passed to validation, create `image-inventory.md` in
the source extraction-notes directory with this exact minimum table contract:

```md
| image_id | source_location | archived_path | image_class | semantic_anchor | target_pages | status | reason_or_notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
```

Use the normal coverage status values. Each `archived_path` must be a durable
Wiki-relative file. A `formalized` or `merged` image must name a target page,
appear in that page, and have a non-empty semantic anchor. Raw-only, omitted,
or unresolved images require a concrete reason.

When one or more images are `formalized` or `merged`, also create
`image-analysis.md`. Record the visual claim, relevant visible text, relation to
the surrounding source, confidence, and any OCR or ambiguity. Do not use OCR
when structured source text already supplies the same content more reliably.

## Semantic Anchors

Every formalized image needs text that lets a text-first Agent retrieve and use
it. Combine:

1. a meaningful section heading;
2. surrounding explanatory text;
3. a knowledge-bearing caption or adjacent sentence;
4. a coverage row or image-inventory row pointing to the formal page.

Do not use captions such as `Figure 1`, `Screenshot`, or `Operation page` alone.
A useful caption states what the image proves or where the user acts, for
example: `The plan settings panel places the audience exclusion control below
the targeting section.`

The formal page should remain useful without reopening raw assets. Text carries
the searchable claim and decision logic; the image carries visual relations,
UI evidence, and detail verification.

## Formal Embedding

Embed a knowledge-bearing image next to the rule, operation, case, or claim it
supports. Use the target Wiki's supported Wiki-relative syntax, such as an
Obsidian embed or standard Markdown image. Avoid author-machine absolute paths
inside formal pages.

Do not force every archived image into formal knowledge. Decorative, duplicate,
unsafe, or low-value images may remain raw-only when the inventory records why.

## Dynamic And Authenticated Sources

For dynamic documents, use the safest available acquisition capability in this
order when practical:

1. official export or documented API;
2. structured page data already available to the authorized session;
3. rendered DOM and directly referenced media;
4. user-authorized browser automation or debugging connection;
5. screenshot plus OCR as a last resort.

This order is an acquisition strategy, not a dependency contract. Never archive
cookies, access tokens, authorization headers, browser profiles, or session
secrets. Inspect structured payloads for sensitive fields before preserving
them. Stop and report when access exceeds the user's authorization.

## Retrieval And Delivery Boundary

Ordinary Wiki search finds the textual semantic anchor, not the pixels. After a
page is routed, a vision-capable Agent may open the linked asset for inspection.
If the answer channel supports media and the image is relevant, it may display
or attach the image. Otherwise return the caption and a valid accessible link or
path. Never claim visual similarity search or pixel-level indexing unless that
separate capability was actually configured and tested.

## Completion Gate

An image-bearing ingest is incomplete when any of these is true:

- a source image has no inventory disposition;
- a knowledge or procedural image exists only behind an external hotlink;
- a formalized image file is missing or unreadable;
- its target page does not embed it;
- its semantic anchor is missing from the target page;
- unique visual knowledge was replaced by a generic prose summary;
- an unredacted sensitive image entered formal knowledge;
- the audit handoff omits image coverage counts or unresolved visual items.
