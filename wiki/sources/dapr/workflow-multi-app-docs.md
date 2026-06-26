---
schema_version: 2
page_type: source
title: "Dapr Multi-Application Workflows 文档"
status: active
created: 2026-06-26
updated: 2026-06-26
summary: "Dapr Workflow 跨 appID 调度与同 namespace/state store 限制的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - dapr
  - workflow
  - multi-app
  - routing
---

## 来源边界

本页只投影 Dapr 官方 Multi-Application Workflows 文档。
它用于界定 Dapr Workflow 如何从一个 app 调度另一个 app 的 activity
或 child workflow，以及该模式的 namespace、state store、SDK 和注册限制。
原始材料未保存到 `raw/`；本页直接引用外部 URL 作为主证据。

## 可复用关键主张

- Multi-app workflows 允许 workflow 调用另一个 Dapr app ID 中注册的
  activity 或 child workflow。
- 该机制可用于把 GPU、网络或依赖不同的执行负载拆到不同 app。
- Multi-app workflows 要求参与 app 位于同一 namespace，
  并使用相同 workflow/actor state store。
- 目标 app 必须注册被调用的 activity 或 child workflow；
  否则父 workflow 可能持续等待或重试。
- 具体 SDK 支持度和限制需要按目标语言复核。

## 限制与冲突

- Multi-app app ID routing 不是 Temporal task queue 的直接等价物；
  它更像通过 app 边界划分 execution domain。
- 同 namespace 和同 state store 要求会限制跨 namespace、跨集群或跨环境的资源池隔离。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://docs.dapr.io/developing-applications/building-blocks/workflow/workflow-multi-app/` | Dapr Multi-Application Workflows 官方文档；访问时间 2026-06-26。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| Dapr Workflow 可以通过 multi-app workflows 把 activity 或 child workflow 调度到不同 app ID。 | 上方证据单元。 | 该能力受同 namespace、同 state store、目标 app 注册和 SDK 支持边界限制。 |
| Dapr app ID routing 可缓解但不能直接替代 Temporal activity task queue routing。 | 上方证据单元。 | 这是本 wiki 对不同 routing abstraction 的机制判断；目标架构仍需 POC 验证。 |
