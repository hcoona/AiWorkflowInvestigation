---
schema_version: 2
page_type: source
title: "Temporal Workflows 文档"
status: active
created: 2026-06-12
updated: 2026-06-12
summary: "Temporal Workflows 官方文档的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - temporal
  - workflow
  - durable-execution
---

## 来源边界

本页只投影 Temporal 的 `https://docs.temporal.io/workflows` 文档。
它用于界定 Workflow Definition、Workflow Execution、Event History 和 replay
等核心术语。
原始材料未保存到 `raw/`；本页直接引用外部 URL 作为主证据。

## 可复用关键主张

- Temporal Workflow 是由代码定义的多步执行单元。
- Workflow Execution 是 durable、reliable、scalable 的运行实例。
- Event History 是 Workflow 状态恢复和 replay 的关键证据。

## 限制与冲突

- 本页不覆盖 Activities 的副作用边界；该边界由独立 source page 记录。
- 文档会随 Temporal 平台演进，本页记录 2026-06-12 访问时支撑的主张。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://docs.temporal.io/workflows` | Temporal Workflows 官方文档；访问时间 2026-06-12。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| Temporal Workflow 是 durable execution 的代码化工作流抽象。 | 上方证据单元。 | 需要与 Activities 和 determinism 文档一起理解完整边界。 |
| Event History/replay 是 Temporal 恢复语义的核心。 | 上方证据单元。 | 本页不单独证明所有 SDK 的具体实现细节。 |
