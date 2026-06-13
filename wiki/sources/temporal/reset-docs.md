---
schema_version: 2
page_type: source
title: "Temporal Reset 文档"
status: active
created: 2026-06-13
updated: 2026-06-13
summary: "Temporal Event History 与 Reset 官方文档的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - temporal
  - reset
  - event-history
---

## 来源边界

本页只投影 Temporal Events
and Event History 文档中 Event History 与 Reset 相关部分。
它用于界定 Reset 如何终止一个 Workflow Execution，并基于 reset point 创建新的
Workflow Execution。
原始材料未保存到 `raw/`；本页直接引用外部 URL 作为主证据。

## 可复用关键主张

- Temporal Event History 是 append-only log，用于 durable recovery 和 audit。
- Reset 终止一个 Workflow Execution，
  并用相同 Workflow Type 与 Workflow ID 创建新的 Workflow Execution。
- 新 execution 的 Event History 复制原 execution 到 reset point 为止的历史前缀。
- Reset 是边界修复/重放能力，不是原地改写已有历史。

## 限制与冲突

- Reset 的有效 reset point 和 Signals 复制选项需按 Temporal 文档和 CLI/API
  细节判断。
- 本页只说明 Reset 的概念边界，不覆盖 batch reset 或 reset-with-move
  的全部操作参数。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://docs.temporal.io/workflow-execution/event#reset` | Temporal Events and Event History 文档中的 Reset 段落；访问时间 2026-06-13。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| Temporal Event History 是 append-only，并用于 recovery 和 audit。 | 上方证据单元。 | 具体事件类型需查 Event reference。 |
| Temporal Reset 复制历史前缀并创建新的 Workflow Execution。 | 上方证据单元。 | Reset 不等于任意原地改写已有历史。 |
