---
schema_version: 2
page_type: source
title: "Microsoft Agent Framework Durable Workflow Registration 源码"
status: active
created: 2026-06-12
updated: 2026-06-16
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
- `ConfigureDurableAgents`、`ConfigureDurableWorkflows` 和 `ConfigureDurableOptions`
  的注释说明 multiple calls are supported，并且 configurations are composed
  additively。
- 源码注释说明该配置会自动注册 orchestrations 和 activities。
- `ConfigureDurableOptions` 示例在一个 shared durable options 中同时注册 agents
  和 workflows。
- `RegisterTasksFromOptions` 遍历 `durableOptions.Workflows.Values`，为 workflows
  构造 registrations，并递归处理 subworkflows。
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
| external | `https://raw.githubusercontent.com/microsoft/agent-framework/main/dotnet/src/Microsoft.Agents.AI.DurableTask/ServiceCollectionExtensions.cs` | Microsoft Agent Framework `ServiceCollectionExtensions.cs` 源码；访问时间 2026-06-12；2026-06-16 复查同一 raw URL。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| Durable Extension 将 graph workflows 注册为 Durable Task orchestrations，并将普通 executors 注册为 activities。 | 上方证据单元。 | 具体运行放置仍由 Durable Task worker/backend 与宿主决定；functional workflow surface 需另行取证。 |
| Durable Extension 的配置支持 additive 的多次调用，并在 shared options 中注册多个 workflows/agents。 | 上方证据单元。 | 这支持“应用/host 配置可包含多个 durable workflows”；不等于证明单个 graph 内部可任意跨多个 Function Apps 拆分。 |
| Durable Extension 会遍历已配置 workflows，并在 base DurableTask worker registration path 中递归将 subworkflows 注册为 separate orchestrations。 | 上方证据单元。 | 这是 .NET 源码证据；具体 orchestration 命名、Azure Functions metadata/Function App path、host 放置和 worker 路由仍由实现与部署配置决定。 |
| agent bindings 和 subworkflow/request-port bindings 使用不同于普通 activity 的专门 dispatch 路径。 | 上方证据单元。 | 需要结合 dispatcher 源码理解实际调用方式。 |
