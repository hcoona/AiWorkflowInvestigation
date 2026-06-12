---
schema_version: 2
page_type: source
title: "LangGraph Overview 文档"
status: active
created: 2026-06-12
updated: 2026-06-12
summary: "LangGraph overview 官方文档的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - langgraph
  - orchestration-runtime
  - agents
---

## 来源边界

本页只投影 LangGraph overview 文档。
它用于说明 LangGraph 的 low-level orchestration framework/runtime 定位。
原始材料未保存到 `raw/`；本页直接引用外部 URL 作为主证据。

## 可复用关键主张

- LangGraph 面向 long-running、stateful agents/workflows。
- LangGraph 被定位为 low-level orchestration framework/runtime。
- durable execution、streaming、HITL 和 persistence 是其核心定位的一部分。

## 限制与冲突

- overview 说明定位，不替代 persistence、interrupts 或 fault-tolerance 细节页。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://docs.langchain.com/oss/python/langgraph/overview` | LangGraph overview 文档；访问时间 2026-06-12。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| LangGraph 是面向 long-running stateful agents/workflows 的低层 runtime。 | 上方证据单元。 | 具体持久化机制需看 persistence 文档。 |
| LangGraph overview 将 durable execution、streaming、HITL 和 persistence 列为核心能力。 | 上方证据单元。 | 本页不讨论 batch scheduling。 |
