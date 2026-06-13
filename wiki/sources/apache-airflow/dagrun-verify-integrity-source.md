---
schema_version: 2
page_type: source
title: "Apache Airflow DagRun verify_integrity 源码"
status: active
created: 2026-06-13
updated: 2026-06-13
summary: "Apache Airflow DagRun verify_integrity 源码的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - airflow
  - dagrun
  - source
---

## 来源边界

本页只投影 Apache Airflow `dagrun.py` 中 `DagRun.verify_integrity` 相关源码。
它用于界定 Airflow 对既有 DagRun 中 task instances 的受控 reconciliation。
原始材料未保存到 `raw/`；本页直接引用 GitHub source URL 作为主证据。

## 可复用关键主张

- `verify_integrity` 可为 DAG 中出现但 DagRun 中缺失的 task 创建 task instance。
- 该逻辑也会处理 task 从 DAG 中消失时的 removed 状态，
  但是否标记 removed 受到 DagRun 状态和 partial DAG 等条件限制。
- 这是既有 DagRun 与当前 DAG 视图之间的受控 reconciliation，
  不是 task/agent 任意改写 DAG topology。

## 限制与冲突

- 本页引用 main 分支源码，具体版本可能与部署版本不同。
- `verify_integrity` 的行为需要结合 DagVersion、bundle versioning 和
  clear/backfill 语义理解。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://github.com/apache/airflow/blob/main/airflow-core/src/airflow/models/dagrun.py#L1662-L1789` | Apache Airflow `DagRun.verify_integrity` 源码；访问时间 2026-06-13。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| Airflow 可对 DagRun task instances 做受控 reconciliation。 | 上方证据单元。 | 条件和版本行为需按具体源码版本核对。 |
| `verify_integrity` 不等于运行中任意 DAG topology mutation。 | 上方证据单元。 | 它操作的是 task instances 与 DAG 视图的一致性。 |
