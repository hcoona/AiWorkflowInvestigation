---
schema_version: 2
page_type: entity
title: "LangGraph"
status: active
created: 2026-06-12
updated: 2026-06-12
summary: "LangGraph 在本 wiki 中作为 checkpointed stateful graph runtime 与 Agent Server 运行边界实体。"
maintenance:
  edit_policy: update
validation:
  body_contract: entity
tags:
  - workflow
  - langgraph
  - ai-agents
---

## 身份

LangGraph 是本 wiki 用于比较 stateful agent graph、checkpointed graph state、
interrupt/resume 和 graph execution placement 的核心实体。
在当前证据边界内，LangGraph Graph API 由 State、图节点和 Edges 组织；
checkpointer 负责 thread-scoped graph state， store 负责跨 thread memory。

LangGraph 需要按 runtime mode 区分： OSS compiled graph 是同进程 graph runtime；
Agent Server 普通模式主要提供 run-level queue worker； distributed runtime 支持
orchestration/execution process 分离， 但当前一手证据不足以把它写成公开图节点级
worker placement 平台。

## 关系与时间线

| 关系 | 当前 wiki 判断 |
| --- | --- |
| 控制表示面 | explicit general graph/state machine，用于长期运行 agent/workflow 控制表示。 |
| 执行与恢复语义 | OSS graph 依赖 checkpointer/thread state；Agent Server run 可从 checkpoint 恢复。 |
| 副作用边界 | 图节点/tool 承担 I/O；图节点级 retries、timeouts 和 error handlers 是 fault-tolerance 能力。 |
| HITL | interrupt/resume 提供图/图节点级暂停恢复语义。 |
| Agent Server | 普通模式支持 run-level task queue 和 queue worker；distributed runtime 拆分 orchestration/execution process。 |
| 与 Airflow/Temporal 的边界 | graph-shaped surface 不等于 Airflow DAG；checkpoint resume 不等于 Temporal Event History replay。 |

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| wiki | [工作流概念比较](../analyses/workflow-concepts-comparison.md) | 将 LangGraph 映射为 checkpointed stateful graph runtime，并区分 OSS、Agent Server 与 distributed runtime。 |
| wiki | [LangGraph Overview 文档](../sources/langgraph/overview-docs.md) | LangGraph 的 low-level orchestration framework/runtime 定位。 |
| wiki | [LangGraph Graph API 文档](../sources/langgraph/graph-api-docs.md) | State、图节点、Edges、message passing 与 super-step。 |
| wiki | [LangGraph Persistence 文档](../sources/langgraph/persistence-docs.md) | checkpointer 与 store 的持久化分层。 |
| wiki | [LangGraph Interrupts 文档](../sources/langgraph/interrupts-docs.md) | interrupt/resume/HITL 的暂停与恢复语义。 |
| wiki | [LangGraph Fault Tolerance 文档](../sources/langgraph/fault-tolerance-docs.md) | 图节点级 retries、timeouts 和 error handlers。 |
| wiki | [LangGraph Agent Server 文档](../sources/langgraph/agent-server-docs.md) | run-level task queue、queue workers 和 distributed runtime 边界。 |
| wiki | [LangGraph Pregel Executor 源码](../sources/langgraph/pregel-executor-source.md) | OSS Pregel sync/async execution 的 thread pool 与 event loop 边界。 |
| wiki | [LangGraph Pregel Retry 源码](../sources/langgraph/pregel-retry-source.md) | Pregel task 的 `invoke`/`ainvoke` 路径和 Platform distributed runtime 的 server/executor 分工。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| LangGraph 在当前比较中代表 checkpointed stateful graph runtime。 | 工作流概念比较；Overview、Graph API 和 Persistence source pages。 | durability 依赖 checkpointer 等配置，不是无条件默认。 |
| LangGraph interrupt/resume 和 fault tolerance 是图/图节点级语义，不等于 Airflow scheduler 或 Temporal Activity 语义。 | Interrupts、Fault Tolerance source pages；工作流概念比较。 | 外部副作用的幂等和重入仍需应用设计。 |
| LangGraph Agent Server 普通模式是 run-level platformization；distributed runtime 不能被当前证据写成公开图节点级 worker placement 平台。 | Agent Server、Pregel Executor、Pregel Retry source pages。 | Platform distributed runtime 的内部实现可能继续演进。 |
