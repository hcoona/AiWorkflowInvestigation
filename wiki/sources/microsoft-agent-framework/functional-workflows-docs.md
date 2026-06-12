---
schema_version: 2
page_type: source
title: "Microsoft Agent Framework Functional Workflows 文档"
status: active
created: 2026-06-12
updated: 2026-06-12
summary: "Microsoft Agent Framework functional workflow API 文档的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - microsoft-agent-framework
  - functional-workflows
  - python
---

## 来源边界

本页只投影 Microsoft Agent Framework 的 functional workflows 文档。
它用于说明 `@workflow` / `@step` 等 Python functional workflow surface
及其成熟度信号。
原始材料未保存到 `raw/`；本页直接引用外部 URL 作为主证据。

## 可复用关键主张

- Functional Workflow API 允许用原生 Python 控制流表达 workflow。
- `@workflow` 与 `@step` 是该 surface 的关键入口。
- 官方警告：Functional Workflow API 是
  experimental，未来版本可能无通知变更或移除。

## 限制与冲突

- 本页不覆盖 graph `WorkflowBuilder` API。
- experimental 信号只说明该 surface 的风险，不等于整个框架不可用。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://learn.microsoft.com/en-us/agent-framework/workflows/functional` | Microsoft Agent Framework functional workflows 文档；访问时间 2026-06-12。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| Microsoft Agent Framework 提供 Python functional workflow surface。 | 上方证据单元。 | 不代表 graph API 具有同一成熟度信号。 |
| functional API 成熟度需要谨慎表述。 | 上方证据单元。 | experimental 限制是 surface-level，不是全框架判断。 |
