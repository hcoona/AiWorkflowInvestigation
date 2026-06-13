---
schema_version: 2
page_type: source
title: "Apache Airflow DAG Bundles 文档"
status: active
created: 2026-06-13
updated: 2026-06-13
summary: "Apache Airflow DAG Bundles 官方文档的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - airflow
  - dag-bundles
  - versioning
---

## 来源边界

本页只投影 Apache Airflow 的 DAG Bundles 文档。
它用于界定 DAG bundle versioning 如何影响 DagRun 使用的 DAG 代码版本。
原始材料未保存到 `raw/`；本页直接引用外部 URL 作为主证据。

## 可复用关键主张

- DAG bundle 是一个或多个 DAG 及其关联文件的集合。
- 支持 versioning 的 DAG bundle 可让 DagRun 在整个 run 中使用同一版本代码，
  即使 DAG 在 run 中途更新。
- Local/S3/GCS 等不支持 bundle versioning 的模式可能让任务使用 latest code。
- DAG bundle 是部署/解析层面的版本控制能力，不是 task 在运行中任意改写当前 DAG。

## 限制与冲突

- 不同 bundle 类型的 versioning 支持不同；
  引用时应说明是 versioned bundle 还是 latest-code bundle。
- 本页不覆盖 `DagRun.verify_integrity` 或 Dynamic Task Mapping。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://airflow.apache.org/docs/apache-airflow/stable/administration-and-deployment/dag-bundles.html` | Apache Airflow DAG Bundles 文档；访问时间 2026-06-13。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| Airflow DAG bundles 支持让 DagRun 使用特定 DAG bundle version。 | 上方证据单元。 | 不是所有 bundle 类型都支持 versioning。 |
| DAG bundle versioning 是部署层 workflow revision 能力，不是 current DagRun 内任意 topology mutation。 | 上方证据单元。 | latest-code bundle 的行为需要单独说明。 |
