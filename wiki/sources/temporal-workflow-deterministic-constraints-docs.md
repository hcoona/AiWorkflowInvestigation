---
schema_version: 2
page_type: source
title: "Temporal Workflow 确定性约束文档"
status: active
created: 2026-06-12
updated: 2026-06-12
summary: "Temporal Workflow deterministic constraints 官方文档的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - temporal
  - determinism
  - workflow
---

## 来源边界

本页只投影 Temporal 的 deterministic constraints 文档锚点。
它用于说明 Workflow 代码在 replay 下必须保持确定性。
原始材料未保存到 `raw/`；本页直接引用外部 URL 作为主证据。

## 可复用关键主张

- Workflow 代码对同一输入和历史必须产生相同的 SDK 调用序列。
- 非确定性行为不应直接进入 Workflow replay 路径。
- Temporal 的动态控制流需要服从 deterministic replay 约束。

## 限制与冲突

- 本页只解释 Workflow 代码约束，不说明 Activity 内部的非确定性处理。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://docs.temporal.io/workflow-definition#deterministic-constraints` | Temporal Workflow deterministic constraints；访问时间 2026-06-12。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| Temporal Workflow 代码必须满足 deterministic replay 约束。 | 上方证据单元。 | 该约束不等于 Activity 代码也必须确定性。 |
| Temporal 的“动态”流程仍必须通过 replay-safe 方式表达。 | 上方证据单元。 | 复杂副作用需要配合 Activities source page 解读。 |
