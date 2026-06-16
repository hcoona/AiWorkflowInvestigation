---
schema_version: 2
page_type: source
title: "Microsoft Agent Framework Azure Functions Durable Workflow Metadata Transformer 源码"
status: active
created: 2026-06-16
updated: 2026-06-16
summary: "MAF Azure Functions hosting 中 durable workflow function metadata 生成路径的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - microsoft-agent-framework
  - azure-functions
  - durable-extension
---

## 来源边界

本页只投影 Microsoft Agent Framework 仓库中的
`dotnet/src/Microsoft.Agents.AI.Hosting.AzureFunctions/Workflows/DurableWorkflowsFunctionMetadataTransformer.cs`
源码文件。
它用于说明 Azure Functions hosting 路径如何为每个已配置 durable workflow
动态注册 function metadata，以及如何为 workflow executor 生成 activity/entity
trigger metadata。
原始材料未保存到 `raw/`；本页直接引用 GitHub raw URL 作为主证据。

## 可复用关键主张

- `DurableWorkflowsFunctionMetadataTransformer` 的注释说明它会为 each configured
  durable workflow and its executors 动态注册 Azure Functions triggers。
- transformer 遍历 `workflowOptions.Workflows`；对每个 workflow 注册 orchestration
  trigger 与 HTTP trigger。
- 如果 workflow 启用 status endpoint、包含 request ports 或启用 MCP tool trigger，
  transformer 会为该 workflow 额外注册 status、respond 或 MCP tool trigger。
- 对 workflow 中的 executors，sub-workflow 和 request port bindings 使用专门
  dispatch，不注册为 activities；AI agent executors 使用 entity trigger；其它
  executors 使用 activity trigger。
- 当多个 workflows 共享同一 executor 时，对应 function 只注册一次。

## 限制与冲突

- 本页是 .NET Azure Functions hosting 源码投影；
  不覆盖 Python 实现、functional workflow surface 或未来版本。
- 本页证明一个 Azure Functions host 的 metadata transformer 可遍历多个已配置
  workflows，并为每个 workflow 生成 trigger metadata；
  不证明单个 graph 内部任意 executor 可跨多个 Function Apps 拆分。
- 本页说明 function metadata 生成路径；
  具体部署拓扑、worker routing、task hub/backend、identity 和网络边界仍需结合部署配置验证。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://raw.githubusercontent.com/microsoft/agent-framework/main/dotnet/src/Microsoft.Agents.AI.Hosting.AzureFunctions/Workflows/DurableWorkflowsFunctionMetadataTransformer.cs` | Microsoft Agent Framework `DurableWorkflowsFunctionMetadataTransformer.cs` 源码；访问时间 2026-06-16。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| MAF Azure Functions hosting 路径会遍历已配置 durable workflows，并为每个 workflow 注册 orchestration/HTTP trigger metadata。 | 上方证据单元。 | 这是 .NET Azure Functions hosting metadata transformer 源码证据；不覆盖其它语言或未来实现。 |
| 一个 Function App/host 的 metadata 生成路径可以处理多个 configured durable workflows。 | 上方证据单元。 | 这不等于推荐所有 workflows 放在同一 Function App；部署边界仍由发布、身份、伸缩和隔离需求决定。 |
| 普通 executor 在 Azure Functions hosting metadata 中表现为 activity trigger；AI agent executor 表现为 entity trigger；sub-workflow/request port 不注册为 ordinary activity trigger。 | 上方证据单元。 | 实际运行 dispatch 还需结合 Durable Executor Dispatcher 源码。 |
| 多个 workflows 共享 executor 时，metadata transformer 会避免重复注册对应 function。 | 上方证据单元。 | 这说明 metadata 去重语义，不说明共享 executor 的业务状态隔离策略。 |
