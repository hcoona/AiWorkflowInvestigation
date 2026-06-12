---
schema_version: 2
page_type: source
title: "Apache Airflow Common AI Provider 博客"
status: active
created: 2026-06-12
updated: 2026-06-12
summary: "Apache Airflow Common AI Provider 官方博客的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - airflow
  - ai-provider
  - agents
---

## 来源边界

本页只投影 Apache Airflow 官方博客 `Introducing Common AI Provider`。
它用于说明 Airflow common.ai provider 如何把 LLM/agent 能力放入 task 语义中。
原始材料已保存到
[`raw/02-apache-airflow/2026-04-14-common-ai-provider.md`](../../raw/02-apache-airflow/2026-04-14-common-ai-provider.md)；
本页使用该 raw 文件作为主证据。

## 可复用关键主张

- Common AI Provider 提供 LLM/agent operators 和 TaskFlow decorators。
- provider 能力嵌入 Airflow DAG/task graph，而不是替换 DAG 控制模型。
- provider 版本和 API 可能快速演进，选型时需要单独评估。

## 限制与冲突

- 这是 provider 层能力，不应直接解释为 Airflow 核心语义整体转向 agent runtime。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| raw | [`raw/02-apache-airflow/2026-04-14-common-ai-provider.md`](../../raw/02-apache-airflow/2026-04-14-common-ai-provider.md) | Apache Airflow Common AI Provider 官方博客正文原文。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| Airflow common.ai provider 把 LLM/agent 能力嵌入 task 体系。 | 上方证据单元。 | provider 层能力不等于核心 scheduler 语义被替换。 |
| common.ai provider 是快速演进的增强层。 | 上方证据单元。 | 具体稳定性需要查看对应版本发布说明。 |
