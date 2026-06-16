---
schema_version: 2
page_type: source
title: "Apache Airflow Backfill 文档"
status: active
created: 2026-06-16
updated: 2026-06-16
summary: "Apache Airflow backfill 创建历史区间 DagRun 与重处理语义的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - airflow
  - backfill
  - dagrun
---

## 来源边界

本页只投影 Apache Airflow 的 Backfill 文档。
它用于界定 Airflow backfill 如何基于 Dag、start date、end date 和 schedule
创建历史区间 DagRun，以及 reprocessing behavior、concurrency、run ordering
和 dry run 的边界。
原始材料未保存到 `raw/`；本页直接引用外部 URL 作为主证据。

## 可复用关键主张

- Backfill 会为 Dag 的过去日期范围创建 DagRun。
- Backfill 可通过 CLI 和 REST API 创建，并需要 Dag、start date 和 end date。
- Backfill 根据 Dag schedule 在指定范围内创建 runs。
- Reprocessing behavior 包括 `none`、`failed` 和 `completed` 等选项。
- 如果最新 run 仍在 running 或 queued，backfill 不会为该 logical date 创建另一个 run。
- Backfill `max_active_runs` 独立控制 backfill 并发。

## 限制与冲突

- Backfill 面向有 time-based schedule 的 Dag；
  文档明确说对没有 time-based schedule 的 Dag 没有意义。
- Backfill 创建的是 DagRun；不等同于长期资源过程对象的任意状态迁移或物理回滚。
- Backfill 可作为历史区间重处理工具；
  对裸金属 buildout 的副作用重放安全仍需业务层验证和保护。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/backfill.html` | Apache Airflow Backfill 文档；访问时间 2026-06-16。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| Airflow backfill 为 Dag 的历史日期范围创建 DagRun，并按 schedule 创建 runs。 | 上方证据单元。 | 只适用于有 time-based schedule 的 Dag。 |
| Airflow backfill 提供重处理行为和并发控制。 | 上方证据单元。 | 这是 DagRun 重处理语义，不是外部物理副作用的安全重放保证。 |
