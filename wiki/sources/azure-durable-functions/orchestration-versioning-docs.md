---
schema_version: 2
page_type: source
title: "Durable Task Orchestration Versioning 文档"
status: active
created: 2026-06-16
updated: 2026-06-16
summary: "Durable Functions 与 Durable Task SDKs orchestration versioning 的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - azure-durable-functions
  - durable-task
  - versioning
---

## 来源边界

本页只投影 Microsoft Learn 的 Durable Task orchestration versioning 文档。
它用于界定 Durable Functions 与 Durable Task SDKs 如何在 deterministic replay
约束下处理 orchestrator code 变更、orchestration instance version 绑定、
worker/version matching 和新旧 instance 兼容。
原始材料未保存到 `raw/`；本页直接引用外部 URL 作为主证据。

## 可复用关键主张

- Durable orchestration replay 会在 host update 后重新执行 orchestration code；
  如果代码变更导致步骤不一致，系统会抛出 nondeterminism error。
- Orchestration versioning 用于避免 nondeterminism 问题，
  同时保持 durable orchestrations 所需的 deterministic execution model。
- Orchestration instance 创建时会永久关联一个 version。
- Orchestrator code 可以读取当前 instance version 并在新旧逻辑之间分支。
- Durable Functions 的 built-in versioning backend agnostic；
  Durable Task SDKs 支持 client/context-based conditional versioning
  与 worker-based versioning。
- Durable Task SDKs 可在 client 侧为新 orchestration 设置默认或显式 version；
  worker version matching 可使用 `Strict`、`CurrentOrOlder`、`Reject`、`Fail`
  等策略保护新旧 execution。

## 限制与冲突

- Orchestration versioning 管理的是 orchestrator code compatibility，
  不是物理副作用回滚或任意业务状态迁移。
- 该机制仍要求保留或实现兼容旧 instance 的代码路径；
  不能把 in-flight orchestration 自动迁移到任意新流程。
- 具体最低版本、比较规则和策略支持随 Durable Functions extension、
  SDK 语言和 backend 而变化，目标部署需要复核。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://learn.microsoft.com/en-us/azure/durable-task/common/durable-orchestration-versioning` | Microsoft Learn Durable Task orchestration versioning 文档；访问时间 2026-06-16。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| Durable Task 生态有内建 orchestration versioning 机制，用于安全处理 orchestrator code 变更与 deterministic replay。 | 上方证据单元。 | 这不等于物理事实恢复、自动业务迁移或无成本升级。 |
| Orchestration instance 与 version 绑定，worker/client 可用 version matching 或条件分支支持新旧 instance 并存。 | 上方证据单元。 | 具体策略和版本比较规则依赖 hosting model 与语言 SDK。 |
