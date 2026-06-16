---
schema_version: 2
page_type: source
title: "Apache Airflow Dag Run 文档"
status: active
created: 2026-06-16
updated: 2026-06-16
summary: "Apache Airflow DagRun 与 catchup 语义的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - airflow
  - dagrun
  - catchup
---

## 来源边界

本页只投影 Apache Airflow 的 Dag Run core concepts 文档。
它用于界定 scheduler 如何基于 Dag schedule/data interval 创建 DagRun，
以及 catchup 如何为未运行的数据区间创建 DagRun。
原始材料未保存到 `raw/`；本页直接引用外部 URL 作为主证据。

## 可复用关键主张

- 有 `start_date`、可选 `end_date` 和非 asset schedule 的 Dag 会定义一系列 intervals，
  scheduler 会将这些 intervals 转成独立 Dag runs 并执行。
- 默认配置下，scheduler activation 时只为最新 interval 创建 DagRun。
- 当 `catchup=True` 时，scheduler 会为自上次 data interval 以来尚未运行的数据区间创建 DagRun。
- Catchup 也会在 Dag 关闭一段时间后重新启用时触发。
- 如果 Dag 没有按数据区间安全处理 catchup，文档建议关闭 catchup。

## 限制与冲突

- DagRun/Catchup 是 schedule/data interval 维度的 DagRun 创建语义；
  不等同于长期资源状态机的事件解释、局部追平或物理副作用补偿。
- 对裸金属 buildout，catchup/backfill/reprocessing 可能触发真实副作用；
  是否安全必须由业务幂等、读回、锁和补偿设计证明。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dag-run.html` | Apache Airflow Dag Run core concepts 文档；访问时间 2026-06-16。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| Airflow scheduler 将 Dag 的 schedule/data intervals 转成 DagRun 并执行。 | 上方证据单元。 | 本页不覆盖 executor 运行 task 的细节。 |
| Airflow catchup 会为尚未运行的数据区间创建 DagRun。 | 上方证据单元。 | Catchup 语义不自动保证真实世界副作用重放安全。 |
