---
schema_version: 2
page_type: source
title: "Temporal Timers and Start Delays 文档"
status: active
created: 2026-06-12
updated: 2026-06-12
summary: "Temporal Timer 与 Start Delay 官方文档的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - temporal
  - timers
  - durable-execution
---

## 来源边界

本页只投影 Temporal 的
`https://docs.temporal.io/workflow-execution/timers-delays` 文档。
它用于界定 Workflow Execution 内部的 Timer 语义，以及一次性延迟启动的 Start
Delay 语义。
原始材料未保存到 `raw/`；本页直接引用外部 URL 作为主证据。

## 可复用关键主张

- Temporal SDK 提供 Timer API，使 Workflow Execution 以确定性方式处理时间值。
- Timer 会被持久化；即使 Worker 或 Temporal Service
  在计时完成时不可用，恢复后等待 Timer 的 Workflow 代码仍会继续执行。
- Worker 等待 Timer 时不额外消耗资源，文档称单个 Worker 可并发等待大量 Timer。
- Start Delay 用于在 Workflow 创建后延迟首次 Workflow Task
  调度，适合一次性未来启动； 它与 Schedules 和 Cron Jobs 不兼容。

## 限制与冲突

- Timer 是 Workflow Execution 内部的持久等待机制，不等同于外部周期性调度器。
- Start Delay 适合一次性未来启动；周期性或日历式启动应结合 Schedule 文档理解。
- Timer 文档建议不要依赖亚秒级精度，应把持续时间理解为最小等待时间。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://docs.temporal.io/workflow-execution/timers-delays` | Temporal Timers and Start Delays 官方文档；访问时间 2026-06-12。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| Temporal Timer 是 Workflow Execution 内部的 deterministic、persisted wait primitive。 | 上方证据单元。 | 具体 SDK API 名称会随语言不同而变化。 |
| Start Delay 是一次性未来启动机制，通过延迟首次 Workflow Task 调度实现。 | 上方证据单元。 | 与 Schedule/Cron Job 不兼容，不能当作周期调度抽象。 |
| Temporal 的时间等待语义属于 durable workflow control，而不是 Airflow 式 schedule-first DAG 语义。 | 上方证据单元。 | 需要结合 Schedule source page 区分外部启动规则。 |
