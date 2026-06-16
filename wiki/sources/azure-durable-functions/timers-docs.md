---
schema_version: 2
page_type: source
title: "Durable Task Timers 文档"
status: active
created: 2026-06-16
updated: 2026-06-16
summary: "Durable timers 长等待和 timeout 语义的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - azure-durable-functions
  - durable-task
  - timers
---

## 来源边界

本页只投影 Microsoft Learn 的 Durable timers 文档。
它用于界定 Durable Functions / Durable Task SDK 中 durable timer 如何表达 delay
和 timeout，以及不同语言和 storage provider 的长 timer 限制。
原始材料未保存到 `raw/`；本页直接引用外部 URL 作为主证据。

## 可复用关键主张

- Durable timers 可在 orchestrator functions / orchestrations 中实现 delays 或 timeouts。
- 应使用 durable timer，而不是语言内建 `sleep` 或 `delay` API。
- Timer 到期时，底层消息会使 function app 或 worker 再次激活。
- JavaScript、Python 和 PowerShell Durable Functions apps 的 durable timers
  限制为六天；较长等待需要循环模拟。最新 .NET 和 Java apps 支持任意长 timers。

## 限制与冲突

- Durable timer 支撑等待语义；
  本来源不覆盖副作用回滚、业务事实存储或业务审计。
- Timer 行为可能受语言 SDK 和 storage provider 影响；
  设计长期裸金属等待时必须复核目标语言和 backend。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://learn.microsoft.com/en-us/azure/durable-task/common/durable-task-timers` | Microsoft Learn Durable timers 文档；访问时间 2026-06-16。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| Durable Functions / Durable Task 支持 durable timers 表达等待和 timeout。 | 上方证据单元。 | 部分语言有六天 timer 限制或内部短 timer 链实现。 |
