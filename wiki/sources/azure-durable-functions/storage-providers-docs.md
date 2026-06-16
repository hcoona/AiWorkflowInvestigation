---
schema_version: 2
page_type: source
title: "Durable Task Storage Providers 文档"
status: active
created: 2026-06-16
updated: 2026-06-16
summary: "Durable Functions 和 Durable Task SDKs storage providers 的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - azure-durable-functions
  - durable-task
  - storage
---

## 来源边界

本页只投影 Microsoft Learn 的 Durable Task storage providers 文档。
它用于界定 Durable Functions / Durable Task SDKs 如何通过 storage provider
持久化 orchestration history、entity state 和 internal messages，
以及 Durable Functions 支持的 Azure managed 与 BYO storage 选项。
原始材料未保存到 `raw/`；本页直接引用外部 URL 作为主证据。

## 可复用关键主张

- Storage providers 持久化 orchestration history、entity state 和 internal messages。
- Durable storage 使 workflows 可以 pause、scale、restart 和 recover without losing progress。
- Durable Functions 支持 Durable Task Scheduler、Azure Storage、Netherite、MSSQL 等 backend。
- Durable Task Scheduler 是 Azure managed backend，并提供 management/observability/performance/security
  等方面的管理能力和 dashboard。
- 某些 storage provider 选项有迁移、连接性、scale-out、KEDA 或支持状态限制。

## 限制与冲突

- Storage provider 是 orchestration runtime 状态后端；
  本来源不覆盖业务领域事实库或审计库设计。
- Backend 选择会影响部署、运维、迁移和环境连接性；
  不能把 Durable Functions 的核心语义与 hosting/storage 约束分开评价。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://learn.microsoft.com/en-us/azure/durable-task/common/durable-task-storage-providers` | Microsoft Learn Durable Task storage providers 文档；访问时间 2026-06-16。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| Durable Task storage provider 持久化 orchestration history、entity state 和 internal messages。 | 上方证据单元。 | 这是 runtime backend；本来源不覆盖业务领域事实库设计。 |
| Durable Functions 支持 Durable Task Scheduler、Azure Storage、Netherite 和 MSSQL 等 storage provider。 | 上方证据单元。 | provider 可用性、支持状态和适用场景需按目标版本复核。 |
| Durable Task Scheduler 是 Azure managed backend，并提供 dashboard 等管理能力。 | 上方证据单元。 | dashboard 面向 Durable Task runtime，不等同于业务操作员 UI。 |
| Durable Functions storage backend 选择会影响运维、迁移、连接性和环境适配。 | 上方证据单元。 | 具体取舍需按目标 backend 和组织约束评估。 |
