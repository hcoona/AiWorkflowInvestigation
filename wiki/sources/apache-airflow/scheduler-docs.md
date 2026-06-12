---
schema_version: 2
page_type: source
title: "Apache Airflow Scheduler 文档"
status: active
created: 2026-06-12
updated: 2026-06-12
summary: "Apache Airflow scheduler 官方文档的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - airflow
  - scheduler
  - task-instances
---

## 来源边界

本页只投影 Apache Airflow 的 scheduler 管理文档。
它用于界定 scheduler 如何监控 DAG 与 tasks、创建 DagRun、选择可调度
TaskInstance，并将其交给 executor 执行。
原始材料未保存到 `raw/`；本页直接引用外部 URL 作为主证据。

## 可复用关键主张

- Airflow scheduler 监控所有 tasks 和 DAGs，并在依赖完成后触发 task instances。
- scheduler 使用配置的 Executor 运行 ready tasks。
- scheduler 会基于 DAG 的 timetable 创建 DagRun。
- HA scheduler 使用 metadata database，并使用 serialized DAG representation
  做 scheduling decisions。
- scheduler loop 的粗略流程包括：创建需要的新 DagRun，检查一批 DagRun
  是否有可调度 TaskInstance 或可完成 DagRun，在 pool 与并发限制下选择可调度
  TaskInstance 并入队执行。

## 限制与冲突

- 本页解释 Airflow scheduler 的 task-instance 推进语义，不覆盖 executor
  内部如何运行具体 task。
- 本页不把 Airflow scheduler 与 Temporal Schedule 等同；
  前者推进 DAG/task-instance 状态，后者是启动 Workflow Execution 的外部规则。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://airflow.apache.org/docs/apache-airflow/stable/administration-and-deployment/scheduler.html` | Apache Airflow Scheduler 官方文档；访问时间 2026-06-12。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| Airflow scheduler 监控 DAG/task，并在依赖完成后触发 task instances。 | 上方证据单元。 | 实际执行由配置的 executor 负责。 |
| Airflow scheduler loop 会创建 DagRun、检查可调度 TaskInstance，并在 pool/concurrency 限制下入队执行。 | 上方证据单元。 | 文档描述的是粗略 loop；具体行为受配置、executor 和版本影响。 |
| Airflow scheduler 使用 serialized DAG representation 和 metadata database 做调度决策。 | 上方证据单元。 | HA scheduler 的数据库要求和锁语义与部署数据库有关。 |
