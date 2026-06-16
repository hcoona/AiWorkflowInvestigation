---
schema_version: 2
page_type: source
title: "Durable Task Hosting Model 文档"
status: active
created: 2026-06-16
updated: 2026-06-16
summary: "Durable Functions 与 standalone Durable Task SDKs hosting model 对比的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - azure-durable-functions
  - durable-task
  - hosting
---

## 来源边界

本页只投影 Microsoft Learn 的 Choose Your Durable Task Hosting Model 文档。
它用于界定 Durable Functions 与 standalone Durable Task SDKs 的 hosting platform、
scaling、triggers、state storage、languages、monitoring 和内置 HTTP management API 差异。
原始材料未保存到 `raw/`；本页直接引用外部 URL 作为主证据。

## 可复用关键主张

- Durable Task 支持 Azure Functions via Durable Functions，以及 self-hosted standalone
  Durable Task SDKs 两种 hosting model。
- 两种 hosting model 提供相同核心 durable execution capabilities，
  但 application hosting、scaling 和 deployment 不同。
- 如果应用构建在 Azure Functions 上，使用 Durable Functions；
  如果运行在其它 compute platform 上，使用 standalone Durable Task SDKs。
- Durable Functions 由 Azure Functions managed scale infrastructure 管理自动伸缩，
  并具有 built-in Azure Functions triggers、portal/Application Insights 集成和内置 HTTP management APIs。
- Standalone Durable Task SDKs 需要自管 scaling、entry points 和 monitoring，
  但可运行在 AKS、VM、on-premises 等平台。

## 限制与冲突

- 本页支撑 hosting model 差异；
  不评价任何 model 对裸金属 buildout 的采购适配性。
- 本来源不评价任何业务 process manager 适配性；
  但它说明 hosting、scale、deployment、monitoring 和 storage backend 是两种 hosting model 的差异轴。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://learn.microsoft.com/en-us/azure/durable-task/common/choose-orchestration-framework` | Microsoft Learn Durable Task hosting model 文档；访问时间 2026-06-16。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| Durable Functions 和 standalone Durable Task SDKs 共享核心 durable execution capabilities，但 hosting/scaling/deployment 不同。 | 上方证据单元。 | 本页不证明它们在运维和生态约束上等价。 |
| Durable Functions 方案绑定 Azure Functions hosting/runtime 选择。 | 上方证据单元。 | App Service、Container Apps、AKS、VM/on-premises 等平台可能对应不同 hosting model。 |
