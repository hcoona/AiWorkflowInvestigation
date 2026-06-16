---
schema_version: 2
page_type: source
title: "Azure Durable Functions Overview 文档"
status: active
created: 2026-06-16
updated: 2026-06-16
summary: "Azure Durable Functions stateful serverless workflows 定位的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - azure-durable-functions
  - durable-task
  - orchestration
---

## 来源边界

本页只投影 Microsoft Learn 的 Durable Functions overview 文档。
它用于界定 Durable Functions 与 Azure Functions、orchestrator functions、
activity functions、entity functions、runtime state/checkpoint/retry/recovery
以及 backend storage providers 的关系。
原始材料未保存到 `raw/`；本页直接引用外部 URL 作为主证据。

## 可复用关键主张

- Durable Functions 是 Azure Functions 的扩展，用于在 serverless environment
  中通过 orchestrator、activity 和 entity functions 构建 stateful workflows。
- Durable Functions runtime 管理 state、checkpoints、retries 和 recovery，
  使 workflows 能可靠地长期运行。
- 开始使用 Durable Functions 需要创建 Azure Functions app、添加 orchestrator
  与 activity functions，并选择 backend storage provider。

## 限制与冲突

- 本页只支撑 Durable Functions 的总体定位；
  不覆盖具体 orchestration replay、code constraints、external events、entities、
  storage provider 取舍或 Azure Functions hosting plans。
- 本来源只说明 runtime/workflow 定位；
  不证明 runtime state 可替代任何业务领域事实库。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://learn.microsoft.com/en-us/azure/durable-task/durable-functions/durable-functions-overview` | Microsoft Learn Durable Functions overview；访问时间 2026-06-16。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| Durable Functions 是 Azure Functions 上的 stateful serverless workflow 扩展。 | 上方证据单元。 | 不说明它在裸金属 buildout 中的业务适配性。 |
| Durable Functions runtime 管理 state、checkpoints、retries 和 recovery。 | 上方证据单元。 | 这些是 orchestration runtime 能力；本来源不覆盖业务领域事实库设计。 |
