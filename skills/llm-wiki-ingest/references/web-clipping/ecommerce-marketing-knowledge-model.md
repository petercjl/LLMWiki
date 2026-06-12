# Ecommerce Marketing Knowledge Model

Use this model when ingesting Taobao/Tmall merchant help pages, marketing tool rules, promotion setup guides, price rules, coupon rules, and campaign announcements.

The goal is to make the wiki useful for later prompts such as:

> 请根据我的淘宝营销知识库，帮我规划最合理的营销工具。

## Required Outputs for Rule-Heavy Marketing Clippings

Do not stop at a source summary. Produce or update at least one AI-usable artifact:

1. Tool card
2. Relationship or conflict matrix
3. Scenario decision playbook
4. Query entry page

For a batch of related clippings, prefer fewer stronger pages over many thin pages.

## Tool Card Template

Use one page per major tool when the tool is likely to recur.

Suggested path:

```text
domains/ecommerce-ops/marketing-tools/<tool-slug>.md
```

Suggested structure:

```md
---
title: 淘宝营销工具：工具名
type: concept
created: YYYY-MM-DD
updated: YYYY-MM-DD
domain: ecommerce-ops
tags: [ecommerce, taobao, marketing-tool]
sources:
  - raw/webpages/taobao/...
status: active
---

# 淘宝营销工具：工具名

## 一句话定位

这个工具解决什么经营问题。

## 适用目标

- 拉新 / 转化 / 提高客单 / 清库存 / 大促承接 / 会员运营 / 私域转化等。

## 核心规则

- 用短条目写明资格、时间、价格、叠加、互斥、限制。

## 价格与门槛公式

```text
公式或校验关系
```

## 可叠加 / 互斥关系

| 相关工具 | 关系 | 说明 | 来源 |
|---|---|---|---|

## 最低价与价保影响

| 影响对象 | 是否计入 | 说明 | 来源 |
|---|---|---|---|

## 风险点

- 资损风险
- 到手价变高风险
- 价保风险
- 活动不生效风险

## 适合使用的场景

- 如果...则优先考虑...

## 不适合使用的场景

- 如果...则避免...

## 操作入口

- 后台路径或官方链接。

## 相关页面

- [[domains/ecommerce-ops/marketing-tools/...]]
```

## Relationship Matrix Pages

Create or update a matrix when multiple tools interact.

Suggested paths:

```text
domains/ecommerce-ops/marketing-tools/taobao-marketing-tool-relationship-map.md
domains/ecommerce-ops/marketing-tools/taobao-promotion-stacking-rules.md
domains/ecommerce-ops/marketing-tools/taobao-lowest-price-rules.md
```

Useful matrices:

### Stacking / Exclusion Matrix

| 工具 A | 工具 B | 关系 | 计算口径 | 商家动作 | 来源 |
|---|---|---|---|---|---|
| 优惠券 | 多件优惠 | 互斥择优 | 子订单 | 选择一个工具并加深力度 | raw/... |

Relationship values:

- 可叠加
- 不可叠加
- 互斥择优
- 大促期间不生效
- 计入最低价
- 不计入最低价
- 条件性生效
- 需要完整覆盖周期

### Tool Selection Matrix

| 商家目标 | 推荐工具 | 适用条件 | 避免条件 | 关键风险 | 来源 |
|---|---|---|---|---|---|

### Time / Validity Matrix

| 工具 | 设置提前期 | 最长有效期 | 校验周期 | 特殊日期规则 | 来源 |
|---|---|---|---|---|---|

### Risk Matrix

| 风险 | 触发条件 | 影响 | 应对动作 | 来源 |
|---|---|---|---|---|

## Scenario Playbook

Create a playbook when the rules imply merchant decisions.

Suggested path:

```text
domains/ecommerce-ops/playbooks/taobao-marketing-tool-selection.md
```

Recommended sections:

- 输入信息：商品价格、毛利、活动周期、库存、转化目标、是否大促、是否已有优惠。
- 决策流程：先排除不可用工具，再比较目标到手价和资损风险。
- 推荐逻辑：
  - If goal is direct price-drop and item-level exposure, consider 超级立减.
  - If goal is targeted channel/user/scenario discount, consider 优惠券.
  - If goal is multi-piece conversion or basket growth, consider 多件优惠.
  - If coupon and multi-piece discount conflict under new rules, choose one shop-level tool or combine item-level discount plus one shop-level tool.
- 输出模板：推荐工具、设置参数、风险检查、需要确认的信息。

## Query Entry Page

Create or update a question-oriented page for AI agents.

Suggested path:

```text
queries/taobao-marketing-tool-planning.md
```

Purpose:

- Tell future AI agents where to read before answering merchant planning questions.
- List key pages and required input questions.
- Provide an answer skeleton.

Recommended content:

```md
# 淘宝营销工具规划查询入口

## 回答前必须读取

- [[domains/ecommerce-ops/marketing-tools/taobao-marketing-tool-relationship-map]]
- [[domains/ecommerce-ops/marketing-tools/taobao-promotion-stacking-rules]]
- [[domains/ecommerce-ops/playbooks/taobao-marketing-tool-selection]]

## 需要向商家确认的信息

- 商品类目、价格带、毛利率
- 活动目标
- 活动时间
- 当前已有优惠
- 是否参加大促
- 是否需要定向人群/渠道

## 输出结构

- 推荐工具组合
- 不推荐的工具及原因
- 到手价/让利估算
- 叠加或互斥风险
- 设置步骤
- 需要复核的官方规则
```

## Tables and Examples

When source pages contain examples with prices, preserve them as executable reasoning examples:

```md
## 算价案例

| 场景 | 升级前 | 升级后 | 经营含义 |
|---|---|---|---|
| 商品 A 100 元，买 2 件，优惠券满 200 减 10，多件优惠 9 折 | 170 元 | 180 元 | 新规下店铺级优惠互斥择优，若要维持 170 元，需要加深单一工具力度。 |
```

## Current Taobao Marketing Concepts to Detect

While ingesting, watch for these entities and link them consistently:

- 优惠券
- 店铺券
- 商品券
- 超级立减
- 单品立减
- 多件优惠
- 店铺宝
- 官方立减
- 跨店满减
- 平台大促
- 最低标价
- 最低普惠券后价
- 红线价
- 价保
- 资损校验
- 子订单
