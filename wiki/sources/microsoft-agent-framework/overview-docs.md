---
schema_version: 2
page_type: source
title: "Microsoft Agent Framework Overview 文档"
status: active
created: 2026-06-12
updated: 2026-06-12
summary: "Microsoft Agent Framework overview 官方文档的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - microsoft-agent-framework
  - agents
  - workflows
---

## 来源边界

本页只投影 Microsoft Agent Framework 的 overview 文档。
它用于说明 Agent Framework 的总体定位、agents/workflows 关系和可用能力边界。
原始材料未保存到 `raw/`；本页直接引用外部 URL 作为主证据。

## 可复用关键主张

- Microsoft Agent Framework 把 agents 与 workflows 作为相关但不同的抽象。
- agents 更偏 LLM 驱动、工具使用和会话能力。
- workflows 更偏显式流程、编排和多步控制。

## 限制与冲突

- overview 是总览文档，不能替代 workflow-specific API 文档。
- 成熟度判断需要结合 functional workflow、WorkflowBuilder 和 Durable Extension
  文档。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://learn.microsoft.com/en-us/agent-framework/overview/` | Microsoft Agent Framework overview；访问时间 2026-06-12。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| Microsoft Agent Framework 同时覆盖 agents 和 workflows。 | 上方证据单元。 | 总览文档不提供每个 API surface 的完整成熟度说明。 |
| agents 与 workflows 不应被当成完全同义的概念。 | 上方证据单元。 | 具体职责边界需要结合 workflows 文档判断。 |
