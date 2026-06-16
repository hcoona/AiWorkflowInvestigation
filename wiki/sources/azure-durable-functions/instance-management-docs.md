---
schema_version: 2
page_type: source
title: "Durable Task Instance Management 文档"
status: active
created: 2026-06-16
updated: 2026-06-16
summary: "Durable Functions 与 Durable Task SDKs orchestration instance management 的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - azure-durable-functions
  - durable-task
  - instance-management
---

## 来源边界

本页只投影 Microsoft Learn 的 Durable Task instance management 文档。
它用于界定 Durable Functions 与 Durable Task SDKs 如何 start/schedule、
query、terminate、suspend、resume 和 purge orchestration instances，
以及 instance ID 的负载分布与外部实体映射边界。
原始材料未保存到 `raw/`；本页直接引用外部 URL 作为主证据。

## 可复用关键主张

- Durable Functions 的 orchestration client binding 和 Durable Task SDKs 的
  `DurableTaskClient` 都提供 instance management APIs。
- Start/schedule 操作会向 backend 写入消息并异步触发 orchestration instance。
- Start/schedule 支持可选 `InstanceId`；
  不指定时会使用随机 ID。
- 文档建议尽可能使用 random identifier 以便在 scale-out 时均衡负载；
  nonrandom instance ID 更适合 ID 来自外部来源或 singleton orchestrator 场景。
- Instance management APIs 覆盖 start、query/list、terminate、suspend、
  resume、purge 等运行时管理动作。

## 限制与冲突

- 固定 resource-derived instance ID 可支持外部实体映射，
  但也可能影响负载分布或热点；目标资源分区策略需要 PoC。
- Management APIs 是 orchestration control-plane 能力；
  不自动提供业务 command gateway、权限、审计、同步结果语义或物理副作用取消。
- Start/schedule 和管理操作的异步性质不应被解释为同步业务命令完成。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://learn.microsoft.com/en-us/azure/durable-task/common/durable-task-instance-management` | Microsoft Learn Durable Task instance management 文档；访问时间 2026-06-16。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| Durable Task 生态提供 orchestration instance start/query/terminate/suspend/resume/purge 等管理 API。 | 上方证据单元。 | 这些是 runtime 管理动作，不等于业务 command gateway。 |
| Orchestration instance ID 可以由调用方指定，并可来自外部来源。 | 上方证据单元。 | 文档建议默认随机 ID 以利于 scale-out 负载分布；固定资源 ID 需要热点与延迟验证。 |
