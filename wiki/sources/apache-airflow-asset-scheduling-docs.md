---
schema_version: 2
page_type: source
title: "Apache Airflow Asset Scheduling 文档"
status: active
created: 2026-06-12
updated: 2026-06-12
summary: "Apache Airflow Asset-Aware Scheduling 文档的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - airflow
  - assets
  - scheduling
---

## 来源边界

本页只投影 Apache Airflow 的 Asset-Aware Scheduling 文档。
它用于说明 Airflow 可由资产更新驱动 DAG 调度。
原始材料未保存到 `raw/`；本页直接引用外部 URL 作为主证据。

## 可复用关键主张

- Airflow 支持以 asset 更新作为 DAG 运行触发条件。
- asset scheduling 扩展了 schedule 语义，使其不只依赖固定时间表。
- 资产更新可作为 DAG/DagRun 调度条件。

## 限制与冲突

- 本页不覆盖所有 Airflow event scheduling 机制，只记录 asset-aware scheduling。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://airflow.apache.org/docs/apache-airflow/stable/authoring-and-scheduling/asset-scheduling.html` | Apache Airflow Asset-Aware Scheduling 文档；访问时间 2026-06-12。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| Airflow 可以由资产更新触发 DAG。 | 上方证据单元。 | 本页只覆盖 asset-aware scheduling。 |
| Airflow 的 schedule 取向包含资产触发，而不只是 cron。 | 上方证据单元。 | 本页不评价 agent runtime 语义。 |
