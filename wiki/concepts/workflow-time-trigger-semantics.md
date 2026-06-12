---
schema_version: 2
page_type: concept
title: "工作流时间与触发语义"
status: active
created: 2026-06-12
updated: 2026-06-12
summary: "区分工作流启动触发、内部持久等待、资产触发和人工暂停恢复等时间相关语义。"
maintenance:
  edit_policy: update
validation:
  body_contract: concept
tags:
  - workflow
  - scheduling
  - time
---

## 定义

工作流时间与触发语义描述时间、触发、等待和暂停恢复属于哪一层： 是创建一次 run
的外部 schedule， 是 workflow execution 内部的持久 timer， 是 scheduler 对 task
graph 的推进， 是 asset update 触发， 还是 graph/图节点级 interrupt/resume。

这个概念用于避免把所有“定时、等待、触发、暂停”混成同一种调度能力。

## 在分析中的用途

[工作流概念比较](../analyses/workflow-concepts-comparison.md) 使用这个概念区分
Airflow 和 Temporal 的常见混淆： Airflow timetable、schedule 和 asset trigger
主要影响 DagRun 创建或触发； Temporal Schedule 是独立于 Workflow Execution
的启动规则； Temporal Timer 是 Workflow Execution 内部的持久等待。
LangGraph interrupt/resume 和 Microsoft Agent Framework HITL
则更接近交互暂停/恢复语义， 不能直接写成 Airflow scheduler 或 Temporal Timer
的等价物。

## 边界与非等价关系

- Timer 不等于 Schedule：
  一个通常是 execution 内部持久等待，另一个通常是外部启动规则。
- run creation 不等于 task scheduling：
  创建一次 workflow/DAG run 与推进 run 内部的 task set 是不同层级。
- interrupt/resume 不等于时间调度；
  它可以与等待有关，但核心是暂停控制流并接收外部输入。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| wiki | [工作流概念比较](../analyses/workflow-concepts-comparison.md) | 将 Timer、Schedule、asset trigger、interrupt/resume 和 HITL 放在时间/调度轴比较。 |
| wiki | [Temporal Timers and Start Delays 文档](../sources/temporal/timers-delays-docs.md) | Temporal Timer 的持久等待语义与 Start Delay 的一次性延迟启动语义。 |
| wiki | [Temporal Schedule 文档](../sources/temporal/schedule-docs.md) | Temporal Schedule 作为外部启动 Workflow Execution 的规则。 |
| wiki | [Airflow Scheduler 文档](../sources/apache-airflow/scheduler-docs.md) | Airflow scheduler loop、DagRun 创建和 TaskInstance 推进语义。 |
| wiki | [Airflow Asset Scheduling 文档](../sources/apache-airflow/asset-scheduling-docs.md) | asset update 触发 DAG 的调度语义。 |
| wiki | [LangGraph Interrupts 文档](../sources/langgraph/interrupts-docs.md) | graph/图节点级暂停与恢复语义。 |
| wiki | [Microsoft Agent Framework Durable Extension 文档](../sources/microsoft-agent-framework/durable-extension-docs.md) | Durable Extension 的 HITL、checkpoint 和 resume 能力。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| 工作流系统中的时间语义至少要区分外部启动规则、execution 内部等待和 scheduler 对任务集合的推进。 | 工作流概念比较；Temporal Timer/Schedule 与 Airflow Scheduler source pages。 | 不同产品的术语和 API 可能继续演进。 |
| Temporal Timer 与 Temporal Schedule 不是同一层语义。 | Temporal Timers and Start Delays 与 Schedule source pages。 | Start Delay 等一次性启动延迟也需与周期性 schedule 区分。 |
| interrupt/resume 和 HITL 不应直接等同于时间调度器。 | LangGraph Interrupts、MAF Durable Extension 与工作流概念比较。 | 具体实现可能使用 timer、external event 或 checkpoint 机制承载等待。 |
