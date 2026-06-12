---
schema_version: 2
page_type: entity
title: "Apache Airflow"
status: active
created: 2026-06-12
updated: 2026-06-12
summary: "Apache Airflow 在本 wiki 中作为 scheduler-managed DAG/task graph 工作流平台实体。"
maintenance:
  edit_policy: update
validation:
  body_contract: entity
tags:
  - workflow
  - airflow
  - orchestration
---

## 身份

Apache Airflow 是本 wiki 用于比较 explicit DAG/task graph、 scheduler-managed
task execution 和 metadata DB 状态推进的核心平台实体。
在当前证据边界内，Airflow 的关键身份是： DAG 是 scheduler
可解释的无环任务依赖控制表示， DagRun、TaskInstance、retry、mapped task state
等运行状态由 metadata DB 和 scheduler loop 推进。

本页聚焦 Airflow 的 DAG/scheduler/task graph 语义。
Executor 选型、集群部署和 provider 生态细节只在影响当前分析时提及。

## 关系与时间线

| 关系 | 当前 wiki 判断 |
| --- | --- |
| 控制表示面 | Airflow DAG 是 explicit DAG/task graph control representation surface。 |
| 执行与恢复语义 | Scheduler 根据 serialized DAG、metadata DB 和依赖约束选择 TaskInstance。 |
| 副作用边界 | task/operator/decorator 是副作用、重试和观测边界。 |
| 动态拓扑 | Dynamic Task Mapping 由 scheduler 管理运行时任务展开。 |
| 时间与触发语义 | timetable/schedule 和 asset trigger 创建或触发 DagRun；scheduler 再推进 run 内 TaskInstance。 |
| AI workload | common.ai provider 和 agentic workloads 将 LLM/agent payload 嵌入 task graph，而不是改变 Airflow 的核心 scheduler 语义。 |

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| wiki | [工作流概念比较](../analyses/workflow-concepts-comparison.md) | 将 Airflow 映射为 scheduler-managed DAG/task graph 平台。 |
| wiki | [Airflow DAG 文档](../sources/apache-airflow/dags-docs.md) | DAG、tasks、dependencies 和 scheduling 的核心语义。 |
| wiki | [Airflow Scheduler 文档](../sources/apache-airflow/scheduler-docs.md) | scheduler loop、DagRun、TaskInstance 和 metadata DB 推进语义。 |
| wiki | [Airflow Dynamic Task Mapping 文档](../sources/apache-airflow/dynamic-task-mapping-docs.md) | 运行时动态展开 task 的语义。 |
| wiki | [Airflow Asset Scheduling 文档](../sources/apache-airflow/asset-scheduling-docs.md) | asset update 触发 DAG 的调度语义。 |
| wiki | [Airflow Common AI Provider 博客](../sources/apache-airflow/common-ai-provider-blog.md) | common.ai provider、LLM/agent operators 与工具集。 |
| wiki | [Airflow Agentic Workloads 博客](../sources/apache-airflow/agentic-workloads-blog.md) | Dynamic Task Mapping + common.ai 的 fan-out/fan-in agentic pipeline。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| Airflow 在当前比较中代表 scheduler-managed DAG/task graph 工作流平台。 | 工作流概念比较；Airflow DAG 与 Scheduler source pages。 | 不覆盖所有 executor、deployment 和 provider 组合。 |
| Airflow 恢复和推进的是 DagRun/TaskInstance 等 scheduler/task execution 状态。 | Airflow Scheduler source page；工作流概念比较。 | 实际故障恢复受 metadata DB、executor 和部署配置影响。 |
| Airflow 的 AI/agent 能力是 task/operator 层 payload 与 provider 扩展，不应被直接写成核心 agent runtime。 | Airflow Common AI Provider、Agentic Workloads source pages；工作流概念比较。 | provider 和示例快速演进，需按版本复核。 |
