---
schema_version: 2
page_type: entity
title: "Dapr Workflow"
status: active
created: 2026-06-26
updated: 2026-06-26
summary: "Dapr Workflow 在本 wiki 中作为 Dapr-native sidecar/actor-backed durable workflow runtime 实体。"
maintenance:
  edit_policy: update
validation:
  body_contract: entity
tags:
  - workflow
  - dapr
  - durable-execution
---

## 身份

Dapr Workflow 是本 wiki 用于比较 Dapr-native durable orchestration 的产品级实体。
在当前证据边界内，它的关键身份不是“Dapr 全部 building blocks”，而是运行在
`daprd` sidecar 中、基于 Dapr Actors、actor state store、reminders 和 SDK
worker 协议的 workflow runtime。

本页聚焦 Dapr Workflow 的 workflow/runtime 语义。
Dapr service invocation、pub/sub、bindings、secrets、configuration、Jobs API
和其他 Dapr building blocks 不在当前实体边界内。

## 关系与时间线

| 关系 | 当前 wiki 判断 |
| --- | --- |
| 控制表示面 | Dapr Workflow 通过 SDK workflow 函数表达 durable control flow。 |
| 执行与恢复语义 | 核心模式是 event-sourced history、deterministic replay 和 actor reminders 恢复。 |
| 副作用边界 | Activity 是承载外部 I/O 和真实世界副作用的主要边界。 |
| 时间与触发语义 | Durable timer 是 workflow 内部持久等待；external event 可恢复等待中的 workflow。 |
| 执行放置单元 | Workflow/activity 执行依赖 sidecar、SDK worker stream、actor placement 和 app ID 边界。 |
| 裸金属 buildout 选型 | 当前定位是次级、POC-only durable orchestration 候选；只有 Dapr control plane、state store、app-ID routing、payload/history、versioning 和 side-effect safety 通过 POC 后才进入主 baseline 对照。 |

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| wiki | [裸金属 Cluster Buildout 的 Process Manager 平台选型](../analyses/bare-metal-cluster-buildout-process-manager-selection.md) | 将 Dapr Workflow 纳入裸金属 buildout 主 process manager 候选比较，并定位为次级、POC-only durable orchestration 候选。 |
| wiki | [Dapr Workflow Overview 文档](../sources/dapr/workflow-overview-docs.md) | Dapr Workflow 的总体定位、多语言 SDK 和 management 操作入口。 |
| wiki | [Dapr Workflow Features and Concepts 文档](../sources/dapr/workflow-features-concepts-docs.md) | Event-sourced replay、activity、timer、external event、child workflow、retry、determinism、Continue-as-new 和 payload/history 边界。 |
| wiki | [Dapr Workflow Architecture 文档](../sources/dapr/workflow-architecture-docs.md) | Sidecar、Actors、actor state store、workflow history/inbox、reminders、placement、scaling 和 retention 边界。 |
| wiki | [Dapr Multi-Application Workflows 文档](../sources/dapr/workflow-multi-app-docs.md) | 跨 app ID 调度 activity/child workflow 及 namespace/state store/app registration 限制。 |
| wiki | [Dapr Workflow Versioning 文档](../sources/dapr/workflow-versioning-docs.md) | Patching、named workflow versioning、stalled workflow 和旧版本保留边界。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| Dapr Workflow 在当前比较中代表 Dapr-native sidecar/actor-backed durable workflow runtime。 | Dapr Overview、Architecture、Features and Concepts source pages。 | 这是 Dapr Workflow 子系统边界，不覆盖 Dapr 全部 runtime/building blocks。 |
| Dapr Workflow 具备 durable orchestration 关键机制：workflow instance、history/replay、activity、timer、external event、child workflow、retry 和 management operations。 | Dapr Overview、Features and Concepts source pages。 | 这些机制不自动满足裸金属资源事实层、业务 command gateway、dashboard 或物理副作用安全。 |
| Dapr Workflow 的 buildout 选型定位是次级、POC-only durable orchestration 候选。 | 裸金属 buildout 选型分析；Dapr Architecture、Multi-Application Workflows、Versioning source pages。 | 该定位依赖当前证据和未完成 POC；若目标组织已标准化 Dapr 并通过 state store、routing、versioning、observability 和 side-effect safety 验证，应重新评估。 |
