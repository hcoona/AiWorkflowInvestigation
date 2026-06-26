---
schema_version: 2
page_type: source
title: "Dapr Workflow Features and Concepts 文档"
status: active
created: 2026-06-26
updated: 2026-06-26
summary: "Dapr Workflow replay、activity、timer、external event、retry 与 determinism 语义的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - dapr
  - workflow
  - replay
  - external-events
---

## 来源边界

本页只投影 Dapr 官方 Workflow features and concepts 文档。
它用于界定 Dapr Workflow 的 workflow 函数、event sourcing/replay、
activity、durable timer、child workflow、external event、retry、
determinism 和 payload/versioning 相关边界。
原始材料未保存到 `raw/`；本页直接引用外部 URL 作为主证据。

## 可复用关键主张

- Dapr Workflow 使用 event-sourced history 和 deterministic replay；
  workflow 代码从头重放，并用历史事件恢复已完成任务结果。
- Activity 是外部工作和副作用边界，执行语义要求业务设计考虑幂等性。
- Durable timer、external event waiter、child workflow 和 retry policy
  是 workflow 函数可调度的主要持久任务类型。
- External event 以事件名和 payload 投递到指定 workflow instance；
  过早到达的事件会保存在 history 中，等待 workflow 后续消费。
- Workflow code 必须遵守 deterministic constraints；
  非确定性 I/O、随机数、当前时间和直接外部状态访问应放在 activity 或外部服务中。
- Continue-as-new 可在保留必要输入/状态的同时开启新的 execution generation，
  用于控制长期 workflow history 增长。
- Payload 和 history 规模会影响 workflow dispatch；
  大对象应通过外部引用而不是直接写入 workflow history。

## 限制与冲突

- 本来源描述的是 Dapr Workflow runtime 语义；
  不覆盖 sidecar、actors、state store、placement、scheduler 或 multi-app routing。
- Durable retry 和 replay 不是 exactly-once 物理副作用保证；
  裸金属设备操作仍需幂等键、读后校验、外部锁和补偿。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://docs.dapr.io/developing-applications/building-blocks/workflow/workflow-features-concepts/` | Dapr Workflow features and concepts 官方文档；访问时间 2026-06-26。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| Dapr Workflow 在执行语义上属于 durable orchestration：history/replay、durable timer、external event、child workflow 和 retry 都是一手机制。 | 上方证据单元。 | 该语义接近 Temporal/Azure Durable 的执行模型，但不等于产品、routing、visibility 或运维成熟度等价。 |
| Dapr Workflow 的 activity/replay 语义要求真实副作用由业务幂等、读回、锁和补偿保护。 | 上方证据单元。 | 文档机制不自动理解裸金属设备状态，也不提供物理操作 exactly-once 保证。 |
| Dapr Workflow 可用 Continue-as-new 控制长期 history 增长。 | 上方证据单元。 | Continue-as-new 是 workflow history/状态交接机制，不是物理副作用回滚或任意拓扑迁移。 |
