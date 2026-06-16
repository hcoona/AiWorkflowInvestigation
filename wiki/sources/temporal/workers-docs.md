---
schema_version: 2
page_type: source
title: "Temporal Workers 文档"
status: active
created: 2026-06-16
updated: 2026-06-16
summary: "Temporal Worker Program、Worker Entity 与 Worker Process 概念的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - temporal
  - workers
  - scale
---

## 来源边界

本页只投影 Temporal Workers 文档。
它用于界定 Worker Program、Worker Entity、 Worker Identity 与 Worker Process
的区别，以及 Worker 与 Task Queue、Temporal Service 和用户代码执行位置的关系。

原始材料未保存到 `raw/`；本页直接引用外部 URL 作为主证据。

## 可复用关键主张

- Worker Entity 是 Worker Process 内监听特定 Task Queue 的单个 Worker。
- Worker Entity 只监听并轮询一个 Task Queue；它可以包含 Workflow Worker
  和/或 Activity Worker。
- Workers 是 stateless 的；blocked Workflow Execution 可以从 Worker 中移除，
  之后在同一或不同 Worker 上恢复，单个 Worker 可处理大量 open Workflow
  Executions， 但可能增加 latency。
- Worker Process 负责轮询 Task Queue、取出 Task、执行用户代码，并把结果返回
  Temporal Service。
- Worker Processes 在 Temporal Service 外部运行；Temporal Service
  不在自己的机器上 执行用户的 Workflow 和 Activity definitions，只负责 state
  transitions 和把 Tasks 提供给可用 Worker Entity。
- 生产级 Temporal Application 通常有运行在 Temporal Service 外部的一组 Worker
  Processes，并且可以按需拥有多个 Worker Processes。
- Worker Process 可以同时是 Workflow Worker Process 和 Activity Worker Process；
  多个 SDK 支持一个 Worker Process 内有多个 Worker
  Entities，因此一个进程可以监听多个 Task Queues。
- 执行 Activity Tasks 的 Worker Processes 必须能访问 Activity
  所需资源，例如网络、 credentials 或 GPU。

## 限制与冲突

- 本页支撑 Temporal worker
  放置和资源池语义；不证明任何具体部署平台、容器编排器或 cloud account 的容量。
- Worker 可处理大量 open Workflow Executions 的说法带有 latency trade-off；
  不能写成无代价无限承载。
- Worker Process 可以监听多个 Task Queues，但这只是允许的部署拓扑；
  是否应该合并仍取决于资源、依赖、SLA 和注册一致性。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://docs.temporal.io/workers` | Temporal Workers 文档；访问时间 2026-06-16。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| Temporal Worker Entity 监听单个 Task Queue；Worker Process 可包含多个 Worker Entities。 | 上方证据单元。 | 具体 SDK 的 Worker Entity 管理 API 不在本页范围。 |
| Temporal Worker Processes 在 Temporal Service 外部执行用户 Workflow/Activity 代码。 | 上方证据单元。 | Temporal Service 仍管理 state transitions 和任务分发。 |
| Temporal Application 可以按需运行多个 Worker Processes 形成 worker fleet。 | 上方证据单元。 | 资源利用仍受 worker sizing、queue backlog、依赖资源和运维约束影响。 |
| Workers 是 stateless，blocked Workflow Execution 可在需要时由同一或不同 Worker 恢复。 | 上方证据单元。 | 这可能增加 latency，且不意味着 activity 副作用本身无需幂等设计。 |
