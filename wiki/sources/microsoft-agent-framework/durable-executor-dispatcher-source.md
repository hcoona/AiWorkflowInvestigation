---
schema_version: 2
page_type: source
title: "Microsoft Agent Framework Durable Executor Dispatcher 源码"
status: active
created: 2026-06-12
updated: 2026-06-12
summary: "Microsoft Agent Framework Durable executor dispatcher 源码文件的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - microsoft-agent-framework
  - durable-extension
  - executor-dispatch
---

## 来源边界

本页只投影 Microsoft Agent Framework 仓库中的
`dotnet/src/Microsoft.Agents.AI.DurableTask/Workflows/DurableExecutorDispatcher.cs`
源码文件。
它用于说明 Durable Extension 在 graph workflow superstep 中如何把 executor
dispatch 到 Durable Task activity、Durable Entity、sub-orchestration 或 external
event。
原始材料未保存到 `raw/`；本页直接引用 GitHub raw URL 作为主证据。

## 可复用关键主张

- `DurableExecutorDispatcher` 在 graph workflow 的每个 superstep dispatch phase
  被调用。
- dispatcher 会根据 executor 类型调用不同 Durable Task API： 普通 executor 使用
  `CallActivityAsync`，agent executor 通过 Durable Entity， subworkflow 使用
  `CallSubOrchestratorAsync`，request port 等待 external event。
- subworkflow 以独立 orchestration instance 运行，具备独立 checkpointing、replay
  和 dashboard visualization。

## 限制与冲突

- 本页是 .NET 源码投影；具体 host/worker scaling 仍需结合 Durable Task Scheduler
  与 Durable Extension 文档；functional workflow surface 需另行取证。
- “executor”在本页指 MAF workflow executor，不等同于 Airflow executor。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://raw.githubusercontent.com/microsoft/agent-framework/main/dotnet/src/Microsoft.Agents.AI.DurableTask/Workflows/DurableExecutorDispatcher.cs` | Microsoft Agent Framework `DurableExecutorDispatcher.cs` 源码；访问时间 2026-06-12。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| MAF Durable Extension 将 graph workflow 中的不同 executor 类型映射到 Durable Task activity/entity/sub-orchestration/external-event 路径。 | 上方证据单元。 | 具体并行度和跨 machine/host 放置由 Durable Task backend、worker 和 host 配置决定；functional workflow surface 需另行取证。 |
| 普通 executor 使用 `CallActivityAsync`，subworkflow 使用 `CallSubOrchestratorAsync`。 | 上方证据单元。 | agent 和 request-port 有专门语义，不应被简化为普通 activity。 |
