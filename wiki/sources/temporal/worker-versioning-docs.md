---
schema_version: 2
page_type: source
title: "Temporal Worker Versioning 文档"
status: active
created: 2026-06-13
updated: 2026-06-13
summary: "Temporal Worker Versioning 和 Build ID routing 的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - temporal
  - worker-versioning
  - deployment
---

## 来源边界

本页只投影 Temporal Worker Versioning 文档。
它用于界定 Worker Deployment Version、Build ID routing 与 Workflow task
路由如何影响运行中 Workflow 的代码版本。
原始材料未保存到 `raw/`；本页直接引用外部 URL 作为主证据。

## 可复用关键主张

- Worker Versioning 解决的是不同 Workflow Execution 如何路由到兼容的 worker
  code version。
- Pinned 或 auto-upgrade 等模式影响 task routing 和部署演进。
- Worker Versioning 不是任意 runtime Workflow Definition mutation；
  replay-safe 约束和 versioning 策略仍然存在。

## 限制与冲突

- 本页只记录 Worker Versioning 的 deployment routing 边界；
  不覆盖应用层如何设计状态迁移。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://docs.temporal.io/production-deployment/worker-deployments/worker-versioning` | Temporal Worker Versioning 文档；访问时间 2026-06-13。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| Temporal Worker Versioning 管理 Workflow task 到 worker code version 的路由。 | 上方证据单元。 | 这是部署路由能力，不是当前 execution 内任意改写流程定义。 |
| Worker Versioning 与 replay-safe 代码演进相关。 | 上方证据单元。 | 具体升级策略还需结合 patching 和 deterministic constraints。 |
