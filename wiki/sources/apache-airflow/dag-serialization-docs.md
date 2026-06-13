---
schema_version: 2
page_type: source
title: "Apache Airflow DAG Serialization 文档"
status: active
created: 2026-06-13
updated: 2026-06-13
summary: "Apache Airflow DAG Serialization 官方文档的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - airflow
  - dag-serialization
  - scheduler
---

## 来源边界

本页只投影 Apache Airflow 的 DAG Serialization 文档。
它用于说明 scheduler 如何使用 serialized DAG，以及 Airflow 3.1
中序列化契约如何支持 server/client decoupling。
原始材料未保存到 `raw/`；本页直接引用外部 URL 作为主证据。

## 可复用关键主张

- Airflow 2.0 起 scheduler 使用 serialized DAG 做 scheduling decisions。
- DagFileProcessorProcess 解析 DAG 文件，将 JSON serialized DAG 保存到 metadata
  DB。
- Airflow 3.1 的 serialization contract 支持 Task SDK 与 server components
  独立部署和版本兼容。
- DAG serialization 是 scheduler 控制视图和部署兼容能力，
  不等于 task/agent 在 current DagRun 内任意改写 DAG definition。

## 限制与冲突

- 本页解释 serialized DAG 的文档语义，不覆盖 `DagRun.verify_integrity`
  源码细节。
- Airflow 3.1 的 client/server decoupling
  仍在演进中，文档说明架构支持不等于全部组件已完全解耦。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://airflow.apache.org/docs/apache-airflow/stable/administration-and-deployment/dag-serialization.html` | Apache Airflow DAG Serialization 文档；访问时间 2026-06-13。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| Airflow scheduler 使用 serialized DAG 做 scheduling decisions。 | 上方证据单元。 | 实际调度仍受 scheduler、executor 和 metadata DB 状态影响。 |
| DAG serialization 支持部署和版本兼容边界，不等于 current DagRun 内任意 topology mutation。 | 上方证据单元。 | 需要结合 DAG bundles、DagRun 和 task instance 行为理解。 |
