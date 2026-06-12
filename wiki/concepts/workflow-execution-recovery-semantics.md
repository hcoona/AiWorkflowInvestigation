---
schema_version: 2
page_type: concept
title: "工作流执行与恢复语义"
status: active
created: 2026-06-12
updated: 2026-06-12
summary: "比较工作流运行时如何解释控制表示、放置工作单元、持久化状态并从故障中恢复。"
maintenance:
  edit_policy: update
validation:
  body_contract: concept
tags:
  - workflow
  - durability
  - recovery
---

## 定义

工作流执行与恢复语义描述 runtime 如何解释控制表示、选择一等调度/放置单元、
持久化可信状态，并在崩溃后恢复“当前位置”。
它包含四个相互关联但不能混为一谈的轴：
执行解释器、执行放置粒度、状态真源和恢复模型。

这个概念的核心问题不是“workflow 写成 DAG、graph 还是 code”，
而是“谁解释它、运行时调度什么、哪份状态可信、恢复时重建什么”。

## 在分析中的用途

[工作流概念比较](../analyses/workflow-concepts-comparison.md)
用这个概念解释为什么 Airflow、Temporal、Microsoft Agent Framework 和 LangGraph
即使都能表达多步控制流，也不能直接互相替代：

- Airflow scheduler 根据 metadata DB 中的 DagRun、TaskInstance 和 mapped task
  state 推进可调度任务集合。
- Temporal worker 通过 Event History replay 重新执行 deterministic workflow
  code， 并重建 replay-safe 局部状态和命令流。
- Microsoft Agent Framework core 更接近嵌入式 framework runtime； Durable
  Extension 的 durable graph-workflow 路径才映射到 Durable Task work items。
- LangGraph OSS 是同进程 graph runtime； Agent Server 普通模式主要是 run-level
  queue worker； distributed runtime 只能在一手证据支持范围内描述为
  orchestration/execution process 分离。

## 边界与非等价关系

- checkpoint resume 不等于 event-sourced deterministic replay。
- per-run queue worker 不等于每个图节点都是用户可控的分布式放置单元。
- Durable Extension 下的 graph-workflow work-item 映射不能外推为所有
  Microsoft Agent Framework surfaces 的默认语义。
- 状态真源和恢复模型必须一起看：
  只知道状态写在哪里，不足以说明崩溃后如何恢复控制流。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| wiki | [工作流概念比较](../analyses/workflow-concepts-comparison.md) | 定义执行解释器、执行放置粒度、状态真源和恢复模型等诊断轴。 |
| wiki | [Temporal Workflows 文档](../sources/temporal/workflows-docs.md) | Temporal Workflow execution 与 Event History/replay。 |
| wiki | [Temporal Workflow 确定性约束文档](../sources/temporal/workflow-deterministic-constraints-docs.md) | deterministic workflow code 与 replay-safe 行为。 |
| wiki | [Airflow Scheduler 文档](../sources/apache-airflow/scheduler-docs.md) | Airflow scheduler loop、DagRun、TaskInstance 与 metadata DB 推进语义。 |
| wiki | [Microsoft Agent Framework Durable Extension 文档](../sources/microsoft-agent-framework/durable-extension-docs.md) | Durable Task-backed execution、checkpoint 与跨 worker process/host 恢复。 |
| wiki | [Microsoft Agent Framework Durable Workflow Registration 源码](../sources/microsoft-agent-framework/durable-workflow-registration-source.md) | durable graph workflows、activities 和 entities 的注册路径。 |
| wiki | [Microsoft Agent Framework Durable Executor Dispatcher 源码](../sources/microsoft-agent-framework/durable-executor-dispatcher-source.md) | executor 到 activity、entity、sub-orchestration 和 external event 的 dispatch。 |
| wiki | [Durable Task Scheduler 文档](../sources/microsoft-durable-task/scheduler-docs.md) | orchestrator、activity 和 entity work items 的调度边界。 |
| wiki | [LangGraph Persistence 文档](../sources/langgraph/persistence-docs.md) | checkpointer 和 store 的持久化分层。 |
| wiki | [LangGraph Agent Server 文档](../sources/langgraph/agent-server-docs.md) | run-level task queue、queue worker 和 distributed runtime 边界。 |
| wiki | [LangGraph Pregel Executor 源码](../sources/langgraph/pregel-executor-source.md) | OSS compiled graph 的本地线程池和 event loop 执行边界。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| 工作流运行时需要按执行解释器、执行放置粒度、状态真源和恢复模型拆开比较。 | 工作流概念比较；Temporal、Airflow、MAF、Durable Task 与 LangGraph source pages。 | 这些轴是综合分析框架，不是厂商 API 分类。 |
| Temporal 的核心恢复语义是 Event History 驱动的 deterministic replay。 | Temporal Workflows 与确定性约束 source pages。 | Activity 等副作用边界需要另行比较。 |
| Airflow 恢复的是 scheduler/task execution 状态和可调度任务集合，而不是任意程序栈。 | Airflow Scheduler source page；工作流概念比较。 | Executor、database 和部署细节会影响实际故障处理。 |
| MAF Durable Extension 的 durable graph-workflow 路径跨过 per-step work-item placement 边界。 | MAF Durable Extension、registration、dispatcher 与 Durable Task Scheduler source pages。 | 不能外推为 core workflow surface 或 functional workflow surface。 |
| LangGraph OSS、Agent Server 普通模式和 distributed runtime 需要分开描述执行放置粒度。 | LangGraph Agent Server 与 Pregel Executor source pages。 | Platform distributed runtime 的内部实现可能继续演进。 |
