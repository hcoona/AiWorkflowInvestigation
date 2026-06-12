---
schema_version: 2
page_type: source
title: "LangGraph Pregel Retry 源码"
status: active
created: 2026-06-12
updated: 2026-06-12
summary: "LangGraph Pregel retry 源码文件的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - langgraph
  - pregel
  - distributed-runtime
---

## 来源边界

本页只投影 LangGraph 仓库中的 `libs/langgraph/langgraph/pregel/_retry.py`
源码文件。
它用于说明 Pregel task 的本地 `invoke`/`ainvoke` 执行路径，以及 LangGraph
Platform distributed runtime 中 server 准备 task、executor
反序列化执行的源码注释。
原始材料未保存到 `raw/`；本页直接引用 GitHub raw URL 作为主证据。

## 可复用关键主张

- OSS 路径中的 `run_with_retry` 调用 `task.proc.invoke(...)`。
- OSS 路径中的 `arun_with_retry` 调用 `task.proc.ainvoke(...)` 或
  `task.proc.astream(...)`。
- 源码注释说明，在 LangGraph Platform distributed runtime 中，
  tasks 由 server 准备，并在 executor 中反序列化；这会绕过 OSS `_algo.py`
  通常创建 `ExecutionInfo` 的路径。

## 限制与冲突

- 本页支持 distributed runtime 存在 server/executor 分工，但不单独证明该模式提供
  用户可控的“每个图节点任意放置到不同 machine/host”的 API。
- “task”在本页指 Pregel executable task；不等同于 Airflow task 或
  Temporal Activity。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://raw.githubusercontent.com/langchain-ai/langgraph/main/libs/langgraph/langgraph/pregel/_retry.py` | LangGraph `_retry.py` 源码；访问时间 2026-06-12。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| OSS LangGraph Pregel task 执行调用本地 `invoke`/`ainvoke`/`astream` 路径。 | 上方证据单元。 | 这是源码实现线索，不替代官方部署文档。 |
| LangGraph Platform distributed runtime 有 server 准备 task、executor 反序列化执行的分工。 | 上方证据单元。 | 不应外推为 Airflow/Temporal/MAF Durable Extension 式公开 per-step placement 模型。 |
