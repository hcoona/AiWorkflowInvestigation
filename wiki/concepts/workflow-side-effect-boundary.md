---
schema_version: 2
page_type: concept
title: "工作流副作用边界"
status: active
created: 2026-06-12
updated: 2026-06-12
summary: "说明外部 I/O、LLM/tool 调用等副作用在不同工作流系统中的受控执行边界。"
maintenance:
  edit_policy: update
validation:
  body_contract: concept
tags:
  - workflow
  - side-effects
  - ai-agents
---

## 定义

工作流副作用边界描述外部 I/O、LLM/tool call、数据库/API 调用或人工交互
应该在哪个 runtime 单元内执行，并如何被 retry、timeout、checkpoint 或幂等化。
它把“控制流”与“图节点、Activity、task、executor 内部的 workload”分开。

这个边界对 AI workflow 尤其重要： LLM/tool 调用很容易被写进任意节点或步骤，
但这并不自动让所在系统具备 agent runtime、durable replay 或任务级副作用隔离。

## 在分析中的用途

[工作流概念比较](../analyses/workflow-concepts-comparison.md)
使用这个概念避免把“能调用 LLM/tool”误判为“运行时语义相同”：

- Temporal 把非确定性 I/O 放在 Activity 等边界内，
  workflow code 保持 deterministic/replay-safe。
- Airflow task/operator 是副作用和重试边界；
  common.ai provider 让 LLM/agent workload 嵌入 task graph。
- Microsoft Agent Framework core executor、step 或 agent 承担节点工作；
  Durable Extension 下普通 executor、agent executor 和 subworkflow
  可映射到 Durable Task activity/entity/sub-orchestration。
- LangGraph 图节点/tool 承担 I/O；
  图节点级 retry、timeout 和 error handler 不自动等价于 Temporal Activity
  的副作用隔离或幂等语义。

## 边界与非等价关系

- “能调用 LLM/tool”不等于“agent runtime”。
- retry 能力不等于幂等保证；
  外部系统副作用仍需要业务层幂等键、补偿或去重策略。
- 图节点级 fault tolerance 不等于 Activity 级 durable side-effect boundary。
- HITL pause/resume 是交互控制语义，
  需要结合副作用重入安全理解。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| wiki | [工作流概念比较](../analyses/workflow-concepts-comparison.md) | 将 LLM/tool call 放在 Activity、task、executor 或图节点 payload 层比较。 |
| wiki | [Temporal Activities 文档](../sources/temporal/activities-docs.md) | Activity 作为 Temporal 外部副作用边界。 |
| wiki | [Airflow DAG 文档](../sources/apache-airflow/dags-docs.md) | Airflow task/operator 与 DAG 控制结构。 |
| wiki | [Airflow Common AI Provider 博客](../sources/apache-airflow/common-ai-provider-blog.md) | Airflow common.ai provider、LLM/agent operators 与工具集。 |
| wiki | [Airflow Agentic Workloads 博客](../sources/apache-airflow/agentic-workloads-blog.md) | LLM/agent workload 嵌入 task graph 的 fan-out/fan-in 示例。 |
| wiki | [Microsoft Agent Framework Durable Executor Dispatcher 源码](../sources/microsoft-agent-framework/durable-executor-dispatcher-source.md) | executor 到 Durable Task activity/entity/sub-orchestration/external-event 路径。 |
| wiki | [LangGraph Fault Tolerance 文档](../sources/langgraph/fault-tolerance-docs.md) | 图节点级 retries、timeouts 和 error handlers。 |
| wiki | [LangGraph Interrupts 文档](../sources/langgraph/interrupts-docs.md) | interrupt/resume 与 HITL 下的重入和副作用安全。 |
| wiki | [StateFlow 论文](../sources/arxiv/stateflow-2403-11322.md) | process control 与 state action 分层。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| LLM/tool 调用通常是工作流节点或动作内部的 payload，而不是控制抽象本身。 | 工作流概念比较；Airflow AI provider、MAF、LangGraph 与 StateFlow source pages。 | 某些 agent framework 会把 agent/tool 建模为一等对象，但仍需区分控制和副作用。 |
| Temporal Activity、Airflow task/operator、MAF executor 和 LangGraph 图节点都是可比较的副作用承载位置，但语义不等价。 | Temporal Activities、Airflow DAG、MAF Durable Executor Dispatcher 与 LangGraph Fault Tolerance source pages。 | 不同 runtime 的 retry、timeout、checkpoint 与幂等要求差异很大。 |
| HITL 和 interrupt/resume 需要与副作用重入安全一起评估。 | LangGraph Interrupts source page；工作流概念比较。 | 本页不提供具体业务幂等设计。 |
