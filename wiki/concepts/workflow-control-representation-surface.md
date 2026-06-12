---
schema_version: 2
page_type: concept
title: "工作流控制表示面"
status: active
created: 2026-06-12
updated: 2026-06-12
summary: "区分 DAG、graph、state machine 与 code-authored workflow 等工作流表达形态。"
maintenance:
  edit_policy: update
validation:
  body_contract: concept
tags:
  - workflow
  - orchestration
  - control-surface
---

## 定义

工作流控制表示面描述用户如何表达一个长期、多步、可恢复或可调度的工作： 例如
DAG、general graph、state machine、functional workflow 或 imperative workflow
code。
它回答的是“workflow 怎么写出来”，不是“runtime 如何调度、持久化或恢复”。

因此，两个系统的控制表示面相似，只能说明它们在 authoring 层可类比。
运行时解释器、状态真源、恢复模型和副作用边界仍需单独比较。

## 在分析中的用途

[工作流概念比较](../analyses/workflow-concepts-comparison.md)
使用这个概念避免把产品术语直接相互等价： Airflow DAG、Microsoft Agent Framework
graph workflow 和 LangGraph graph 都属于 graph-shaped 表示形态，
但三者的调度器、checkpoint、worker placement 和恢复语义不同。
Temporal workflow code 和 Microsoft Agent Framework functional workflow 都属于
code-authored 表示形态， 但只有与 deterministic replay、Durable Task hosting
或其他 runtime contract 结合时才形成具体恢复语义。

## 边界与非等价关系

- DAG 是 graph 的受限子类，但 Airflow DAG 还携带 DagRun、TaskInstance
  和 scheduler 解释语义，不能外推为所有 graph workflow。
- graph workflow 与 functional workflow 是 authoring surface 维度，
  不是互斥产品类型。
- LLM/tool call 通常是表示面内部某个 task、activity、executor 或图节点的
  payload， 不是控制表示面本身。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| wiki | [工作流概念比较](../analyses/workflow-concepts-comparison.md) | 将 DAG、graph、state machine 与 workflow code 放入多轴诊断矩阵。 |
| wiki | [Temporal Workflows 文档](../sources/temporal/workflows-docs.md) | Temporal workflow code 作为控制程序，并由 Event History replay 解释。 |
| wiki | [Airflow DAG 文档](../sources/apache-airflow/dags-docs.md) | Airflow DAG 作为任务依赖与调度控制表示。 |
| wiki | [Microsoft Agent Framework WorkflowBuilder 文档](../sources/microsoft-agent-framework/workflow-builder-docs.md) | MAF graph workflow surface 的 executor 和 edge 表达。 |
| wiki | [Microsoft Agent Framework Functional Workflows 文档](../sources/microsoft-agent-framework/functional-workflows-docs.md) | MAF functional workflow surface 的 `@workflow` / `@step` 表达。 |
| wiki | [LangGraph Graph API 文档](../sources/langgraph/graph-api-docs.md) | LangGraph State、图节点、Edges、message passing 与 super-step 表达。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| DAG、graph、state machine 和 workflow code 都可以作为 workflow 的控制表示面。 | 工作流概念比较；Temporal、Airflow、MAF 与 LangGraph source pages。 | 这是跨来源综合判断，不是单一厂商文档原话。 |
| 控制表示面相似不能推出运行时语义等价。 | 工作流概念比较；Temporal replay、Airflow scheduler、MAF workflow surfaces 与 LangGraph Graph API source pages。 | 具体产品版本和 deployment mode 仍需逐项取证。 |
| graph workflow 与 functional workflow 是 authoring surface 维度，不是互斥产品类型。 | MAF WorkflowBuilder 与 Functional Workflows source pages；工作流概念比较。 | 本页不判断任一 surface 的成熟度或 GA 状态。 |
