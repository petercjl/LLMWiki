# Placement Rules

Use these rules when deciding where a clipping should become durable knowledge in `/Users/pechen/wiki`.

## Core Principle

Source format decides where raw evidence goes. Knowledge role decides where formal pages go.

Examples:

- A Taobao help page is raw webpage evidence, but the formal knowledge usually belongs in `domains/ecommerce-ops/`.
- A brand case article is raw webpage evidence, but the formal knowledge may belong in `domains/brand-strategy/samples/`.
- A page about Obsidian Web Clipper is raw webpage evidence, but the formal knowledge belongs in `domains/AI Agent工程/01-知识系统/`.

## Recommended Formal Destinations

### Ecommerce Operations

Use `domains/ecommerce-ops/` for:

- Taobao, Tmall, JD, Douyin ecommerce platform rules
- Merchant backend workflows
- Product listing, traffic, conversion, pricing, promotion operations
- Customer service, refund, review, compliance, store health rules

Suggested subfolders when needed:

```text
domains/ecommerce-ops/platform-rules/
domains/ecommerce-ops/merchant-operations/
domains/ecommerce-ops/growth-playbooks/
domains/ecommerce-ops/marketing-tools/
domains/ecommerce-ops/playbooks/
```

For Taobao/Tmall marketing tool rules, prefer `domains/ecommerce-ops/marketing-tools/` for tool cards and rule matrices, and `domains/ecommerce-ops/playbooks/` for scenario decision workflows.

### Brand Strategy

Use `domains/brand-strategy/` for:

- Brand positioning
- Category strategy
- Consumer mindshare
- Brand cases
- Naming, value proposition, differentiation, competitive strategy

Existing useful paths include:

```text
domains/brand-strategy/samples/
domains/brand-strategy/learning-paths/
```

### Visual Production

Use `domains/visual-production/` for:

- Ecommerce main images
- Detail pages
- Creative direction
- Visual diagnosis
- Product image workflows
- Content and asset production rules

### AI Agent Engineering

Use `domains/AI Agent工程/` for:

- LLM Wiki operations
- Obsidian and knowledge systems
- Agent architecture
- Skill design
- Toolchain and browser automation
- Prompt/context engineering
- Evaluation and debugging

Existing subfolders:

```text
domains/AI Agent工程/01-知识系统/
domains/AI Agent工程/02-Agent架构/
domains/AI Agent工程/03-Skill设计/
domains/AI Agent工程/05-工具链/
domains/AI Agent工程/04-提示词与上下文/
domains/AI Agent工程/06-自动化工作流/
domains/AI Agent工程/07-评测与调试/
```

### Shared

Use `shared/` only for cross-domain foundations that are not owned by one specific domain, such as knowledge management, general business frameworks, and reusable thinking models.

### Projects

Use `projects/` only for concrete project context, implementation notes, decisions, and project-specific operating procedures.

### Entities

Use `entities/` for:

- People
- Companies
- Products
- Tools
- Platforms
- Agents

Entity pages can link to domain pages, but should not become long topical essays.

## Five-Question Intake Checklist

Ask these before placing a clipping:

1. Is this original source evidence or durable knowledge?
2. Is the durable knowledge a long-term capability, project context, entity, SOP, comparison, decision, or query?
3. Does an existing formal page already cover this topic?
4. What future question should this page help answer?
5. What raw source proves the claims in the formal page?

## Deletion Standard

A clipping can be deleted from `Clippings/` only after it has one of these outcomes:

- Preserved under `raw/` and converted into formal knowledge.
- Preserved under `raw/` but marked as source-only in `log.md`.
- Moved to `inbox/` because user judgment is needed.
- Identified as duplicate/noise and logged if part of a meaningful batch.
