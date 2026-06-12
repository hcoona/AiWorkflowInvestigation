---
schema_version: 2
page_type: source
title: "Apache Airflow DAG 文档"
status: active
created: 2026-06-12
updated: 2026-06-12
summary: "Apache Airflow DAG 核心概念文档的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - airflow
  - dag
  - orchestration
---

## 来源边界

本页只投影 Apache Airflow 的 DAG 核心概念文档。
它用于界定 Airflow workflow 的 DAG/task graph 语义。
原始材料未保存到 `raw/`；本页直接引用外部 URL 作为主证据。

## 可复用关键主张

- DAG 封装执行 workflow 所需的 tasks、dependencies、schedule 等运行细节。
- DAG 本身关注如何执行 tasks：schedule、dependencies、执行顺序、重试和超时等。
- DAG 运行时会实例化为 DagRun 和 TaskInstance 等调度对象。

## 限制与冲突

- Airflow 的 DAG 语义比数学 DAG 更宽，但仍是 task graph-centric。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dags.html` | Apache Airflow DAG 核心概念文档；访问时间 2026-06-12。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| Airflow workflow 的核心抽象是 DAG/task graph。 | 上方证据单元。 | 需要结合 dynamic mapping 与 asset scheduling 文档理解现代扩展。 |
| DAG 负责组织 schedule、tasks 和 dependencies。 | 上方证据单元。 | 本页不覆盖 executor 或 provider 实现细节。 |
