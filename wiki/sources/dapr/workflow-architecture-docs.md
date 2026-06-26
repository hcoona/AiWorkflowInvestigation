---
schema_version: 2
page_type: source
title: "Dapr Workflow Architecture 文档"
status: active
created: 2026-06-26
updated: 2026-06-26
summary: "Dapr Workflow sidecar、actor、state store、reminder 和 scaling 架构的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - dapr
  - workflow
  - actors
  - state-store
---

## 来源边界

本页只投影 Dapr 官方 Workflow architecture 文档。
它用于界定 Dapr Workflow 如何在 Dapr sidecar 中运行、如何通过 SDK worker
与 sidecar 通信、如何依赖 Dapr Actors、actor state store、reminders、
placement 和 app replica scaling。
原始材料未保存到 `raw/`；本页直接引用外部 URL 作为主证据。

## 可复用关键主张

- Dapr Workflow engine 运行在 `daprd` sidecar 内部；
  应用通过 workflow SDK worker 与 sidecar 通信。
- Dapr Workflow 建立在 Dapr Actors 和 Durable Task 风格的 work item 协议之上。
- Workflow state 保存在 actor state store 中，包含 inbox、history、
  custom status 和 metadata 等记录。
- Actor reminders/timers 是 workflow wake-up 与 crash recovery 的关键机制。
- Workflow/activity execution 可跨同一 app ID 的 replicas 分布；
  但所有 replicas 必须注册相同 workflows 和 activities。
- Workflow state 在完成后仍会保留，需用 retention/purge 策略控制存储增长。

## 限制与冲突

- 本来源使 Dapr Workflow 的运维依赖成为候选评估的一部分：
  sidecar、actors、placement、scheduler/reminders 和 actor state store
  不是可忽略的实现细节。
- 本来源不证明 Dapr 提供与 Temporal Task Queue、Visibility 或 Web UI
  等价的 routing/visibility 能力。
- 支持的 state store、payload、concurrency 和 replica registration
  约束会随 Dapr 版本与部署方式变化；目标 POC 必须按实际 release 复核。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://docs.dapr.io/developing-applications/building-blocks/workflow/workflow-architecture/` | Dapr Workflow architecture 官方文档；访问时间 2026-06-26。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| Dapr Workflow 是 sidecar-native、actor-backed 的 durable workflow runtime，而不是独立的外部 workflow server。 | 上方证据单元。 | 该架构可能降低 Dapr-native 集成成本，也会把 Placement、Scheduler/reminders 和 state store 纳入核心运维边界。 |
| Dapr Workflow 的状态、唤醒和扩缩容语义依赖 actor state、reminders 和同 app ID replicas。 | 上方证据单元。 | 这不等同于 Temporal task queue routing；资源池隔离需要 app ID、multi-app 或外层业务路由设计。 |
