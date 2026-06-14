# course-transcript-to-knowledge v1.2.0 Checklist

适用场景：Get 笔记、飞书妙记、课程录音转写、长时口播资料进入 `~/wiki`。

## 一句话目标

不是做摘要，而是把课程知识重构成“可检索、可复用、可让 Agent 调用”的正式理论体系。

## 0. 启动前

必须先读：
1. `~/wiki/AGENTS.md`
2. `~/wiki/SCHEMA.md`
3. `~/wiki/index.md`
4. 最近的 `~/wiki/log.md`
5. 搜索已有相关页面，避免重复建页

## 1. 文件 inspection

每个 transcript 都要先确认：
- 标题
- 日期
- 字数 / 行数 / 时长
- 主要主题
- 是否适合 `品牌策略` / `电商运营` / `视觉制作` / `shared`
- 是单文件处理还是 batch 中的一员

## 2. raw 保留

每个文件都必须单独复制到：
- `raw/transcripts/<slug>-<date>.md`

raw 永不修改。

## 3. extraction notes

每个文件都要有独立 extraction 目录，至少包含：
- `segment-plan.md`
- `micro-segment-plan.md`
- `coverage-matrix.md`
- `segment-knowledge-inventory.md`

如果是大文件，必要时再扩展 `micro-segments/`。

## 4. 正式输出规则

- 用“顺序化 learning path”优先，不要轻易做一页大总纲
- 文件名可以是 slug，但：
  - `title:` 必须是中文
  - 页面 `# 标题` 必须是中文
  - `index.md` 中的人类可见标题必须是中文
- 正式页面不能暴露内部处理过程
- 不能保留：
  - 课堂组织
  - 加分
  - 课间休息
  - 主持串场
  - 学员互动噪音

## 5. Batch 处理纪律

如果一次处理多个 transcript：
1. 先统一 inspection
2. 对每个文件单独决定：
   - raw slug
   - 归档 domain/path
   - 章节规划
   - must-keep anchors
   - 可能的 omit 类型
3. 每个文件独立做 raw / extraction / formal / audit
4. 不要把多个文件直接合成一篇总理论页
5. 最后再统一更新 index/log

## 6. omission audit 最低标准

每个 dense business / brand course，至少检查：
- 12 个 anchors
- 至少 4 个案例/品牌名
- 至少 2 个数字或百分比
- 至少 2 个方法/框架
- 至少 2 个后半段案例或结论

缺失锚点必须分类为：
- `preserve-now`
- `already-absorbed`
- `classroom-logistics`
- `speaker-credential-noise`
- `duplicate-example`
- `low-knowledge-value`

如果课程中出现多个可迁移案例，不要只把案例压缩进理论章节。
需要检查是否存在或需要创建 domain-level 案例库，例如
`domains/品牌策略/90-样本/`。案例库至少要支持：
- 按问题调用案例
- 每个案例有来源 raw / extraction note trace
- 每个案例反链到对应理论页
- 每个案例说明适用边界，避免机械套用

## 7. 数字锚点特别规则

这些数字不能随便丢：
- 百分比
- 增长倍数
- 生命周期区间
- 价格带变化
- 服务/消耗规模
- 搜索占比
- 调研样本量
- 转化 / 跳出率 / 深睡时长等证据型数据

原则：
不是所有数字都要单独成段，
但只要它在老师论证里承担“证据作用”，就应保留或明确说明为什么省略。

## 8. formal page 补强方式

如果 audit 发现缺失，不要机械补一堆“遗漏事实”。
应把缺失锚点嵌回：
- 原因链
- 证据链
- 案例链
- 判断标准
- 对比逻辑

也就是：
补的是“推理结构”，不是“事实仓库”。

## 9. 提交前检查

- `git status --short --untracked-files=all`
- 只 stage 当前 transcript / batch 相关文件
- 不要把旧的无关未提交内容混进来
- 检查 formal pages 是否仍含：
  - `课堂`
  - `老师`
  - `录音`
  - `转写`
  - `原始片段`
  - `大模型扩展分析`
- 确认：
  - `index.md` 已更新
  - domain index 已更新
  - `log.md` 已更新

## 10. 最终结果判断

合格结果应满足：
1. raw 完整
2. extraction notes 完整
3. formal pages 成体系
4. 章节命名清晰
5. omission audit 已完成
6. 关键案例/数字没有无声丢失
7. 可直接给 Agent 用于分析、策划、诊断、生成

## 11. 最短实战理解

传统做法：人反复看课程，再试着应用。

LLM Wiki 做法：
- 先把课程知识编译成系统化页面
- 之后人只需要提出目标
- Agent 去读取最合适的整页理论、案例与判断标准
- 人再判断 AI 的结论是否可行

也就是说，LLM Wiki 不是替你做判断，
而是把“找原文、找方法、找案例、找证据”的成本大幅压缩。
