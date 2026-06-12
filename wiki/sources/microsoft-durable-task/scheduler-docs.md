---
schema_version: 2
page_type: source
title: "Durable Task Scheduler 文档"
status: active
created: 2026-06-12
updated: 2026-06-12
summary: "Microsoft Durable Task Scheduler 官方文档的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - microsoft-durable-task
  - scheduler
  - durable-execution
---

## 来源边界

本页只投影 Durable Task Scheduler 文档。
它用于说明 Durable Task Scheduler 作为独立后端如何 dispatch orchestrator、
activity 与 entity work items，并管理 durable state。
原始材料未保存到 `raw/`；本页直接引用外部 URL 作为主证据。

## 可复用关键主张

- Durable Task Scheduler 是 Durable Functions 与 Durable Task SDKs
  的推荐存储和调度后端。
- scheduler backend dispatches orchestrator、activity 和 entity work items。
- 应用通过 gRPC 连接 scheduler；work items 由 scheduler push 到 app，
  app 可以并行处理多个 work items 并回传结果。
- scheduler 与 app 可独立伸缩，并在 scheduler 内部管理 orchestrations/entities
  state。

## 限制与冲突

- Durable Task Scheduler 是底层后端；具体上层框架如何映射 workflow step
  需要结合对应集成代码。
- 本页不证明 Microsoft Agent Framework core workflow 在不使用 Durable Extension
  时具备同等语义。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://learn.microsoft.com/en-us/azure/azure-functions/durable/durable-task-scheduler/durable-task-scheduler` | Durable Task Scheduler 官方文档；访问时间 2026-06-12。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| Durable Task Scheduler dispatches orchestrator、activity 和 entity work items。 | 上方证据单元。 | 上层框架的 step 映射需另有证据。 |
| connected apps 可以并行处理多个 work items，并将结果返回 scheduler。 | 上方证据单元。 | 具体并行度和放置由宿主、worker 和配置决定。 |
