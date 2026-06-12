---
schema_version: 2
page_type: source
title: "Microsoft Agent Framework Durable Workflow Registration 源码"
status: active
created: 2026-06-12
updated: 2026-06-12
summary: "Microsoft Agent Framework Durable workflow registration 源码文件的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - microsoft-agent-framework
  - durable-extension
  - durable-task
---

## 来源边界

本页只投影 Microsoft Agent Framework 仓库中的
`dotnet/src/Microsoft.Agents.AI.DurableTask/ServiceCollectionExtensions.cs`
源码文件。
它用于说明 Durable Extension 如何注册 durable graph workflows、orchestrations、
activities 和 agent entities。
原始材料未保存到 `raw/`；本页直接引用 GitHub raw URL 作为主证据。

## 可复用关键主张

- `ConfigureDurableWorkflows` 用于配置 durable graph workflows。
- 源码注释说明该配置会自动注册 orchestrations 和 activities。
- 注册逻辑会为 workflows 建立 orchestration registrations。
- 普通 executor bindings 会被注册为 Durable Task activities；
  `AIAgentBinding`、`SubworkflowBinding` 与 `RequestPortBinding`
  使用专门 dispatch 路径而不是普通 activity。
- agent factories 会注册为 durable agent keyed services，并且 agent entities
  会注册到 Durable Task registry。

## 限制与冲突

- 本页是 .NET 源码投影，不覆盖 Python 实现、functional workflow surface
  或所有未来版本。
- 本页证明 Durable Extension 的注册映射，不证明未启用 Durable Extension 的
  core workflows 具备同等分布式放置语义。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://raw.githubusercontent.com/microsoft/agent-framework/main/dotnet/src/Microsoft.Agents.AI.DurableTask/ServiceCollectionExtensions.cs` | Microsoft Agent Framework `ServiceCollectionExtensions.cs` 源码；访问时间 2026-06-12。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| Durable Extension 将 graph workflows 注册为 Durable Task orchestrations，并将普通 executors 注册为 activities。 | 上方证据单元。 | 具体运行放置仍由 Durable Task worker/backend 与宿主决定；functional workflow surface 需另行取证。 |
| agent bindings 和 subworkflow/request-port bindings 使用不同于普通 activity 的专门 dispatch 路径。 | 上方证据单元。 | 需要结合 dispatcher 源码理解实际调用方式。 |
