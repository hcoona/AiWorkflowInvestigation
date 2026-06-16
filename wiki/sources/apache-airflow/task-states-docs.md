---
schema_version: 2
page_type: source
title: "Apache Airflow Task States 文档"
status: active
created: 2026-06-16
updated: 2026-06-16
summary: "Apache Airflow Task 与 TaskInstance 状态语义的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - airflow
  - task-instance
  - state
---

## 来源边界

本页只投影 Apache Airflow 的 Tasks core concept 文档。
它用于界定 Task、TaskInstance、依赖关系、TaskInstance 状态和 task heartbeat
timeout 等基础运行语义。
原始材料未保存到 `raw/`；本页直接引用外部 URL 作为主证据。

## 可复用关键主张

- Task 是 Airflow 的基本执行单元，组织在 DAG 中并由上下游依赖表达顺序。
- Dag 每次运行会把 Task 实例化为 TaskInstance；
  TaskInstance 是带状态的具体 task run。
- TaskInstance 状态包括 `scheduled`、`queued`、`running`、`success`、
  `failed`、`up_for_retry`、`up_for_reschedule`、`deferred`、`removed`
  等。
- Airflow 会处理 task instance heartbeat timeout，将卡在 `running` 的任务标为
  failed 或按 retry 策略处理。

## 限制与冲突

- TaskInstance 状态表达的是 Airflow task 生命周期；
  不能直接等同于裸金属节点、机架、BMC、固件或验收事实的领域状态。
- 文档中可见状态随版本演进；使用版本敏感状态时需要复核目标 Airflow 版本。
- XCom 和 TaskInstance metadata 可以承载部分运行数据，
  但不应被默认写成长期领域事实真源。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/tasks.html` | Apache Airflow Tasks core concept 文档；访问时间 2026-06-16。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| Airflow 的运行状态核心对象之一是 TaskInstance。 | 上方证据单元。 | DagRun 和 scheduler 语义还需结合 DAG/Scheduler source pages。 |
| TaskInstance 状态覆盖 task 生命周期、重试、reschedule、deferred 和 removed 等执行状态。 | 上方证据单元。 | 状态集合随版本可能变化。 |
| TaskInstance 状态不应直接替代裸金属资源领域状态。 | 上方证据单元。 | 这是场景映射；具体系统可把外部领域状态与 TaskInstance 关联。 |
