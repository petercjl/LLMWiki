# Placement Rules

Read `/Users/pechen/wiki/SCHEMA.md` first. These are practical defaults.

## Formal Knowledge

| Knowledge role | Path |
| --- | --- |
| ecommerce operations, merchant rules, platform operations | `domains/电商运营/` |
| ecommerce API docs / ERP integrations | `domains/电商运营/30-ERP与系统工具/<provider>/` |
| brand strategy, category positioning, brand cases | `domains/品牌策略/` |
| visual production, AI image/video generation, creative workflows | `domains/视觉制作/` |
| AI agents, skills, tools, model APIs, automation workflows | `domains/AI Agent工程/` |
| cross-domain methods | `shared/` |
| project-specific context | `projects/` |
| people, companies, tools, models, platforms | `entities/` |
| reusable query entry | `queries/` |

## Raw Sources

| Source role | Path |
| --- | --- |
| webpage/clipping | `raw/webpages/<provider-or-topic>/` |
| API documentation | `raw/api/<provider>/` |
| book | `raw/books/<book-slug>-<year>/` |
| transcript | `raw/transcripts/` |
| data/report | `raw/data/` |
| source assets | `raw/assets/<source-slug>/` |

## Extraction Notes

Always:

```text
_meta/extraction-notes/<source-slug>/
```

## Naming

- Use Chinese-readable human-facing domain and page paths by default.
- Keep English slugs in aliases, tags, or metadata when useful for search or compatibility.
- Use ordered prefixes for learning paths: `01-...md`.
- Avoid raw source titles as formal page names unless the page is a source summary.

## Ecommerce Placement

- First decide whether the knowledge is platform-specific or platform-independent.
- Taobao/Tmall knowledge belongs under `domains/电商运营/02-淘宝天猫/`.
- JD knowledge belongs under `domains/电商运营/03-京东/`.
- Pinduoduo, Douyin, and Xiaohongshu knowledge should use their platform areas when those areas exist.
- Cross-border ecommerce belongs under `domains/电商运营/20-跨境电商/` unless the page is really about a single domestic platform.
- Platform-independent merchant methods, consulting delivery, channel strategy, settlement interfaces, and reusable playbooks belong under `domains/电商运营/01-通用电商方法/`.
- ERP/API/system-tool knowledge belongs under `domains/电商运营/30-ERP与系统工具/`.
- Do not keep durable ecommerce knowledge under `learning-paths/` merely because it came from a course or book.

## Brand Strategy vs Visual Production

- Use `domains/品牌策略/` when the durable question is about brand positioning, category mind, consumer perception, differentiation, hero-product strategy, product-line strategy, brand memory assets, or why a visual system should exist.
- Use `domains/视觉制作/` when the durable question is about image/video production, ecommerce image conversion, detail pages, layouts, shooting, AI image/video workflows, style libraries, prompt control, or how a visual system is produced repeatedly.
- For brand visual materials, keep strategic asset logic in `domains/品牌策略/04-品牌视觉资产/` and production/execution logic in `domains/视觉制作/02-品牌视觉标准化/` or the relevant AI visual workflow directory.
- Cross-link overlapping pages through a "相关记忆" section instead of merging the two domains.

## Case Libraries

- If a source or existing domain contains many reusable named cases, build or update a case library layer instead of leaving cases scattered only inside theory chapters.
- Brand strategy cases belong in `domains/品牌策略/90-样本/` unless the case is primarily a visual-production execution case or another domain owns the durable question.
- Case pages should be problem-routed and reusable: conclusion, background problem, action moves, why it worked, transferable method, misuse boundary, source links, and related theory pages.
- The domain index should link to the case library with a clear use case such as "想找相似品牌案例做类比".

## Index Rules

- Every formal page appears in `/Users/pechen/wiki/index.md`.
- Domain pages appear in the domain index.
- Internal extraction notes do not need main index entries unless they are formal source-summary pages intended for retrieval.
