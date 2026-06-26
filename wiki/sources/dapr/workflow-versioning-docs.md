---
schema_version: 2
page_type: source
title: "Dapr Workflow Versioning 文档"
status: active
created: 2026-06-26
updated: 2026-06-26
summary: "Dapr Workflow patching 与 named workflow versioning 的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - dapr
  - workflow
  - versioning
  - deterministic-replay
---

## 来源边界

本页只投影 Dapr 官方 Workflow versioning 文档。
它用于界定 Dapr Workflow 在 deterministic replay 约束下如何处理 workflow
code 变更、patching、named workflow versioning、stalled workflow
和 old-version retention。
原始材料未保存到 `raw/`；本页直接引用外部 URL 作为主证据。

## 可复用关键主张

- Dapr Workflow code 变更必须保持 replay compatible；
  不兼容变更可能让在途 workflow stalled。
- Patching 允许 workflow code 在 replay-safe 边界内引入条件逻辑。
- Named workflow versioning 允许新旧 workflow definition 并存，
  并将新 instance 调度到指定版本。
- 长期或 dormant workflow 需要保留旧版本代码，直到依赖旧版本的 instances 结束或迁移。

## 限制与冲突

- Versioning 处理的是 workflow code/replay compatibility；
  不是物理副作用回滚、任意 topology mutation 或自动业务状态迁移。
- 该来源不覆盖所有 SDK 对 patching/named versions 的支持差异；
  目标语言必须单独验证。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://docs.dapr.io/developing-applications/building-blocks/workflow/workflow-versioning/` | Dapr Workflow versioning 官方文档；访问时间 2026-06-26。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| Dapr Workflow 支持 patching 和 named workflow versioning 来管理 deterministic replay 下的代码演进。 | 上方证据单元。 | 具体 SDK 和部署策略仍需目标环境 POC；这不是物理过程自动迁移。 |
| Agent-driven plan change 应作为受控业务事件或版本化输入进入 workflow，而不是在运行时原地改写 workflow definition。 | 上方证据单元。 | 这是基于 Dapr replay/versioning 约束的架构判断；业务 PlanPatch schema 与审批流需另行设计。 |
