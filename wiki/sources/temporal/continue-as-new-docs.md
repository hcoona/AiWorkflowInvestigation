---
schema_version: 2
page_type: source
title: "Temporal Continue-As-New 文档"
status: active
created: 2026-06-13
updated: 2026-06-13
summary: "Temporal Continue-As-New 官方文档的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - temporal
  - continue-as-new
  - workflow
---

## 来源边界

本页只投影 Temporal 的 Continue-As-New 文档。
它用于界定 Workflow 如何把最新相关状态传给新的 Workflow Execution，并用新的
Event History 继续运行。
原始材料未保存到 `raw/`；本页直接引用外部 URL 作为主证据。

## 可复用关键主张

- Continue-As-New 会 checkpoint Workflow 的状态并启动一个 fresh Workflow。
- 新 Workflow Execution 属于同一个 execution chain，
  使用相同 Workflow Id、不同 Run Id，并拥有新的 Event History。
- Continue-As-New 可用于避免过长 Event History，
  也可用于避免长运行 Workflow 卡在旧代码版本上。
- 该能力不是改写已有历史；
  更准确地说，它是在 run 边界把最新状态移交给新的 execution，
  因而可以承载受控 workflow 演进或计划修订。

## 限制与冲突

- Continue-As-New 不会原地修改当前 Workflow Execution 的历史。
- 新 execution 是否运行新代码或新计划，仍取决于已部署代码、版本策略和传入状态。
- 本页只解释 Continue-As-New；
  replay-safe 代码变更仍需结合 deterministic constraints、workflow versioning 和
  worker versioning source pages。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://docs.temporal.io/workflow-execution/continue-as-new` | Temporal Continue-As-New 官方文档；访问时间 2026-06-13。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| Continue-As-New 把最新相关状态传给新的 Workflow Execution，并创建 fresh Event History。 | 上方证据单元。 | 新 execution 仍属于 Temporal execution chain，不是原地改写当前 history。 |
| Continue-As-New 可用于长运行 Workflow 的受控演进，包括避免旧代码版本长期运行。 | 上方证据单元。 | 具体演进路径受部署、worker versioning 和 workflow code 约束。 |
