---
schema_version: 2
page_type: source
title: "LangGraph Pregel Executor 源码"
status: active
created: 2026-06-12
updated: 2026-06-12
summary: "LangGraph Pregel executor 源码文件的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - langgraph
  - pregel
  - executor
---

## 来源边界

本页只投影 LangGraph 仓库中的 `libs/langgraph/langgraph/pregel/_executor.py`
源码文件。
它用于说明 OSS LangGraph Pregel 执行器在本地进程内使用 thread pool 或 event loop
承载 graph task execution。
原始材料未保存到 `raw/`；本页直接引用 GitHub raw URL 作为主证据。

## 可复用关键主张

- `BackgroundExecutor` 用 thread pool executor 将 sync tasks 分派到线程。
- `AsyncBackgroundExecutor` 使用当前 event loop 将 async tasks 分派为 asyncio
  tasks。
- 因此，在 OSS compiled graph 直接运行路径中，并发执行边界是本地线程或 event
  loop， 不是外部 worker/process pool。

## 限制与冲突

- 本页是源码级证据，说明 OSS runtime 的本地执行器；它不覆盖 LangGraph Platform
  distributed runtime 的所有内部实现。
- 本页使用 “graph task” 或 “图节点任务”指 Pregel execution task，
  不使用裸 “node” 表示 machine/host。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://raw.githubusercontent.com/langchain-ai/langgraph/main/libs/langgraph/langgraph/pregel/_executor.py` | LangGraph `_executor.py` 源码；访问时间 2026-06-12。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| OSS LangGraph sync Pregel tasks 通过本地 thread pool 执行。 | 上方证据单元。 | 具体 executor 可受 `RunnableConfig` 影响，但仍是进程内 executor 抽象。 |
| OSS LangGraph async Pregel tasks 通过当前 event loop 执行。 | 上方证据单元。 | 不说明平台托管模式下的远端执行细节。 |
