---
schema_version: 2
page_type: entity
title: "Temporal"
status: active
created: 2026-06-12
updated: 2026-06-12
summary: "Temporal 在本 wiki 中作为 event-history replay 型 durable execution 平台实体。"
maintenance:
  edit_policy: update
validation:
  body_contract: entity
tags:
  - workflow
  - temporal
  - durability
---

## 身份

Temporal 是本 wiki 用于比较 durable execution 和 workflow recovery semantics
的核心平台实体。
在当前证据边界内，它的关键身份不是“能写 workflow code”， 而是 workflow code 由
Event History replay 解释， Activities 承担外部副作用， Timer 和 Schedule
分别处在 execution 内部等待与外部启动规则层。

本页聚焦 Temporal 的 workflow/runtime 语义。
Temporal Cloud、部署运维和 SDK 语言差异不在当前实体边界内。

## 关系与时间线

| 关系 | 当前 wiki 判断 |
| --- | --- |
| 控制表示面 | Temporal workflow code 是 code-authored control representation surface。 |
| 执行与恢复语义 | 核心模式是 Event History 驱动的 deterministic replay。 |
| 副作用边界 | Activity 是承载非确定性 I/O、LLM/API/DB 调用的主要边界。 |
| 时间与触发语义 | Timer 是 Workflow Execution 内部的持久等待；Schedule 是外部启动规则。 |
| 与 Airflow 的边界 | 二者都可有 schedule/trigger/run，但 Temporal 内部由 replay 解释 deterministic program，而 Airflow scheduler 推进 task graph。 |
| 与 agent workload 的关系 | Temporal 可承载 dynamic AI agent 或 deep research agent workload，但这属于 durable execution 上的 workload pattern。 |

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| wiki | [工作流概念比较](../analyses/workflow-concepts-comparison.md) | 将 Temporal 映射为 event-sourced deterministic replay 型 workflow runtime。 |
| wiki | [Temporal Workflows 文档](../sources/temporal/workflows-docs.md) | Workflow Execution、Event History 和 replay 语义。 |
| wiki | [Temporal Workflow 确定性约束文档](../sources/temporal/workflow-deterministic-constraints-docs.md) | deterministic workflow code 与 replay-safe 行为。 |
| wiki | [Temporal Activities 文档](../sources/temporal/activities-docs.md) | Activity 作为外部副作用边界。 |
| wiki | [Temporal Timers and Start Delays 文档](../sources/temporal/timers-delays-docs.md) | Timer 和 Start Delay 的时间语义。 |
| wiki | [Temporal Schedule 文档](../sources/temporal/schedule-docs.md) | Schedule 作为外部启动 Workflow Execution 的规则。 |
| wiki | [Temporal 动态 AI Agent 博客](../sources/temporal/dynamic-ai-agents-blog.md) | Temporal 承载动态 AI agent 的官方示例。 |
| wiki | [Temporal Deep Research Agent 博客](../sources/temporal/deep-research-agents-blog.md) | Temporal 承载 deep research agent 的官方示例。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| Temporal 在当前比较中代表 event-history replay 型 durable workflow runtime。 | 工作流概念比较；Temporal Workflows 与确定性约束 source pages。 | 这是 workflow/runtime 视角，不覆盖 Temporal 全部产品能力。 |
| Temporal Activity 是当前分析中的主要副作用边界。 | Temporal Activities source page；工作流概念比较。 | Activity 幂等和补偿仍需业务设计。 |
| Temporal Timer 与 Schedule 属于不同时间层级。 | Temporal Timers and Start Delays、Schedule source pages。 | 具体 schedule policy 和 namespace 配置不在本页范围。 |
