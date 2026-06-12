# Formal Page Patterns

Use this reference when writing formal pages from book material.

## Learning Path Index

Use `type: source-summary`.

Recommended sections:

```markdown
# Learning Path Title

## 来源

## 这组页面解决什么问题

## 阅读顺序

## Agent 使用方式

## 原始资料与覆盖
```

## Method Page

Use `type: concept` or `type: playbook`.

Recommended sections:

```markdown
# Page Title

## 问题定义

## 核心模型

## 操作流程

## 判断标准

## 案例与证据锚点

## 适用边界

## Agent 使用提示

## 来源与边界
```

## Handling Old Platform Advice

For platform books, separate stable method from time-bound tactic:

```markdown
## 平台时间边界

本页来源包含 2018 年淘宝运营语境。以下内容应作为历史规则或方法启发使用，实际执行前需要用当前平台规则、生意参谋/千牛后台、官方文档或实时数据复核：

- ...
```

Then convert:

- old tool names into "platform tool/function class"
- old ranking rules into "ranking factor category"
- old campaign tactics into "campaign planning principle"

## Source Citation Pattern

Keep citations short:

```markdown
来源锚点：`raw/books/book-slug-year/chapters/ch033-title.md`，原书第 2 篇第 8 讲。
```

Do not quote long book passages. Rewrite as durable knowledge.

## Agent Usage Template Page

The final page should help future Agents answer applied questions.

Recommended sections:

```markdown
# Agent 使用模板：...

## 先读哪些页面

## 诊断输入

## 诊断步骤

## 输出结构

## 不得推断

## 需要复核的当前平台信息
```

Make the template operational enough that an Agent can route to the right pages without rereading the whole book.
