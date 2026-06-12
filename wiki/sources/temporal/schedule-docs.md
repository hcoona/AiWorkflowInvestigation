---
schema_version: 2
page_type: source
title: "Temporal Schedule 文档"
status: active
created: 2026-06-12
updated: 2026-06-12
summary: "Temporal Schedule 官方文档的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - temporal
  - schedule
  - workflow
---

## 来源边界

本页只投影 Temporal 的 `https://docs.temporal.io/schedule` 文档。
它用于界定 Schedule 作为启动 Workflow Execution 的独立时间规则，而不是 Workflow
Execution 内部的 Timer。
原始材料未保存到 `raw/`；本页直接引用外部 URL 作为主证据。

## 可复用关键主张

- Schedule 包含在特定时间启动 Workflow Execution 的指令。
- Schedule 有自己的 identity，并且独立于 Workflow Execution；这不同于把 cron
  schedule 作为 Workflow Execution 属性的 Temporal Cron Job。
- Schedule 的 Action 定义要启动的 Workflow Execution 属性；Spec 定义何时触发
  Action，可使用 interval 或 calendar expression。
- Schedule 支持 pause、backfill、action count limit，以及 overlap、catchup
  window、pause-on-failure 等策略。

## 限制与冲突

- Schedule 是外部启动规则，不是 Workflow Execution 内部的控制流等待。
- 对一次性未来启动，文档建议使用 Start Delay 而不是 Schedule。
- Schedule 能补足 Temporal 的时间触发能力，但不能把 Temporal 简化成 Airflow 式
  DAG scheduler；它启动的是 Workflow Execution，而不是调度 DAG 内 task graph。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://docs.temporal.io/schedule` | Temporal Schedule 官方文档；访问时间 2026-06-12。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| Temporal Schedule 是独立于 Workflow Execution 的时间触发对象，用于在特定时间启动 Workflow Execution。 | 上方证据单元。 | 它不描述 Workflow Execution 内部如何等待或恢复。 |
| Schedule 支持 interval/calendar spec 与 overlap/catchup 等运行策略。 | 上方证据单元。 | 调度策略作用于 Schedule Action 和 Workflow Execution 启动，不是 DAG task scheduling。 |
| Temporal 同时具备外部 Schedule 和内部 Timer，但二者处在不同抽象层。 | 上方证据单元和 [Temporal Timers and Start Delays 文档](timers-delays-docs.md)。 | 这是跨 source page 的综合判断。 |
