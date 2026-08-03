# Web Clipping Adapter

Use for Obsidian Web Clipper notes, saved webpages, product pages, blog posts, console pages, and clipped API docs.

This adapter absorbs the previous `wiki-clippings-ingest` workflow. Use it inside `llm-wiki-ingest`; do not maintain a separate Clippings skill.

## References

Load only when needed:

- `references/web-clipping/source-type-profiles.md`
- `references/web-clipping/placement-rules.md`
- `references/web-clipping/ecommerce-marketing-knowledge-model.md`
- `references/image-knowledge-contract.md` when the page contains informative images

## Intake

Capture these fields in `source-profile.md`:

- clipping file path
- original URL
- clipped title
- created/captured date
- visible source publish/update date, if present
- page type: article, product page, API doc, console page, pricing page, case library, mixed
- whether current web verification is required
- whether the page is login-gated or dynamic
- image count, visual density, and whether images carry unique knowledge
- acquisition capability used, kept separate from Wiki ingestion

## Inventory

Inventory every:

- frontmatter field with source value
- heading and section
- paragraph claim
- table row, metric, price, parameter, version, or model ID
- image/video/audio item that carries information
- prompt, example, case, demo, scenario, or UI path
- API endpoint, model name, code block, request/response detail
- warning, limitation, eligibility condition, region condition, or date-sensitive claim

For clipped pages with screenshots or media placeholders, preserve the text reference even when the binary asset is unavailable.

For image-bearing pages, archive original image bytes when authorized and follow
`references/image-knowledge-contract.md`. Inventory decorative images too, but
only formalize images that carry knowledge, procedural guidance, or useful
evidence.

## Dynamic Page Acquisition Branch

Dynamic page reading is a source-acquisition concern, not a Wiki dependency.
Use the safest available capability in this order when practical:

1. official export or documented API;
2. structured page data available to the authorized session;
3. rendered DOM and referenced media;
4. user-authorized browser automation or debugging connection;
5. screenshot plus OCR as a last resort.

Do not name or require a particular CLI, debugging port, browser profile, or
Agent-specific tool in the portable core. Record the capability and evidence in
`source-profile.md`, while keeping acquisition implementation details outside
formal knowledge. Never preserve cookies, access tokens, authorization headers,
profiles, or session secrets. Inspect structured payloads before archiving.

## Raw Handling

Archive to:

```text
raw/webpages/<provider-or-topic>/<source-slug>-<capture-date>.md
```

Archive durable page images separately under
`raw/assets/<source-slug>/`; do not leave an authenticated or expiring hotlink as
the only copy.

If the page is really API documentation, also use `api-docs.md` for modeling after raw queue handling.

Only remove the original file from `Clippings/` after raw archive, coverage matrix, formal page, index update, log entry, and audit handoff exist.

## Formal Output

Choose one or more:

- product/tool/entity card
- capability map
- API reference page
- usage playbook
- prompt/case library
- decision page
- source-summary page when the source itself is important

Do not collapse examples into a generic statement. Each case must remain recoverable as a reusable pattern, prompt template, parameter example, or limitation.

For ecommerce marketing clips, preserve tool purpose, eligibility, stacking/exclusion rules, pricing/discount formula, platform UI path, timing rules, risk and asset-loss notes, and operational decision criteria. Convert them into tool cards, rule matrices, selection playbooks, query entries, or Agent usage templates as appropriate.

## Validation

Check that every source heading appears in coverage. Run `rg` for all model names, prices, endpoints, IDs, examples, and prompts across the formal pages.

For image-bearing pages, also verify that every archived image has an inventory
disposition and every formalized image exists locally, appears in its target
page, and has a searchable semantic anchor.
