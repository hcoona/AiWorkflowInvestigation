---
schema_version: 2
page_type: source
title: "Microsoft Agent Framework Workflow Checkpoints 文档"
status: active
created: 2026-06-13
updated: 2026-06-13
summary: "Microsoft Agent Framework workflow checkpoints 官方文档的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - microsoft-agent-framework
  - checkpoints
  - workflow
---

## 来源边界

本页只投影 Microsoft Agent Framework Workflows 的 Checkpoints 文档。
它用于界定 checkpoints 保存什么状态，以及它们如何用于恢复、暂停和迁移。
原始材料未保存到 `raw/`；本页直接引用 Microsoft Learn URL 作为主证据。

## 可复用关键主张

- Checkpoints 保存 workflow
  执行中的状态，可用于失败恢复、暂停/恢复、审计/合规和跨环境迁移。
- Checkpoints 在 superstep 结束时创建。
- Checkpoint 捕获 executor state、下一 superstep 的 pending messages、pending
  requests/responses 和 shared states。
- 文档说明 checkpoint 的保存/恢复能力；
  它不承诺把 checkpoint 自动迁移到任意变更后的 graph topology。

## 限制与冲突

- 本页只投影 checkpoint 文档，不覆盖源码中的 graph compatibility 校验。
- 具体 checkpoint 兼容性需结合实现语言、storage backend 和 workflow definition。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://learn.microsoft.com/en-us/agent-framework/workflows/checkpoints` | Microsoft Agent Framework Workflows Checkpoints 文档；访问时间 2026-06-13。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| MAF checkpoints 捕获 workflow execution state 并支持恢复/迁移场景。 | 上方证据单元。 | 文档中的迁移是执行环境/实例迁移语境，不等于任意 graph schema migration。 |
| MAF checkpoints 不应被解释为自动 topology migration 能力。 | 上方证据单元。 | 兼容性约束需结合源码和具体 storage 后端。 |
