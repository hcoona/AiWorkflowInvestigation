---
schema_version: 2
page_type: source
title: "Temporal 工作流文档投影"
status: superseded
created: 2026-06-12
updated: 2026-06-12
summary: "已被更细粒度的 Temporal 单来源投影页取代。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - temporal
  - workflow
  - durable-execution
  - ai-agents
---

> [!WARNING] 已被取代
> 本页已被 [Temporal Workflows 文档](temporal-workflows-docs.md)、
> [Temporal Workflow 确定性约束文档](temporal-workflow-deterministic-constraints-docs.md)、
> [Temporal Activities 文档](temporal-activities-docs.md)、
> [Temporal 动态 AI Agent 博客](temporal-dynamic-ai-agents-blog.md) 和
> [Temporal Deep Research Agent 博客](temporal-deep-research-agents-blog.md)
> 取代。
> 原因：source page 应投影一个主要上游证据对象，不能把多个独立外链聚合为 n:
> 1 证据锚点。 取代日期：2026-06-12。
> 除修复该提示、链接或证据链外，不要继续更新本页。

## 来源边界

本页汇总 Temporal 官方 Workflow
文档与两篇官方博客：`/workflows`、`/workflow-definition#deterministic-constraints`、`/activities`
以及 AI agent 相关文章。
Temporal 的关键信息不在于“是否能跑
agent”，而在于其工作流必须确定性、活动可以承载非确定性副作用，以及执行可通过
Event History/replay 恢复。

## 可复用关键主张

- Workflow 是由代码定义的步骤序列；执行恢复依赖 Event History/replay。
- Workflow 代码必须确定性；非 replay-safe 的时间、随机数、网络调用应放在
  Activities 中。
- Activities 是执行外部系统调用、LLM 调用、数据库查询、文件 I/O
  等副作用的地方，允许非确定性，但应尽量幂等。
- Temporal 的 AI agent 文章说明：agent 可以被表达为“确定性的编排层 + 非确定性的
  Activities/工具调用”，因此 agent 模式是可承载的上层工作负载，而不是替代其
  durable execution 模型。

## 限制与冲突

- AI agent 相关文章属于应用模式示例，不应被解读为 Temporal 已经变成专用 agent
  runtime。
- 文档强调 Workflow 必须确定性，但 Activities、LLM 调用与外部 I/O 不在 replay
  路径中；理解时应把两层分开。
- 官方文档与博客会持续演进；本页只记录当前访问版本所支持的结论。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://docs.temporal.io/workflows` | Workflow 定义、执行与 Event History/replay；访问时间 2026-06-12。 |
| external | `https://docs.temporal.io/workflow-definition#deterministic-constraints` | Workflow 确定性约束与 replay-safe 行为；访问时间 2026-06-12。 |
| external | `https://docs.temporal.io/activities` | Activities 承担外部 I/O、LLM 调用与其他副作用；访问时间 2026-06-12。 |
| external | `https://temporal.io/blog/of-course-you-can-build-dynamic-ai-agents-with-temporal` | 动态 AI agent 示例；访问时间 2026-06-12。 |
| external | `https://temporal.io/blog/how-to-build-deep-research-agents-using-temporal-and-braintrust` | 深度研究 agent 示例；访问时间 2026-06-12。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| Temporal 的 Workflow 定义、执行和恢复依赖 Event History/replay，且 Workflow 代码必须确定性。 | 上方证据单元 1、2。 | replay-safe APIs 之外的外部副作用不能直接进入 Workflow。 |
| Activities 承担 LLM/API/DB/I/O 等非确定性副作用，并应尽量幂等。 | 上方证据单元 3。 | Activities 可能被重试；幂等性仍然重要。 |
| Temporal 可以承载动态 AI agent 和 deep research pipeline，但这些只是建立在 durable execution 之上的应用模式。 | 上方证据单元 4、5。 | 博客示例不等于专用 agent runtime。 |
