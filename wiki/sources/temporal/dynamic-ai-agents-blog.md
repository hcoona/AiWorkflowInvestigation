---
schema_version: 2
page_type: source
title: "Temporal 动态 AI Agent 博客"
status: active
created: 2026-06-12
updated: 2026-06-12
summary: "Temporal 官方动态 AI agent 博客的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - temporal
  - ai-agents
  - durable-execution
---

## 来源边界

本页只投影 Temporal 官方博客
`Of Course You Can Build Dynamic AI Agents with Temporal`。
它用于说明 Temporal 如何承载动态 agent 模式。 原始材料已保存到
[`raw/01-temporal/2025-11-12-of-course-you-can-build-dynamic-ai-agents-with-temporal.md`](../../../raw/01-temporal/2025-11-12-of-course-you-can-build-dynamic-ai-agents-with-temporal.md)；
本页使用该 raw 文件作为主证据。

## 可复用关键主张

- Temporal 可以把 agent loop 表达为 durable workflow。
- 非确定性的模型调用和工具调用应放在 Activities 或等价副作用边界。
- Temporal 的 agent 方案仍依赖 durable execution，而不是替代 Workflow/Activity
  模型。

## 限制与冲突

- 官方博客带有产品立场；引用时应把它当作 Temporal 提供的应用模式示例。
- 博客示例不等于独立证明 Temporal 是专用 agent runtime。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| raw | [`raw/01-temporal/2025-11-12-of-course-you-can-build-dynamic-ai-agents-with-temporal.md`](../../../raw/01-temporal/2025-11-12-of-course-you-can-build-dynamic-ai-agents-with-temporal.md) | Temporal 官方动态 AI agent 博客正文原文。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| Temporal 可以承载动态 AI agent 模式。 | 上方证据单元。 | 这是官方示例，不是独立第三方验证。 |
| Temporal agent 模式仍建立在 Workflow/Activity 边界上。 | 上方证据单元。 | 需要结合 Workflows 和 Activities 文档理解。 |
