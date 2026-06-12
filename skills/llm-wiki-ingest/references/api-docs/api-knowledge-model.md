# API Knowledge Model

## Required Artifact Types

### Raw Archive

Location:

```text
raw/api/<provider-slug>/
```

Preserve:

- Full scrape JSON.
- Full Markdown archive.
- Compact endpoint index.
- Auth/signature docs.
- OpenAPI/Postman/spec files when available.

### API Home Page

Purpose: entry point for the provider API knowledge.

Must include:

- Provider/product name.
- Official docs URL.
- API version/date if known.
- Endpoint count by category.
- Links to capability map, auth/call contract, reference manuals, skill-building guide, and raw sources.
- Known gaps and confidence.

### Capability Map

Purpose: let an AI choose APIs by business goal.

Organize by task, not by documentation category:

- read/query data
- create/update business objects
- inventory/reporting/export
- master data
- orders/returns/procurement
- callbacks/sync/acknowledgement

For each task include recommended endpoint, alternatives, key filters, output fields, and caveats.

### Auth / Call Contract

Purpose: enable code generation once credentials are available.

Must include:

- Required credential names and origin.
- Common request fields.
- Signature/token process.
- Environment URLs.
- Common response format.
- Pagination/time-window/rate-limit rules.
- Minimal pseudocode or verified sample when possible.

### Category Endpoint Manuals

Purpose: concrete endpoint usage.

Each category page should include:

- Table of endpoints in that category.
- One section per endpoint.
- Request URLs.
- Common/auth params.
- Business request params.
- Response fields.
- Nested object fields.
- Examples.
- Notes, side effects, and source URL.

This is the main artifact future agents use to write code.

### Skill-Building Guide

Purpose: tell future Codex/Hermes agents how to create a working skill/script using the API.

Include:

- Which reference pages to read first.
- How to locate endpoints by business goal.
- Required credential placeholders.
- Recommended client architecture.
- Pagination/export pattern.
- Error handling.
- Testing checklist.

### Query Pages

Purpose: pre-shaped answers for repeated future prompts.

Examples:

- "根据某 ERP API 知识库，帮我导出库存资产 Excel"
- "根据某平台 API，创建商品库存查询 skill"
- "根据某 API，写订单同步脚本"

Query pages should point to exact endpoint manuals and include field formulas or data flow.

## Endpoint Section Template

```md
### <service>: <apiName>

| 项目 | 内容 |
|---|---|
| 分类 |  |
| 服务名 | `service` |
| 方法/路径 |  |
| 描述 |  |
| 文档 URL |  |

#### 请求地址

...

#### 公共请求参数

...

#### 业务请求参数

...

#### 业务响应参数

...

#### 示例

...

#### 注意事项

- 分页:
- 时间窗口:
- 副作用:
- 前置条件:
```

## Quality Bar

The formal wiki is not acceptable if:

- Endpoint manuals only say "see raw archive".
- Auth/signature details are missing when the source docs include them.
- Required request fields are not visible.
- Response fields are not visible.
- A future agent cannot write a first working script from the formal pages plus credentials.
