---
schema_version: 2
page_type: concept
title: "工作流执行放置单元"
status: active
created: 2026-06-12
updated: 2026-06-12
summary: "工作流 runtime 对外暴露或内部调度的可执行 work item 粒度。"
maintenance:
  edit_policy: update
validation:
  body_contract: concept
tags:
  - workflow
  - placement
  - knowledge-graph
---

## 定义

工作流执行放置单元是 runtime 选择、排队、dispatch 或放置到 worker process、host
或 machine 上的可执行 work item 粒度。
它回答“调度的是整次 run、TaskInstance、Activity、executor-dispatched work item，
还是 Durable Task activity/entity/sub-orchestration”。

它不是 [工作流控制表示面](workflow-control-representation-surface.md)。
同样写成 graph 的 workflow，可能由本地 graph runner 在同一进程内执行， 也可能被
Durable Task backend 拆成多个 work items。

## 关系

| 关系 | 对象 | 说明 |
| --- | --- | --- |
| `selected-by` | 工作流执行解释器 | 执行解释器决定哪个 work item 可运行；该候选概念目前保留在分析页中，不单独建页。 |
| `may-carry` | [工作流副作用边界](workflow-side-effect-boundary.md) | 放置单元通常承载外部 I/O 或 LLM/tool payload。 |
| `recovered-by` | [工作流恢复模型](workflow-recovery-model.md) | 恢复模型决定失败后哪些放置单元可重新运行。 |
| `implemented-by` | [Apache Airflow](../entities/apache-airflow.md) TaskInstance | Airflow scheduler 选择 TaskInstance 并交给 executor/worker。 |
| `implemented-by` | [Temporal](../entities/temporal.md) Activity | Temporal Activity 是主要分布式副作用 work item。 |
| `implemented-by` | [Microsoft Agent Framework](../entities/microsoft-agent-framework.md) Durable Task work items | Durable Extension 的 graph-workflow 路径映射到 activity/entity/sub-orchestration。 |
| `implemented-by` | [LangGraph](../entities/langgraph.md) run 或 Pregel task | Agent Server 普通模式主要是 run-level；distributed runtime 证据只支持 server/executor 分工。 |

## 使用边界

当问题关注“能否跨进程、host 或 machine 执行”时引用本页。
不要用它回答“workflow 是 DAG 还是 graph”； 那属于控制表示。
也不要把“有 worker”直接理解为“每个图节点都能任意放置到不同 worker”； 必须检查
runtime 暴露的一等放置单元。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| wiki | [工作流概念比较](../analyses/workflow-concepts-comparison.md) | 定义 whole run、TaskInstance、Activity、Durable Task work item 与 Pregel task 的放置差异。 |
| wiki | [Airflow Scheduler 文档](../sources/apache-airflow/scheduler-docs.md) | TaskInstance 选择和 executor/worker dispatch。 |
| wiki | [Temporal Activities 文档](../sources/temporal/activities-docs.md) | Activity 作为可调度副作用 work item。 |
| wiki | [Microsoft Agent Framework Durable Workflow Registration 源码](../sources/microsoft-agent-framework/durable-workflow-registration-source.md) | Durable Extension registration 映射。 |
| wiki | [Microsoft Agent Framework Durable Executor Dispatcher 源码](../sources/microsoft-agent-framework/durable-executor-dispatcher-source.md) | executor dispatch 到 Durable Task activity/entity/sub-orchestration。 |
| wiki | [Durable Task Scheduler 文档](../sources/microsoft-durable-task/scheduler-docs.md) | orchestrator、activity、entity work items。 |
| wiki | [LangGraph Agent Server 文档](../sources/langgraph/agent-server-docs.md) | run-level task queue、queue worker 和 distributed runtime。 |
| wiki | [LangGraph Pregel Executor 源码](../sources/langgraph/pregel-executor-source.md) | OSS runtime 的本地 thread pool/event loop 边界。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| 执行放置单元是 KG-style 概念节点，区别于控制表示和执行解释器。 | 工作流概念比较；各产品 source pages。 | 不同产品对外暴露的放置控制粒度可能随版本演进。 |
| Airflow TaskInstance、Temporal Activity 和 Durable Task work item 可作为不同放置单元模式比较。 | Airflow Scheduler、Temporal Activities、MAF Durable Extension 与 Durable Task source pages。 | 它们的恢复和副作用语义仍不等价。 |
| LangGraph Agent Server 普通模式的 run-level worker 不应被写成图节点级 placement 平台。 | LangGraph Agent Server 和 Pregel source pages。 | distributed runtime 内部实现可能继续变化。 |
