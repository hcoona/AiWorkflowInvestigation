---
schema_version: 2
page_type: source
title: "Microsoft Agent Framework Workflows 概览"
status: active
created: 2026-06-12
updated: 2026-06-12
summary: "Microsoft Agent Framework workflows 概览文档的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - microsoft-agent-framework
  - workflows
  - orchestration
---

## 来源边界

本页只投影 Microsoft Agent Framework 的 workflows 概览文档。
它用于说明 workflows 的定位、API surface 和适用边界。
原始材料未保存到 `raw/`；本页直接引用外部 URL 作为主证据。

## 可复用关键主张

- workflows 用于表达显式、多步、可编排的流程。
- workflows 与 agents 可以组合，但不是同一个抽象。
- Microsoft Agent Framework workflows 包含多种 surface，不能只按一个 API 理解。

## 限制与冲突

- 该页是概览，细节需要交给 functional、WorkflowBuilder 和 Durable Extension
  单来源投影页。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://learn.microsoft.com/en-us/agent-framework/workflows/` | Microsoft Agent Framework workflows 概览；访问时间 2026-06-12。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| Microsoft Agent Framework workflows 是显式流程编排 surface。 | 上方证据单元。 | 该页不完整说明每个 surface 的成熟度。 |
| workflows 与 agents 可以组合但概念上应区分。 | 上方证据单元。 | 需要结合 overview 判断总体系定位。 |
