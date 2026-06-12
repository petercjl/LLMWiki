# Extraction Strategy

## Prefer Official Structured Sources

Look first for:

- OpenAPI/Swagger JSON: `openapi.json`, `swagger.json`, `/v3/api-docs`, `/api-docs`.
- Postman collections.
- Static API reference pages with tables.
- In-page JSON state, such as `__NEXT_DATA__`, Nuxt payloads, or docs bundles.
- Network requests that return endpoint metadata.

If a structured spec exists, preserve it as raw evidence and use it as the primary source for endpoint manuals.

## Website Shapes

### Static HTML Docs

Use browser/web/open commands to capture pages. Extract headings, tables, code blocks, and links. Preserve source URL and fetch date.

### SPA or Interactive Docs

Use Chrome DevTools MCP:

1. Open the docs page.
2. Inspect the accessibility snapshot for categories and endpoint links.
3. Use `evaluate_script` to read DOM, route state, embedded JSON, and link lists.
4. Click or fetch each endpoint page when content loads per route.
5. Capture network requests if endpoint metadata comes from API calls.

### Login-Gated Docs

Use the user's existing logged-in browser session only when available. Do not ask for or save passwords, tokens, cookies, app secrets, or production credentials. If the docs expose tenant-specific values, replace them with placeholders in formal pages.

### OpenAPI/Swagger Docs

Capture:

- `paths`
- `components.schemas`
- security schemes
- servers/base URLs
- parameters
- examples
- response schemas

Create endpoint manuals from operations and a separate schema/reference page if shared models are large.

### Poorly Structured Docs

If tables are not accessible:

- Preserve full text and screenshots/raw HTML as evidence.
- Extract endpoint facts manually into the normalized model.
- Mark uncertain fields and quote source dates.

## Normalized JSON Shape

A scrape JSON should aim for:

```json
{
  "sourceUrl": "https://docs.example.com/api",
  "scrapedAt": "YYYY-MM-DDTHH:mm:ssZ",
  "endpointCount": 10,
  "categories": [{"name": "Inventory", "count": 3}],
  "endpoints": [
    {
      "category": "Inventory",
      "service": "stock.query",
      "apiName": "Query Stock",
      "description": "Query stock balance",
      "docUrl": "https://docs.example.com/api/stock.query",
      "method": "POST",
      "path": "/stock/query",
      "tables": [
        {"kind": "request_urls", "rows": [["Environment", "URL"], ["Prod", "https://api.example.com/stock/query"]]},
        {"kind": "common_request_params", "rows": [["Name", "Field", "Type", "Required", "Description"]]},
        {"kind": "business_request_params", "rows": [["Name", "Field", "Type", "Required", "Description"]]},
        {"kind": "business_response_params", "rows": [["Name", "Field", "Type", "Required", "Description"]]}
      ],
      "examples": [{"title": "Request", "language": "json", "body": "{}"}],
      "fullText": "..."
    }
  ],
  "errors": []
}
```

Do not force every provider into this exact shape. Use it as the target because the bundled reference compiler understands it.
