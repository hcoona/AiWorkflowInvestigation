---
schema_version: 2
page_type: source
title: "Durable Task Entities 文档"
status: active
created: 2026-06-16
updated: 2026-06-16
summary: "Durable entities 小块状态和串行操作语义的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - azure-durable-functions
  - durable-task
  - entities
---

## 来源边界

本页只投影 Microsoft Learn 的 Durable Entities overview 文档。
它用于界定 durable entities 如何管理小块状态、entity identity、operations、
串行执行和与 orchestrations/clients 的消息交互。
原始材料未保存到 `raw/`；本页直接引用外部 URL 作为主证据。

## 可复用关键主张

- Entity functions / entities 定义读取和更新小块状态的 operations。
- Durable entities 显式管理 entity state，而不是像 orchestrator 一样通过控制流表示状态。
- 每个 entity 有唯一 identity，operation 被 runtime 通过可靠队列传递。
- 为避免冲突，单个 entity 的 operations 串行执行。
- Runtime 会把 entity state 持久化到 storage。

## 限制与冲突

- Durable entities 适合小块协调状态；
  本来源不证明它们可替代大型业务数据库、资源图或审计库。
- 将复杂业务实体建模为 entities 仍需要明确 schema、容量、查询、审计和迁移设计；
  这些内容不在本来源范围内。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://learn.microsoft.com/en-us/azure/durable-task/common/durable-task-entities` | Microsoft Learn Durable Entities overview；访问时间 2026-06-16。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| Durable entities 可管理小块状态并串行处理 operations。 | 上方证据单元。 | 本来源不覆盖大型业务数据库、资源图或审计库设计。 |
