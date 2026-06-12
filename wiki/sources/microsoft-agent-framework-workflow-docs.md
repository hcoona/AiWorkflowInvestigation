---
schema_version: 2
page_type: source
title: "Microsoft Agent Framework 工作流文档投影"
status: active
created: 2026-06-12
updated: 2026-06-12
summary: "Microsoft Agent Framework agents、workflows 与 Durable Extension 文档的来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - microsoft-agent-framework
  - workflows
  - durability
  - agent-runtime
---

## 来源边界

本页汇总 Microsoft Learn 的 overview、workflows、functional、workflows/workflows
与 durable-extension 文档。
它们分别覆盖 agents 与 workflows 的分工、graph 与 functional 两条 workflow
surface、checkpointing/HITL，以及 Durable Extension 如何引入 Durable Task-backed
durability。

本页不把 Microsoft Agent Framework
视为单一成熟度平面的产品，而是把它视为一个正在演进的 workflow/agent 组合面：图式
workflow、functional workflow、Durable Extension 与安装包语义并不完全同步成熟。

## 可复用关键主张

- Agent Framework 明确区分 agents 与 workflows：agents 更偏 LLM
  驱动的工具使用，workflows 更偏显式流程编排。
- `WorkflowBuilder` graph surface 用 `executors` 和 `edges` 组织流程；functional
  `@workflow`/`@step` surface 则用原生 Python 控制流表达逻辑。
- Durable Extension 把 durable execution 引入 agents、multi-agent orchestrations
  与 workflows，可用于 checkpoint、resume、HITL 等场景。
- 公开文档对成熟度的表述并不完全一致：functional API 明确
  experimental，而部分安装示例又使用 prerelease 旗标，因此不应把整个 surface
  简化为统一 GA。

## 限制与冲突

- Graph API 与 functional API 的成熟度信号不同，不能按同一稳定级别处理。
- Durable Extension 是 hosting/integration 层，不是对整个 Agent Framework
  的替代。
- 官方文档同时出现“supported”与“experimental/prerelease”信号；本页把这理解为
  surface 分层成熟，而不是自相矛盾。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://learn.microsoft.com/en-us/agent-framework/overview/` | overview，agents/workflows 总览；访问时间 2026-06-12。 |
| external | `https://learn.microsoft.com/en-us/agent-framework/workflows/` | workflows 概览；访问时间 2026-06-12。 |
| external | `https://learn.microsoft.com/en-us/agent-framework/workflows/functional` | functional workflow API 与 `@workflow` / `@step`；访问时间 2026-06-12。 |
| external | `https://learn.microsoft.com/en-us/agent-framework/workflows/workflows` | `WorkflowBuilder` graph API、executors、edges 与 execution；访问时间 2026-06-12。 |
| external | `https://learn.microsoft.com/en-us/agent-framework/integrations/durable-extension` | Durable Extension 与 Durable Task-backed execution；访问时间 2026-06-12。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| Agent Framework 明确区分 agents 与 workflows，且 workflows 提供显式流程编排能力。 | 上方证据单元 1、2。 | agents 与 workflows 的职责边界在不同文档里被不同方式描述。 |
| `WorkflowBuilder` graph surface 与 functional `@workflow`/`@step` surface 同时存在。 | 上方证据单元 2、3、4。 | functional API 明确 experimental，不能按统一 GA 处理。 |
| Durable Extension 把 durable execution 引入 Agent Framework workflows，并以 Durable Task 作为底层能力。 | 上方证据单元 1、5。 | 这是 integration/hosting 层，不是整个框架的唯一运行方式。 |
| 公开文档的成熟度信号是混合的，不能把整个 surface 简化为单一稳定等级。 | 上方证据单元 1、3、5。 | 需要把 experimental 与 prerelease 语义纳入风险判断。 |
