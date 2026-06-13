---
schema_version: 2
page_type: source
title: "Apache Airflow Dynamic DAG Generation 文档"
status: active
created: 2026-06-13
updated: 2026-06-13
summary: "Apache Airflow dynamic DAG generation 官方文档的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - airflow
  - dynamic-dag-generation
  - dag
---

## 来源边界

本页只投影 Apache Airflow 的 Dynamic DAG Generation 文档。
它用于界定解析期动态生成 DAG 与运行期 Dynamic Task Mapping 的差别。
原始材料未保存到 `raw/`；本页直接引用外部 URL 作为主证据。

## 可复用关键主张

- Dynamic DAG Generation 允许用 Python 代码生成 DAG structure。
- 官方文档把这种机制和 Dynamic Task Mapping 区分开：
  如果任务数量在不同 DagRun 中不应变化，可用动态 DAG 生成；
  如果任务数量需要基于上游输出变化，应使用 Dynamic Task Mapping。
- 该能力属于解析期/authoring 侧动态生成，不等于运行中任意修改当前 DagRun 的 DAG
  topology。

## 限制与冲突

- 本页只投影 Dynamic DAG Generation，不覆盖 scheduler 的所有 DAG refresh 行为。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://airflow.apache.org/docs/apache-airflow/stable/howto/dynamic-dag-generation.html` | Apache Airflow Dynamic DAG Generation 文档；访问时间 2026-06-13。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| Airflow Dynamic DAG Generation 是解析期生成 DAG structure 的能力。 | 上方证据单元。 | 它不是当前 DagRun 内任意插入 task 的机制。 |
| Airflow 文档将 Dynamic DAG Generation 与 Dynamic Task Mapping 分开。 | 上方证据单元。 | 二者都属于受控动态性，但发生层级不同。 |
