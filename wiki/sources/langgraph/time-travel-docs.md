---
schema_version: 2
page_type: source
title: "LangGraph Time Travel 文档"
status: active
created: 2026-06-13
updated: 2026-06-13
summary: "LangGraph time travel 官方文档的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - langgraph
  - time-travel
  - checkpoint
---

## 来源边界

本页只投影 LangGraph 的 Time Travel 文档。
它用于界定 replay、fork 和 `update_state` 如何改变后续执行路径。
原始材料未保存到 `raw/`；本页直接引用外部 URL 作为主证据。

## 可复用关键主张

- Time travel 通过 checkpoints 支持 replay 和 fork。
- Replay 从 prior checkpoint 继续，checkpoint 之后的节点会重新执行。
- Fork 通过 `update_state` 从过去 checkpoint 创建带修改 state 的新分支；
  原 execution history 保持 intact。
- `update_state` 可通过 `as_node` 影响后续 pending successors，
  但改变的是 state/checkpoint 分支，不是 graph topology。

## 限制与冲突

- Time travel 会重新触发后续节点中的 LLM/API/interrupts；
  这影响可复现性。
- 本页不覆盖 graph migrations 或 compiled graph builder 边界。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://docs.langchain.com/oss/python/langgraph/use-time-travel` | LangGraph Time Travel 文档；访问时间 2026-06-13。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| LangGraph time travel 可通过 checkpoint replay/fork 改变后续执行路径。 | 上方证据单元。 | 后续节点会重新执行，外部副作用需单独管理。 |
| LangGraph `update_state` 创建新的 checkpoint 分支而不是回滚或改写原历史。 | 上方证据单元。 | 这不是 graph topology mutation。 |
