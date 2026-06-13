---
schema_version: 2
page_type: concept
title: "工作流时间与触发语义"
status: active
created: 2026-06-12
updated: 2026-06-12
summary: "工作流系统中创建 run、内部等待、资产触发和人工恢复的时间相关触发概念。"
maintenance:
  edit_policy: update
validation:
  body_contract: concept
tags:
  - workflow
  - scheduling
  - knowledge-graph
---

## 定义

工作流时间与触发语义是 workflow runtime 或 scheduler 中与时间、事件、资产更新、
人工输入或延迟等待有关的触发概念。
它描述某个运行实例何时被创建、何时继续等待中的控制流， 或何时重新进入暂停的
graph/agent workflow。

它不是单一调度器能力。
外部 Schedule、内部 Timer、asset trigger、start delay 和 interrupt/resume
处在不同 runtime 层级。

## 关系

| 关系 | 对象 | 说明 |
| --- | --- | --- |
| `creates` | workflow/DAG run | 外部 schedule 或 asset trigger 通常创建或触发新的 run。 |
| `resumes` | [工作流恢复模型](workflow-recovery-model.md) | Timer、external event 或 HITL input 可能让等待中的控制流继续。 |
| `implemented-by` | [Temporal](../entities/temporal.md) Timer | Temporal Timer 是 Workflow Execution 内部持久等待。 |
| `implemented-by` | [Temporal](../entities/temporal.md) Schedule | Temporal Schedule 是外部启动 Workflow Execution 的规则。 |
| `implemented-by` | [Apache Airflow](../entities/apache-airflow.md) timetable/schedule/asset trigger | Airflow 时间表和资产更新影响 DagRun 创建或触发。 |
| `implemented-by` | [LangGraph](../entities/langgraph.md) interrupt/resume | LangGraph interrupt/resume 是图/图节点级暂停恢复语义。 |
| `implemented-by` | [Microsoft Agent Framework](../entities/microsoft-agent-framework.md) HITL/external event | Durable Extension 可通过 checkpoint/resume 和 external event 承载等待。 |

## 使用边界

当问题关注“run 何时创建、等待何时恢复、人工输入如何触发继续”时引用本页。
如果问题关注的是 scheduler 如何选择可运行 task， 应引用
[工作流执行放置单元](workflow-execution-placement-unit.md) 或产品实体页中的
scheduler/runtime 关系。

不要把 Timer、Schedule、asset trigger 和 interrupt/resume 写成同义词。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| wiki | [工作流概念比较](../analyses/workflow-concepts-comparison.md) | 区分 Timer、Schedule、asset trigger、interrupt/resume 和 HITL。 |
| wiki | [Temporal Timers and Start Delays 文档](../sources/temporal/timers-delays-docs.md) | Timer 和 Start Delay 的时间语义。 |
| wiki | [Temporal Schedule 文档](../sources/temporal/schedule-docs.md) | Schedule 作为外部启动规则。 |
| wiki | [Airflow Scheduler 文档](../sources/apache-airflow/scheduler-docs.md) | DagRun 创建和 TaskInstance 推进。 |
| wiki | [Airflow Asset Scheduling 文档](../sources/apache-airflow/asset-scheduling-docs.md) | asset update 触发 DAG。 |
| wiki | [LangGraph Interrupts 文档](../sources/langgraph/interrupts-docs.md) | graph/图节点级暂停恢复。 |
| wiki | [Microsoft Agent Framework Durable Extension 文档](../sources/microsoft-agent-framework/durable-extension-docs.md) | HITL、checkpoint 和 resume 能力。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| 工作流时间与触发语义是独立概念节点，覆盖 run creation、内部等待和交互恢复等关系。 | 工作流概念比较；Temporal、Airflow、LangGraph 和 MAF source pages。 | 不同产品的术语可能使用 schedule、timer、trigger、event 等不同名称。 |
| Timer、Schedule、asset trigger 和 interrupt/resume 不应直接等价。 | Temporal Timer/Schedule、Airflow Asset Scheduling、LangGraph Interrupts source pages。 | 某些实现可能在底层共享队列或 timer infrastructure，但语义层级不同。 |
| run creation 与 run 内 task scheduling 是不同层级。 | Airflow Scheduler source page；工作流概念比较。 | 具体调度策略需要产品级配置证据。 |
