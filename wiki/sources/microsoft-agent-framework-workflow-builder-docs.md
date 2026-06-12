---
schema_version: 2
page_type: source
title: "Microsoft Agent Framework WorkflowBuilder 文档"
status: active
created: 2026-06-12
updated: 2026-06-12
summary: "Microsoft Agent Framework WorkflowBuilder graph API 文档的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - microsoft-agent-framework
  - workflow-builder
  - graph-workflow
---

## 来源边界

本页只投影 Microsoft Agent Framework 的 Workflow Builder & Execution 文档。
它用于说明 graph workflow、executors、edges 和 execution semantics。
原始材料未保存到 `raw/`；本页直接引用外部 URL 作为主证据。

## 可复用关键主张

- `WorkflowBuilder` 用 executors 和 edges 构造显式工作流图。
- graph workflow 支持条件路由、并行和 streaming 等编排能力。
- 该页说明 `WorkflowBuilder` 用 executors、edges 与 superstep execution
  构造和运行 graph workflow。

## 限制与冲突

- Graph workflow 的能力不应自动外推到 functional workflow 或 Durable Extension。
- 与 LangGraph 的类别比较属于分析页综合判断。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://learn.microsoft.com/en-us/agent-framework/workflows/workflows` | Microsoft Agent Framework WorkflowBuilder 文档；访问时间 2026-06-12。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| `WorkflowBuilder` 是显式 graph workflow surface。 | 上方证据单元。 | 需要与 functional API 分开评价。 |
| Microsoft Agent Framework graph workflow 通过 executors/edges 表达控制流。 | 上方证据单元。 | 本页不证明 Durable Task-backed 恢复。 |
