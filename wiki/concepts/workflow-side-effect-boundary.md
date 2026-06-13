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

工作流副作用边界是 workflow runtime 中专门承载外部 I/O、LLM/tool call、
数据库/API 调用或人工交互的执行单元边界。
它的功能是把 replay-safe 或 scheduler-interpreted 控制流
与不可随意重放的外部副作用分离。

它不是“任何能运行代码的步骤”的同义词。
只有当 runtime、框架或应用约定把 retry、timeout、checkpoint、幂等或补偿责任
明确放在该边界上时，才应把它称为副作用边界。

## 关系

| 关系 | 对象 | 说明 |
| --- | --- | --- |
| `part-of` | [工作流执行放置单元](workflow-execution-placement-unit.md) | 副作用边界通常也是某种可执行或可放置工作单元。 |
| `constrains` | [工作流恢复模型](workflow-recovery-model.md) | 恢复模型需要知道哪些副作用不能被控制流重放直接重复执行。 |
| `implemented-by` | [Temporal](../entities/temporal.md) Activity | Temporal 将非确定性 I/O 放入 Activity 等边界内。 |
| `implemented-by` | [Apache Airflow](../entities/apache-airflow.md) task/operator | Airflow task/operator 是常见副作用和重试边界。 |
| `implemented-by` | [Microsoft Agent Framework](../entities/microsoft-agent-framework.md) executor/agent/subworkflow | Durable Extension 下不同 executor 可映射到 Durable Task activity/entity/sub-orchestration。 |
| `implemented-by` | [LangGraph](../entities/langgraph.md) 图节点/tool | LangGraph 图节点/tool 可承载 I/O，但其 fault tolerance 不自动等价于 Temporal Activity。 |

## 使用边界

引用本页时，问题应关心外部副作用在哪个执行单元内发生、 能否安全
retry、是否要求幂等、以及恢复时会不会重复执行外部 I/O。
如果问题只是在比较系统整体 runtime， 应优先回到
[工作流概念比较](../analyses/workflow-concepts-comparison.md)
中的执行解释器分析，或链接 [工作流恢复模型](workflow-recovery-model.md)。

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
