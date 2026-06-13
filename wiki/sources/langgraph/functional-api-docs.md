---
schema_version: 2
page_type: source
title: "LangGraph Functional API 文档"
status: active
created: 2026-06-13
updated: 2026-06-13
summary: "LangGraph Functional API 官方文档的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - langgraph
  - functional-api
  - workflow
---

## 来源边界

本页只投影 LangGraph 的 Functional API 文档。
它用于界定 Functional API 中由普通 Python 控制流运行时生成任务执行图的语义。
原始材料未保存到 `raw/`；本页直接引用外部 URL 作为主证据。

## 可复用关键主张

- Functional API 允许用普通 Python 控制流组织 `@task` 和 `@entrypoint`。
- 文档将 Functional API 描述为 runtime dynamically generated graph，
  因此不同于显式 StateGraph 的静态拓扑 authoring。
- 这种 runtime-generated graph 是执行任务图/trace 的生成，
  不等同于已编译 StateGraph 在运行中任意增删节点/边。

## 限制与冲突

- 本页只投影 Functional API，不覆盖 StateGraph compile、graph migration 或 Agent
  Server deployment。
- “dynamically generated graph” 容易被误读为 topology mutation；
  本页仅按官方 Functional API 语境解释。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://docs.langchain.com/oss/python/langgraph/functional-api` | LangGraph Functional API 文档；访问时间 2026-06-13。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| LangGraph Functional API 使用普通 Python 控制流组织任务执行。 | 上方证据单元。 | 这不同于 StateGraph 的显式 topology surface。 |
| Functional API 的 runtime-generated graph 不等于已编译 StateGraph 原地拓扑修改。 | 上方证据单元。 | 仍需结合 StateGraph/Graph API source page 判断显式图语义。 |
