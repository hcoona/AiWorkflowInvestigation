---
schema_version: 2
page_type: source
title: "Microsoft Agent Framework Workflow State 文档"
status: active
created: 2026-06-13
updated: 2026-06-13
summary: "Microsoft Agent Framework workflow state 官方文档的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - microsoft-agent-framework
  - workflow-state
  - immutability
---

## 来源边界

本页只投影 Microsoft Agent Framework Workflows 的 State 文档。
它用于界定 workflow state、state isolation、mutable workflow builders 与
immutable workflows 的边界。
原始材料未保存到 `raw/`；本页直接引用 Microsoft Learn URL 作为主证据。

## 可复用关键主张

- Workflow state 允许 workflow 中多个 executors 访问和修改共享数据。
- Workflow builders 被描述为 generally mutable。
- Workflows 被描述为 immutable：workflow build 后不能通过 public API 修改。
- 官方建议为不同任务或请求创建新的 workflow instance，
  以避免状态共享和线程安全问题。

## 限制与冲突

- 本页投影的是 Microsoft Learn state 文档，不覆盖 Durable Extension 或
  checkpoint storage 的全部行为。
- “immutable” 是 public API 层面的 workflow instance 语义；
  不排除应用通过 builder/YAML/Python code 生成新的 workflow instance。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://learn.microsoft.com/en-us/agent-framework/workflows/state` | Microsoft Agent Framework Workflows State 文档；访问时间 2026-06-13。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| MAF workflow builders 可变，而 built workflows 没有 public API 可修改。 | 上方证据单元。 | 这是 workflow instance 级语义，不排除新建 workflow definition。 |
| MAF workflow state 是 execution 内共享数据，不是 graph topology mutation。 | 上方证据单元。 | state 可影响行为，但不自动修改 graph。 |
