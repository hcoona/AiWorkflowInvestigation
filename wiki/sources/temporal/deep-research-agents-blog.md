---
schema_version: 2
page_type: source
title: "Temporal Deep Research Agent 博客"
status: active
created: 2026-06-12
updated: 2026-06-12
summary: "Temporal 官方 deep research agent 博客的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - temporal
  - deep-research
  - ai-agents
---

## 来源边界

本页只投影 Temporal 官方博客
`How to Build Deep Research Agents using Temporal and Braintrust`。
它用于说明 deep research agent 作为长运行、多步 agent pipeline 的 Temporal
应用模式。 原始材料已保存到
[`raw/01-temporal/2026-06-03-how-to-build-deep-research-agents-using-temporal-and-braintrust.md`](../../../raw/01-temporal/2026-06-03-how-to-build-deep-research-agents-using-temporal-and-braintrust.md)；
本页使用该 raw 文件作为主证据。

## 可复用关键主张

- Deep research agent 可被拆成多个可恢复的步骤和 agent 子任务。
- Temporal 适合承载长时间运行、可观测、可恢复的 research pipeline。
- 该博客说明的是应用模式，而不是修改 Temporal workflow 的核心定义。

## 限制与冲突

- Braintrust 集成属于示例架构的一部分，不代表 Temporal 必须依赖该工具。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| raw | [`raw/01-temporal/2026-06-03-how-to-build-deep-research-agents-using-temporal-and-braintrust.md`](../../../raw/01-temporal/2026-06-03-how-to-build-deep-research-agents-using-temporal-and-braintrust.md) | Temporal 官方 deep research agent 博客正文原文。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| Temporal 可用于 deep research agent 这类长运行多步流程。 | 上方证据单元。 | 该博客是示例架构，不是唯一实现方式。 |
| deep research agent 是 durable execution 之上的应用模式。 | 上方证据单元。 | 需要结合 Temporal Workflow/Activity 文档判断执行边界。 |
