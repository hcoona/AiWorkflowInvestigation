---
schema_version: 2
page_type: source
title: "Temporal Message Passing 文档"
status: active
created: 2026-06-13
updated: 2026-06-13
summary: "Temporal Signals、Updates 和 Queries 的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - temporal
  - message-passing
  - workflow
---

## 来源边界

本页只投影 Temporal TypeScript SDK 的 Workflow message passing 文档。
它用于界定 Signals、Updates 和 Queries 如何与运行中的 Workflow Execution 交互。
原始材料未保存到 `raw/`；本页直接引用外部 URL 作为主证据。

## 可复用关键主张

- Signal 是异步消息，可向运行中的 Workflow 发送外部事件。
- Update 是可验证、可追踪并可返回结果的请求，可改变 Workflow 状态。
- Query 用于读取 Workflow 状态，不应改变 Workflow 状态。
- 这些机制让 Workflow Execution 的后续行为受运行期消息影响，
  但它们改变的是 execution state 和控制路径，不是 Workflow Definition 本身。

## 限制与冲突

- 本页只投影 TypeScript SDK 文档；
  其它 SDK 的 API 名称和 handler 细节可能不同。
- message passing 解释动态输入和状态变化，不覆盖 versioning、deployment routing
  或 Activities 的副作用边界。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://docs.temporal.io/develop/typescript/workflows/message-passing` | Temporal TypeScript Workflow message passing 文档；访问时间 2026-06-13。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| Temporal Signals 和 Updates 可影响运行中 Workflow Execution 的状态和后续行为。 | 上方证据单元。 | 这是 execution state/message 交互，不是 Workflow Definition 原地改写。 |
| Temporal Queries 用于读取状态，不应改变 Workflow 状态。 | 上方证据单元。 | 具体 handler 限制仍应按 SDK 文档判断。 |
