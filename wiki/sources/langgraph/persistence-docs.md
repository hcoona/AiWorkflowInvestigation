---
schema_version: 2
page_type: source
title: "LangGraph Persistence 文档"
status: active
created: 2026-06-12
updated: 2026-06-12
summary: "LangGraph persistence 官方文档的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - langgraph
  - persistence
  - checkpointing
---

## 来源边界

本页只投影 LangGraph persistence 文档。
它用于说明 checkpointers、stores、threads/thread_id 等持久化语义。
原始材料未保存到 `raw/`；本页直接引用外部 URL 作为主证据。

## 可复用关键主张

- LangGraph 使用 checkpointers 保存 thread-scoped graph state。
- stores 提供 cross-thread long-term memory。
- 在 OSS 自行编译 graph 时，恢复/持久化需要配置 checkpointer/store
  并传入 thread_id。

## 限制与冲突

- 使用 Agent Server 时，文档称 persistence 由服务器自动处理。
- persistence 机制不等于外部副作用自动幂等。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://docs.langchain.com/oss/python/langgraph/persistence` | LangGraph persistence 文档；访问时间 2026-06-12。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| LangGraph 的持久化由 checkpointers/stores 分层支撑。 | 上方证据单元。 | 需要在应用中正确配置和使用。 |
| OSS 自行编译 graph 时，恢复/持久化需要配置 checkpointer/store 并使用 thread_id。 | 上方证据单元。 | 使用 Agent Server 时，文档称 persistence 由服务器自动处理。 |
