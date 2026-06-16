---
schema_version: 2
page_type: source
title: "Apache Airflow Deferrable Operators 文档"
status: active
created: 2026-06-16
updated: 2026-06-16
summary: "Apache Airflow deferrable operators 与 triggerer 等待语义的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - airflow
  - deferrable-operators
  - waiting
---

## 来源边界

本页只投影 Apache Airflow 的 Deferrable Operators 文档。
它用于界定 task/operator 如何 defer 到 trigger、deferred 时 worker slot 如何释放、
以及恢复时状态传递的限制。
原始材料未保存到 `raw/`；本页直接引用外部 URL 作为主证据。

## 可复用关键主张

- Deferrable operator 可在等待外部条件时调用 `self.defer(...)`，
  并由 trigger 负责等待。
- Operator deferred 后会停止执行并从 worker 移出；本地变量或实例属性不会自动持久化。
- Operator 恢复时会创建新的 operator instance；状态需要通过 resume method、
  kwargs 和 trigger event 等方式传递。
- Trigger 需要可序列化、异步运行，并应避免依赖持久状态或产生不可控副作用。

## 限制与冲突

- Deferrable operators 解决的是 task/operator 等待和 worker slot 占用问题，
  不等同于长期领域资源状态机。
- Trigger 设计仍有副作用、幂等和可序列化约束；不能把 trigger 当成任意外部事件总线。
- 本页不覆盖 HITL 专用 operator，也不覆盖 event-driven Dag scheduling。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://airflow.apache.org/docs/apache-airflow/stable/authoring-and-scheduling/deferring.html` | Apache Airflow Deferrable Operators 文档；访问时间 2026-06-16。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| Airflow 支持 operator 在等待时 defer，并释放当前 worker 执行位置。 | 上方证据单元。 | deferred task 仍属于 TaskInstance/DagRun 语义。 |
| Deferral 不自动持久化 operator 本地状态，恢复状态需要显式传递。 | 上方证据单元。 | 不排除 task 使用外部系统保存领域状态。 |
| Trigger 适合等待事件，但不应承载有副作用的长期领域状态机。 | 上方证据单元。 | 这是从 trigger 设计约束映射出的工程判断。 |
