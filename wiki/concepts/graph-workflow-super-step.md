---
schema_version: 2
page_type: concept
title: "图工作流 Super-step"
status: active
created: 2026-06-13
updated: 2026-06-13
summary: "图工作流 runtime 以轮次推进可运行图节点或 executor 的执行阶段。"
maintenance:
  edit_policy: update
validation:
  body_contract: concept
tags:
  - workflow
  - graph-workflow
  - knowledge-graph
---

## 定义

图工作流 Super-step 是 graph workflow runtime 推进执行的一轮同步阶段： runtime
在一轮中让当前可运行的图节点或 executor 执行，收集消息或 state updates，
再决定下一轮可运行的图节点集合。

它不是图节点、不是 Airflow `TaskInstance`，也不是 Temporal `Activity`。
Super-step 描述 graph execution algorithm 的推进边界；
它本身不说明图节点是否会被放置到不同 worker process、host 或 machine。
这个名词值得单独成页，是因为 LangGraph 与 Microsoft Agent Framework 都使用
super-step/superstep 语言描述 graph workflow execution， 而它很容易被误读成
step、node 或 distributed work item。

## 关系

| 关系 | 对象 | 说明 |
| --- | --- | --- |
| `specializes` | [工作流控制表示面](workflow-control-representation-surface.md) | Super-step 只适用于 graph workflow surface 的执行推进，不适用于所有 workflow 表达。 |
| `contrasts-with` | [工作流执行放置单元](workflow-execution-placement-unit.md) | Super-step 是执行轮次，不是 runtime 暴露的一等调度或放置 work item。 |
| `constrained-by` | [工作流恢复模型](workflow-recovery-model.md) | 如果 runtime 支持 checkpoint 或 durable backend，恢复模型决定 super-step 前后哪些状态可恢复。 |
| `implemented-by` | [LangGraph](../entities/langgraph.md) Graph API | LangGraph 文档把底层 graph algorithm 写成 message passing 和 super-step 推进。 |
| `implemented-by` | [Microsoft Agent Framework](../entities/microsoft-agent-framework.md) WorkflowBuilder | MAF WorkflowBuilder 文档使用 superstep execution 描述 graph workflow 运行。 |
| `implemented-by` | [Microsoft Agent Framework](../entities/microsoft-agent-framework.md) Durable Extension dispatcher | durable graph-workflow 路径中，每个 superstep 的 dispatch phase 可调用 Durable Task activity、entity、sub-orchestration 或 external event。 |

## 使用边界

当问题关注 graph workflow 如何按轮次推进、为什么 graph workflow surface 不等于
DAG scheduler 或 deterministic replay 时引用本页。
如果问题关注“能否跨进程、host 或 machine 放置执行”，应引用
[工作流执行放置单元](workflow-execution-placement-unit.md)；
如果问题关注单个产品的 API 名称或源码细节，应留在对应 entity/source page。

不要因为系统包含 graph、node 或 step 就默认套用本页。
当前证据只支持在 LangGraph Graph API 与 Microsoft Agent Framework graph workflow
语境中使用它；不能外推到 Airflow DAG、Temporal workflow code， 或 MAF functional
workflow surface。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| wiki | [工作流概念比较](../analyses/workflow-concepts-comparison.md) | 将 LangGraph 与 MAF graph workflow 的 super-step/superstep 推进放在执行解释器和放置粒度边界中比较。 |
| wiki | [LangGraph Graph API 文档](../sources/langgraph/graph-api-docs.md) | LangGraph Graph API 使用 message passing 和 super-step 推进 graph execution。 |
| wiki | [Microsoft Agent Framework WorkflowBuilder 文档](../sources/microsoft-agent-framework/workflow-builder-docs.md) | MAF WorkflowBuilder 文档以 executors、edges 与 superstep execution 描述 graph workflow。 |
| wiki | [Microsoft Agent Framework Durable Executor Dispatcher 源码](../sources/microsoft-agent-framework/durable-executor-dispatcher-source.md) | Durable Extension 在 graph workflow 的每个 superstep dispatch phase 中分派 executor。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| 图工作流 Super-step 是可复用领域概念，能跨 LangGraph 与 MAF graph workflow 语境解释 graph execution 的轮次推进。 | LangGraph Graph API、MAF WorkflowBuilder 和工作流概念比较。 | 当前证据不支持将它外推为所有 graph/workflow 系统的通用标准术语。 |
| Super-step 不等于图节点、step、TaskInstance、Activity 或 Durable Task work item。 | 工作流概念比较；MAF Durable Executor Dispatcher source page。 | MAF Durable Extension 可在 superstep dispatch phase 调用 Durable Task API，但那是 durable graph-workflow 路径的实现细节。 |
| 看到 super-step/superstep 不能直接推出图节点级跨 host/machine 放置。 | 工作流执行放置单元；LangGraph 与 MAF source pages。 | 具体部署能力仍需按 runtime mode、Durable Extension 配置和后端复核。 |
