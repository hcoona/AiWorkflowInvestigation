---
schema_version: 2
page_type: source
title: "Durable Task External Events 文档"
status: active
created: 2026-06-16
updated: 2026-06-16
summary: "Durable orchestrations external events 的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - azure-durable-functions
  - durable-task
  - external-events
---

## 来源边界

本页只投影 Microsoft Learn 的 Durable Task external events 文档。
它用于界定 running orchestrations 如何等待和接收 human approvals、webhook callbacks
或其它系统发来的 external events，以及 external events 的单向异步限制。
原始材料未保存到 `raw/`；本页直接引用外部 URL 作为主证据。

## 可复用关键主张

- External events 允许运行中的 orchestrations 接收外部来源信号，
  例如 human approvals、webhook callbacks 或其它系统。
- Orchestrator functions / orchestrations 可以异步等待和监听 external events。
- External events 是 one-way asynchronous operations；
  不适合发送事件的 client 需要 orchestrator 同步响应的场景。

## 限制与冲突

- External events 支撑事件注入；
  不等同于同步控制 API，也不自动提供业务事件模型、权限、审计或补偿。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://learn.microsoft.com/en-us/azure/durable-task/common/durable-task-external-events` | Microsoft Learn Durable Task external events 文档；访问时间 2026-06-16。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| Durable orchestrations 可等待和接收外部事件。 | 上方证据单元。 | External events 是单向异步操作。 |
| External events 可支撑人工审批、webhook 回调和外部系统事件进入 orchestration。 | 上方证据单元。 | 业务事件解释、权限和审计不由本来源覆盖。 |
