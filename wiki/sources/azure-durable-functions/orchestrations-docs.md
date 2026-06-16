---
schema_version: 2
page_type: source
title: "Durable Task Orchestrations 文档"
status: active
created: 2026-06-16
updated: 2026-06-16
summary: "Durable orchestrations、instance identity、event sourcing 和 replay 语义的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - azure-durable-functions
  - durable-task
  - orchestration
---

## 来源边界

本页只投影 Microsoft Learn 的 Durable Orchestrations overview 文档。
它用于界定 orchestrator function、long-running workflow、orchestration instance
identity、event sourcing、execution history、checkpoint/replay、sub-orchestrations、
durable timers 和 error handling 的语义。
原始材料未保存到 `raw/`；本页直接引用外部 URL 作为主证据。

## 可复用关键主张

- Durable orchestration 使用 orchestrator function 协调其它 functions，
  以代码定义 reliable、long-running workflow。
- Orchestration instance 可以有 instance ID；
  用户生成 instance ID 适合一对一映射到外部应用实体。
- Durable Task Framework 使用 event sourcing 与 append-only execution history
  维护 orchestration state，并在 `await` / `yield` 等位置 checkpoint 进度。
- 当有响应消息或 timer 到期时，orchestrator 会从头 re-execute，
  并通过 execution history replay 已完成 activity 的结果。
- Durable orchestrations 支持 sub-orchestrations，用于把工作拆分到子
  orchestration instance 中。
- Orchestrator function code 必须 deterministic。

## 限制与冲突

- 本页支撑 Durable Task 的 durable orchestration 核心语义；
  不覆盖 Azure Functions hosting model、storage provider 取舍或业务 UI。
- Event sourcing/replay 维护 orchestration 控制状态；
  本来源不覆盖业务领域事实、锁、补偿或验收账本设计。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://learn.microsoft.com/en-us/azure/durable-task/common/durable-task-orchestrations` | Microsoft Learn Durable Orchestrations overview；访问时间 2026-06-16。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| Durable orchestration 可表达可靠、长期、代码定义的 orchestration instance。 | 上方证据单元。 | 不等于自动适配所有裸金属 buildout 运维约束。 |
| Durable Task 通过 event sourcing、execution history 和 replay 恢复 orchestrator local state。 | 上方证据单元。 | 本来源不覆盖真实外部副作用的幂等或补偿设计。 |
| Durable orchestration instance ID 可映射外部应用实体。 | 上方证据单元。 | 这只支撑实例身份；本来源不覆盖外部应用实体的数据模型。 |
| Durable orchestrations 支持 sub-orchestrations，可作为资源过程分区的候选建模锚点。 | 上方证据单元。 | 本页没有单独展开 sub-orchestration ID、版本、监控和局部追平策略。 |
