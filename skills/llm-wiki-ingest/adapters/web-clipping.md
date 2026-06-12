# Web Clipping Adapter

Use for Obsidian Web Clipper notes, saved webpages, product pages, blog posts, console pages, and clipped API docs.

This adapter absorbs the previous `wiki-clippings-ingest` workflow. Use it inside `llm-wiki-ingest`; do not maintain a separate Clippings skill.

## References

Load only when needed:

- `references/web-clipping/source-type-profiles.md`
- `references/web-clipping/placement-rules.md`
- `references/web-clipping/ecommerce-marketing-knowledge-model.md`

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

## Raw Handling

Archive to:

```text
raw/webpages/<provider-or-topic>/<source-slug>-<capture-date>.md
```

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
