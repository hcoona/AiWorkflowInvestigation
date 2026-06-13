---
schema_version: 2
page_type: concept
title: "工作流控制表示面"
status: active
created: 2026-06-12
updated: 2026-06-12
summary: "工作流中用于表达步骤、依赖、分支、等待和副作用边界的控制结构。"
maintenance:
  edit_policy: update
validation:
  body_contract: concept
tags:
  - workflow
  - control-surface
  - knowledge-graph
---

## 定义

工作流控制表示面是用户或生成器用来表达 workflow 结构的领域概念。
它描述步骤、依赖、分支、循环、等待和副作用边界如何被写成 DAG、general graph、
state machine、functional workflow 或 imperative workflow code。

它不是 runtime 恢复语义。
同一种控制表示面可以由不同 runtime 解释，
并绑定到不同执行放置单元、状态真源和恢复模型。

## 关系

| 关系 | 对象 | 说明 |
| --- | --- | --- |
| `interpreted-by` | 工作流执行解释器 | 控制表示面需要由 scheduler、replay runtime、graph runner 或 agent orchestration runtime 解释；该解释器目前保留在分析页中，不单独建概念页。 |
| `contrasts-with` | [工作流恢复模型](workflow-recovery-model.md) | 表示形态相似不能推出恢复模型相同。 |
| `contrasts-with` | [工作流执行放置单元](workflow-execution-placement-unit.md) | 写成 graph 或 code 不说明 runtime 暴露的调度/放置粒度。 |
| `implemented-by` | [Apache Airflow](../entities/apache-airflow.md) DAG | Airflow DAG 是 scheduler 可解释的无环任务依赖控制表示。 |
| `implemented-by` | [Temporal](../entities/temporal.md) workflow code | Temporal workflow code 是 code-authored control representation。 |
| `implemented-by` | [Microsoft Agent Framework](../entities/microsoft-agent-framework.md) graph/functional surfaces | MAF 同时提供 graph workflow surface 与 functional workflow surface。 |
| `implemented-by` | [LangGraph](../entities/langgraph.md) graph | LangGraph graph 是长期运行 agent/workflow 的 explicit graph/state-machine 表示。 |

## 使用边界

当问题关注“workflow 是如何被写出来或生成出来的”时引用本页。
当问题关注“运行时调度什么、崩溃后如何恢复、外部 I/O 在哪里执行”时，
应引用执行放置单元、恢复模型或副作用边界等更具体概念页。

不要把本页当成 DAG、graph 或 workflow code 的百科条目；
这些变体只有在反复成为独立检索对象时才需要拆出自己的概念页。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| wiki | [工作流概念比较](../analyses/workflow-concepts-comparison.md) | 将 DAG、graph、state machine 和 workflow code 作为 authoring/control representation surface 比较。 |
| wiki | [Airflow DAG 文档](../sources/apache-airflow/dags-docs.md) | Airflow DAG、tasks 和 dependencies。 |
| wiki | [Temporal Workflows 文档](../sources/temporal/workflows-docs.md) | Temporal workflow code 与 Workflow Execution。 |
| wiki | [Microsoft Agent Framework WorkflowBuilder 文档](../sources/microsoft-agent-framework/workflow-builder-docs.md) | MAF graph workflow surface、executors 和 edges。 |
| wiki | [Microsoft Agent Framework Functional Workflows 文档](../sources/microsoft-agent-framework/functional-workflows-docs.md) | MAF functional workflow API。 |
| wiki | [LangGraph Graph API 文档](../sources/langgraph/graph-api-docs.md) | LangGraph State、图节点、Edges 和 super-step。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| 工作流控制表示面是独立于 runtime 恢复语义的概念节点。 | 工作流概念比较；四类产品 source pages。 | 具体系统通常把控制表示与 runtime contract 绑定在一起，需要逐项拆开。 |
| DAG、graph、state machine 和 code-authored workflow 都可作为控制表示变体。 | Airflow、Temporal、MAF 和 LangGraph source pages。 | 这些变体不是运行时等价声明。 |
| 控制表示面相似不能推出执行放置单元或恢复模型相同。 | 工作流概念比较。 | 本页不覆盖所有 workflow DSL 或生成式 workflow 表示。 |
