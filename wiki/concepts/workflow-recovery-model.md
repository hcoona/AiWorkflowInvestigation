---
schema_version: 2
page_type: concept
title: "工作流恢复模型"
status: active
created: 2026-06-12
updated: 2026-06-12
summary: "工作流 runtime 在故障后利用状态真源重建控制位置和可运行工作的方式。"
maintenance:
  edit_policy: update
validation:
  body_contract: concept
tags:
  - workflow
  - recovery
  - knowledge-graph
---

## 定义

工作流恢复模型是 runtime 在崩溃、重启或 worker 替换后，
利用工作流状态真源重建控制位置、可运行 work set 或 replay-safe 局部状态的方式。

它不是“有 checkpoint”或“有 retry”的同义词。
恢复模型必须说明恢复的是什么： 任务集合、程序控制点、graph thread state、durable
orchestration state， 还是某种 work-item dispatch 状态。

## 关系

| 关系 | 对象 | 说明 |
| --- | --- | --- |
| `uses` | 工作流状态真源 | 恢复模型依赖 runtime 可信的持久状态；该候选概念目前保留在分析页中，不单独建页。 |
| `implemented-by` | [Temporal](../entities/temporal.md) deterministic replay | Temporal replay 重建 replay-safe 局部状态并生成或校验命令。 |
| `implemented-by` | [Apache Airflow](../entities/apache-airflow.md) scheduler recovery | Airflow 恢复 task graph instance state 和可调度 task set。 |
| `implemented-by` | [LangGraph](../entities/langgraph.md) checkpoint resume | LangGraph 可从 checkpoint/thread state 恢复 graph execution。 |
| `implemented-by` | [Microsoft Agent Framework](../entities/microsoft-agent-framework.md) Durable Extension recovery | Durable Task infrastructure 可 checkpoint/recover graph-based workflows。 |
| `constrained-by` | [工作流副作用边界](workflow-side-effect-boundary.md) | 恢复时必须避免错误重复外部副作用。 |

## 使用边界

当问题关注“故障后恢复的是哪种当前位置”时引用本页。
不要用本页替代状态真源： Event History、metadata DB 或 checkpoint 是恢复输入，
不是恢复算法本身。
也不要把 retry policy 直接等同于恢复模型。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| wiki | [工作流概念比较](../analyses/workflow-concepts-comparison.md) | 将可运行任务集合、program replay、graph thread state 和 durable orchestration state 放入恢复模型轴。 |
| wiki | [Temporal Workflows 文档](../sources/temporal/workflows-docs.md) | Workflow replay 和 Event History。 |
| wiki | [Temporal Workflow 确定性约束文档](../sources/temporal/workflow-deterministic-constraints-docs.md) | deterministic/replay-safe 约束。 |
| wiki | [Airflow Scheduler 文档](../sources/apache-airflow/scheduler-docs.md) | scheduler loop、DagRun 和 TaskInstance state 推进。 |
| wiki | [LangGraph Persistence 文档](../sources/langgraph/persistence-docs.md) | checkpointer/thread state。 |
| wiki | [LangGraph Interrupts 文档](../sources/langgraph/interrupts-docs.md) | interrupt/resume 和 HITL 恢复语义。 |
| wiki | [Microsoft Agent Framework Durable Extension 文档](../sources/microsoft-agent-framework/durable-extension-docs.md) | Durable Task-backed checkpoint/recover。 |
| wiki | [Microsoft Agent Framework Durable Executor Dispatcher 源码](../sources/microsoft-agent-framework/durable-executor-dispatcher-source.md) | Durable Extension 下 work item dispatch 与恢复相关边界。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| 工作流恢复模型是独立 KG-style 概念节点，区别于状态真源和 retry policy。 | 工作流概念比较；各 runtime source pages。 | 本页不覆盖业务补偿事务或数据一致性策略。 |
| Temporal replay、Airflow scheduler recovery、LangGraph checkpoint resume 和 MAF Durable Extension recovery 是不同恢复模型。 | 对应 source pages。 | 实际恢复行为受部署、配置和版本影响。 |
| 副作用边界会约束恢复模型是否能安全重放或重试。 | 工作流副作用边界；Temporal Activities、LangGraph Interrupts 和 MAF Durable source pages。 | 幂等性最终仍需要业务语义支撑。 |
