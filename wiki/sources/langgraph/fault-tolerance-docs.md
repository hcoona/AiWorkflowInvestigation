---
schema_version: 2
page_type: source
title: "LangGraph Fault Tolerance 文档"
status: active
created: 2026-06-12
updated: 2026-06-12
summary: "LangGraph fault tolerance 官方文档的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - langgraph
  - fault-tolerance
  - retries
---

## 来源边界

本页只投影 LangGraph fault tolerance 文档。
它用于说明 retries、timeouts 和 error handlers 的图/图节点 execution
故障处理语义。
原始材料未保存到 `raw/`；本页直接引用外部 URL 作为主证据。

## 可复用关键主张

- LangGraph 提供图节点级 retries、timeouts 和 error handlers。
- fault tolerance 用于图/图节点 execution 失败处理。
- 图节点级 timeouts 和 error handlers 要求 `langgraph>=1.2`。

## 限制与冲突

- 本页不证明所有外部工具调用天然幂等或可恢复。
- timeouts 是 async-only；timeouts/error handlers 是 Python-only；
  retries 也存在于 TypeScript。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://docs.langchain.com/oss/python/langgraph/fault-tolerance` | LangGraph fault tolerance 文档；访问时间 2026-06-12。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| LangGraph 提供 retries、timeouts 和 error handlers 等故障处理能力。 | 上方证据单元。 | 这些能力需要配合节点设计和外部副作用治理。 |
| 图节点级 timeouts 和 error handlers 要求 `langgraph>=1.2`。 | 上方证据单元。 | timeouts 是 async-only；timeouts/error handlers 是 Python-only。 |
