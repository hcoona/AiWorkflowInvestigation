---
schema_version: 2
page_type: source
title: "Durable Task Code Constraints 文档"
status: active
created: 2026-06-16
updated: 2026-06-16
summary: "Durable orchestrator replay 与 deterministic code constraints 的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - azure-durable-functions
  - durable-task
  - determinism
---

## 来源边界

本页只投影 Microsoft Learn 的 Durable orchestrator code constraints 文档。
它用于界定 Durable Functions / Durable Task SDK orchestrator replay 对代码确定性的约束，
以及时间、随机数、外部 I/O 等非确定性操作的边界。
原始材料未保存到 `raw/`；本页直接引用外部 URL 作为主证据。

## 可复用关键主张

- Orchestrator functions / orchestrators 使用 event sourcing 保证可靠执行并维护本地变量状态。
- Replay behavior 会约束 orchestrator code；orchestrator 必须 deterministic，
  多次 replay 必须产生相同结果。
- 非确定性 API 不能随意在 orchestrator 中使用；
  时间、随机 GUID/UUID 等需要使用 Durable Task 提供的 replay-safe API 或放入 activity。
- Code constraints 只约束 orchestrator；activity 等其它 function 类型没有同样限制。

## 限制与冲突

- 本页不表示 deterministic constraints 是缺陷；
  它们是 durable replay 模型的必要纪律。
- 外部 I/O、API 调用、文件/DB 操作等非确定性操作应放在 activity 或外部边界；
  本来源不覆盖业务幂等与补偿的具体设计。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://learn.microsoft.com/en-us/azure/durable-task/common/durable-task-code-constraints` | Microsoft Learn Durable orchestrator code constraints 文档；访问时间 2026-06-16。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| Durable orchestrator code 必须遵守 deterministic replay 约束。 | 上方证据单元。 | 具体 API 限制按语言 SDK 文档判断。 |
| 外部 I/O 和非确定性操作不应直接写入 orchestrator replay 路径。 | 上方证据单元。 | 本来源不覆盖 activity 内部业务幂等和补偿设计。 |
