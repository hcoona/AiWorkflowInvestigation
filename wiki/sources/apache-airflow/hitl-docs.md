---
schema_version: 2
page_type: source
title: "Apache Airflow HITL 文档"
status: active
created: 2026-06-16
updated: 2026-06-16
summary: "Apache Airflow Human-in-the-loop operators 的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - airflow
  - hitl
  - human-approval
---

## 来源边界

本页只投影 Apache Airflow 的 HITLOperator tutorial 文档。
它用于界定 Airflow 如何在 DAG 中表达人工输入、选项选择、批准/拒绝、
分支选择和通知。
原始材料未保存到 `raw/`；本页直接引用外部 URL 作为主证据。

## 可复用关键主张

- Airflow HITL 功能允许 workflow 暂停并等待人工输入。
- HITL operators 可用于输入参数、选项选择、批准/拒绝和分支选择。
- 人工选择可以通过 XCom 等方式被后续 task 使用，并可影响 DAG 后续路径。
- Notifier 可在 HITL 事件发生时通知人类操作员，并生成指向 Airflow UI 的链接。

## 限制与冲突

- HITL 支撑的是 Airflow DAG/TaskInstance 内的人机交互；
  不等同于长期裸金属资源状态机的完整人工协作模型。
- 本页只投影 tutorial 文档；不同 Airflow 版本中的等待状态和实现细节应以对应版本文档为准。
- 人工输入如何进入外部 inventory/resource graph、审计系统和补偿流程，仍需业务设计。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://airflow.apache.org/docs/apache-airflow/stable/tutorial/hitl.html` | Apache Airflow HITLOperator tutorial；访问时间 2026-06-16。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| Airflow 支持在 DAG 中暂停并等待人工输入或审批。 | 上方证据单元。 | 这是 task/DAG 语义内的 HITL，不是任意领域事件入口。 |
| HITL 可影响后续 task 或分支选择。 | 上方证据单元。 | 具体分支和后续路径仍需 DAG 预先建模。 |
| HITL 可作为裸金属 buildout 中审批、确认和人工门禁的调度层能力。 | 上方证据单元。 | 领域事实和审计仍应落到外部系统或明确数据模型。 |
