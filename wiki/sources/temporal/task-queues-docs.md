---
schema_version: 2
page_type: source
title: "Temporal Task Queues 文档"
status: active
created: 2026-06-16
updated: 2026-06-16
summary: "Temporal Task Queue 调度、路由和 worker 轮询语义的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - temporal
  - task-queues
  - scale
---

## 来源边界

本页只投影 Temporal Task Queues 文档。
它用于界定 Task Queue 作为 Workflow Task、Activity Task 和 Nexus Task
的轻量调度队列，以及它与 Worker 轮询、负载均衡、任务路由和分区的关系。

原始材料未保存到 `raw/`；本页直接引用外部 URL 作为主证据。

## 可复用关键主张

- Task Queue 是轻量、动态分配的队列，一个或多个 Worker Entities 可以轮询它来获取
  Tasks。
- Task Queues 不需要显式注册；Workflow Execution、Activity、Nexus Operation
  被调用或 Worker Process 开始轮询时按需创建。
- 一个 Temporal Application 可以使用、Temporal Service 可以维护不限数量的
  Task Queues。
- Workers 通过同步 RPC 轮询 Task Queues；Worker Process 只有在有 spare capacity
  时才轮询消息。
- Task Queues 支持跨多个 Worker Processes 的 load balancing、Task Routing、
  Activity Task Queues 的 server-side throttling，以及 worker down 时持久保存
  Workflow/Activity Tasks。
- 同一 Task Queue 上的 Worker Entities 通常必须注册相同的 Workflow、Activity
  和 Nexus handlers；否则对应 Task 会以 Not Found 失败。
- Workflow Execution、Worker Entity/Process、Activity Execution、Child Workflow
  Execution 和 Nexus Endpoint 都可以设置或继承 Task Queue 名称。
- Task Queues 可以通过 partitions 扩展；默认每个 Task Queue 有 4 个 partitions。

## 限制与冲突

- 本页支撑 Task Queue 的调度、路由和 scale-out 语义；不提供具体系统容量、
  成本或端到端 benchmark。
- “unlimited number of Task Queues” 是产品模型主张，不等于无成本地无限扩容；
  仍需要容量、命名、worker 注册和运维治理。
- 同一 Task Queue 的 worker 注册一致性要求意味着 Task Queue 是路由边界，
  不是把任意异构代码混在一起的自由池。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://docs.temporal.io/task-queue` | Temporal Task Queues 文档；访问时间 2026-06-16。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| Temporal Task Queue 是轻量、按需创建的调度队列，可由一个或多个 Worker Entities 轮询。 | 上方证据单元。 | 不给出具体容量上限或成本模型。 |
| Task Queues 支持 load balancing、Task Routing、server-side throttling 和持久化 Workflow/Activity Tasks。 | 上方证据单元。 | 这些能力需要正确配置 worker 注册、queue 命名和超时/重试策略。 |
| Temporal 可以在启动 Workflow、运行 Worker、启动 Activity 或 Child Workflow 时设置 Task Queue。 | 上方证据单元。 | 具体 API 名称随 SDK 变化；本页只投影概念文档。 |
| Task Queues 可通过 partitions 扩展，默认每个 Task Queue 有 4 个 partitions。 | 上方证据单元。 | 分区影响 task dispatch/order 语义；不等于业务层 Workflow Execution 顺序可被任意重排。 |
