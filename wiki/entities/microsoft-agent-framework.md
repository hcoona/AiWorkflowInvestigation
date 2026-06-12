---
schema_version: 2
page_type: entity
title: "Microsoft Agent Framework"
status: active
created: 2026-06-12
updated: 2026-06-12
summary: "Microsoft Agent Framework 在本 wiki 中作为 agent/workflow framework 及可选 Durable Extension hosting 实体。"
maintenance:
  edit_policy: update
validation:
  body_contract: entity
tags:
  - workflow
  - microsoft-agent-framework
  - ai-agents
---

## 身份

Microsoft Agent Framework 是本 wiki 用于比较 agent framework 内 workflow
surface、multi-agent orchestration 和可选 durable hosting 的核心实体。
在当前证据边界内，它同时提供 graph workflow surface 和 functional workflow
surface； core workflow runtime 不应默认写成分布式任务平台。

Durable Extension 是该实体的重要 integration/hosting 层： 它可将 durable graph
workflow 映射到 Durable Task orchestration、 activity、entity 和
sub-orchestration work items。
但这条证据只覆盖 graph-based workflow model， 不能外推为 functional workflow
surface 或所有 Microsoft Agent Framework surfaces 的默认语义。

## 关系与时间线

| 关系 | 当前 wiki 判断 |
| --- | --- |
| 控制表示面 | 同时包含 graph workflow surface 与 functional workflow surface。 |
| core runtime | 更接近嵌入式 framework runtime；需按具体 surface 判断状态真源和恢复语义。 |
| Durable Extension | 可选 Durable Task-backed hosting/integration 层，支持 checkpoint、resume、HITL 和跨 worker process/host 恢复。 |
| per-step work-item placement | durable graph-workflow 路径下，普通 executor、agent executor 和 subworkflow 可映射到 Durable Task work items。 |
| 与 Temporal/Airflow 的边界 | 不能因为有 workflow 或 durable extension 就直接等同于 Temporal replay 或 Airflow scheduler。 |
| 与 LangGraph 的边界 | 二者都可表达 graph workflow，但 MAF 的 Durable Extension 和 LangGraph 的 checkpointer/Agent Server 边界不同。 |

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| wiki | [工作流概念比较](../analyses/workflow-concepts-comparison.md) | 将 MAF 区分为 core surfaces 和 Durable Extension durable graph-workflow 路径。 |
| wiki | [Microsoft Agent Framework Overview 文档](../sources/microsoft-agent-framework/overview-docs.md) | agents/workflows 总览。 |
| wiki | [Microsoft Agent Framework Workflows 概览](../sources/microsoft-agent-framework/workflows-overview-docs.md) | workflows 与 agent orchestration 定位。 |
| wiki | [Microsoft Agent Framework Functional Workflows 文档](../sources/microsoft-agent-framework/functional-workflows-docs.md) | functional workflow API 与 `@workflow` / `@step`。 |
| wiki | [Microsoft Agent Framework WorkflowBuilder 文档](../sources/microsoft-agent-framework/workflow-builder-docs.md) | graph workflow surface、executors、edges 与 execution。 |
| wiki | [Microsoft Agent Framework Durable Extension 文档](../sources/microsoft-agent-framework/durable-extension-docs.md) | Durable Task-backed execution、checkpoint、resume、HITL 和 hosting model。 |
| wiki | [Microsoft Agent Framework Durable Workflow Registration 源码](../sources/microsoft-agent-framework/durable-workflow-registration-source.md) | durable graph workflows、activities 和 entities 的注册路径。 |
| wiki | [Microsoft Agent Framework Durable Executor Dispatcher 源码](../sources/microsoft-agent-framework/durable-executor-dispatcher-source.md) | executor 到 activity、entity、sub-orchestration 或 external event 的 dispatch。 |
| wiki | [Durable Task Scheduler 文档](../sources/microsoft-durable-task/scheduler-docs.md) | Durable Task work item dispatch 语义。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| Microsoft Agent Framework 在当前比较中代表 agent framework 内的 graph/functional workflow surfaces。 | Overview、Workflows Overview、Functional Workflows 和 WorkflowBuilder source pages。 | functional API 状态和跨语言差异需按版本复核。 |
| Core workflow surface 不应默认写成分布式任务平台。 | 工作流概念比较；MAF workflow source pages。 | 具体 host 或 extension 可改变执行边界。 |
| Durable Extension 是可选 Durable Task-backed hosting/integration 层，且本页细粒度映射只覆盖 durable graph-workflow 路径。 | Durable Extension、registration、dispatcher 和 Durable Task Scheduler source pages。 | 不能外推为 functional workflow surface 或所有 MAF surfaces 的默认语义。 |
