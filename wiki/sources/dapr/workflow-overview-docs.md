---
schema_version: 2
page_type: source
title: "Dapr Workflow Overview 文档"
status: active
created: 2026-06-26
updated: 2026-06-26
summary: "Dapr Workflow 总体定位、SDK 与管理能力的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - dapr
  - workflow
  - durable-execution
---

## 来源边界

本页只投影 Dapr 官方 Dapr Workflow overview 文档。
它用于界定 Dapr Workflow 的产品定位、适用任务、SDK 入口和管理操作边界。
原始材料未保存到 `raw/`；本页直接引用外部 URL 作为主证据。

## 可复用关键主张

- Dapr Workflow 面向 long-running、stateful、fault-tolerant 的应用流程。
- Dapr Workflow 将业务流程写成 workflow 函数，并由 Dapr runtime
  负责 orchestration、状态持久化和恢复。
- 官方文档列出 .NET、Java、JavaScript、Python 和 Go SDK。
- Dapr Workflow 暴露 workflow management 操作，用于 start、query、
  pause/resume、raise event、terminate、purge 等生命周期管理。

## 限制与冲突

- 本来源只支撑 Dapr Workflow 的总体定位和入口能力；
  不覆盖 actor-backed runtime、state store、multi-app、versioning
  或具体生产运维限制。
- 本来源不证明 Dapr Workflow 自动满足裸金属 buildout 的资源身份、
  command gateway、业务 dashboard 或物理副作用安全。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://docs.dapr.io/developing-applications/building-blocks/workflow/workflow-overview/` | Dapr Workflow overview 官方文档；访问时间 2026-06-26。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| Dapr Workflow 是 Dapr 面向 long-running stateful workflows 的 workflow building block。 | 上方证据单元。 | 不说明它在裸金属 buildout 中应作为主 baseline、次级候选还是 adapter。 |
| Dapr Workflow 有多语言 SDK 与 workflow management 操作入口。 | 上方证据单元。 | 具体 SDK 能力和成熟度不完全一致，需要结合 SDK/source 证据和目标语言 POC。 |
