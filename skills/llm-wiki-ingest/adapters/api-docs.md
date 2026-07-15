# API Docs Adapter

Use for developer documentation, SDK docs, endpoint references, OpenAPI specs, code examples, authentication docs, model cards with API invocation details, and API pages captured by a web clipper.

This adapter absorbs the previous `api-docs-wiki-ingest` workflow. Use it inside `llm-wiki-ingest`; do not maintain a separate API-docs skill.

## References And Scripts

Load only when needed:

- `references/api-docs/extraction-strategy.md`
- `references/api-docs/api-knowledge-model.md`
- `references/api-docs/wiki-output-layout.md`

When a normalized scrape JSON exists and category manuals are needed, use:

```bash
<verified-python> <skill>/scripts/api/compile_api_reference.py \
  --input $WIKI_ROOT/raw/api/<provider>/<full-scrape>.json \
  --output-dir $WIKI_ROOT/domains/<domain>/api/<provider>/reference \
  --title-prefix "<Provider>" \
  --domain <domain> \
  --source "raw/api/<provider>/<full-scrape>.json"
```

## Intake

Record:

- provider, product, API version, region, base URL
- docs URL and capture/update date
- auth scheme
- endpoints and methods
- SDK languages shown
- model IDs or resource IDs
- pricing/rate-limit/version deprecation signals
- whether official docs must be checked for currentness

## Inventory

Every API detail is a source unit:

- endpoint path and method
- auth header, token scope, signature rule, region condition
- request field, type, requiredness, default, enum, range, unit
- response field, status, streaming/event shape
- error code, retry rule, rate limit, quota
- SDK installation and initialization
- every code block and command
- every example request/response
- model capability, constraint, price, latency, supported modality
- migration/deprecation note

## Formal Output

Prefer a compact but complete reference manual:

- overview and current-source note
- authentication and environment setup
- endpoint map
- request schema table
- response schema table
- examples copied or faithfully reconstructed within copyright limits
- usage recipes and failure handling
- Agent-ready payload templates
- unresolved/currentness checks

When code examples are long, preserve their structure and all parameters; do not reduce them to prose.

At minimum, create or update:

- API home/index page
- capability map organized by business task
- authentication/call contract page or section
- skill-building guide for future agents
- category endpoint manuals when endpoint tables are substantial
- query page for future prompts when the API will be reused

Also compile business-facing views: which endpoint to use for which job, common extraction plans, field interpretation notes, endpoint joins, export/report recipes, and risk notes for write endpoints.

## Validation

For each endpoint, verify the formal page contains method, path, auth, required parameters, example payload, response shape, and known caveats. If any are absent from source, mark `unresolved`, not inferred as known.
