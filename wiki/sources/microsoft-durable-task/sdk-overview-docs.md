---
schema_version: 2
page_type: source
title: "Durable Task SDKs Overview 文档"
status: active
created: 2026-06-16
updated: 2026-06-16
summary: "Durable Task SDKs portable orchestration libraries 的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - microsoft-durable-task
  - sdk
  - durable-execution
---

## 来源边界

本页只投影 Microsoft Learn 的 Durable Task SDKs overview 文档。
它用于界定 standalone Durable Task SDKs 的 portable orchestration
定位、支持的 compute platforms、与 Durable Task Scheduler 的 backend 关系、
语言 SDK 状态，以及 orchestration/activity/entity/timer/external-event 等能力。
原始材料未保存到 `raw/`；本页直接引用外部 URL 作为主证据。

## 可复用关键主张

- Durable Task SDKs 是 portable、open-source libraries，
  可用普通代码构建 durable orchestrations、activities 和 entities。
- SDKs 可运行在 Azure Container Apps、Kubernetes 或 VMs 等任意 compute platform。
- 每个 SDK 连接 Durable Task Scheduler 作为 managed backend。
- .NET、Python、Java SDK 显示为 GA；JavaScript / TypeScript SDK 显示为 Preview。
- SDK feature comparison 支撑 orchestrations、activities、sub-orchestrations、
  durable timers、external events、durable entities、retry policies、
  continue-as-new 和 suspend/resume 等能力。

## 限制与冲突

- “任意 compute platform”描述的是 worker/app placement；
  state/backend 仍连接 Durable Task Scheduler managed backend。
- SDK 语言状态不同，目标语言选择会影响 PoC 风险。
- 本页不证明 Durable Task Scheduler 对 air-gapped 或完全自托管场景可用；
  backend、网络、私有连接和运营边界需另行验证。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://learn.microsoft.com/en-us/azure/durable-task/sdks/durable-task-overview` | Microsoft Learn Durable Task SDKs overview 文档；访问时间 2026-06-16。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| Standalone Durable Task SDKs 可在 Azure Functions 之外的 compute platform 上运行 durable orchestration workers。 | 上方证据单元。 | SDK 仍连接 Durable Task Scheduler managed backend；不是完全自带后端。 |
| Durable Task SDKs 支持 sub-orchestrations、durable timers、external events、durable entities、continue-as-new 和 suspend/resume 等核心 durable orchestration 能力。 | 上方证据单元。 | 具体语义、限制和成熟度随语言 SDK 与 backend 变化。 |
