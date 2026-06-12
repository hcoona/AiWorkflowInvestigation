---
schema_version: 2
page_type: source
title: "Apache Airflow 工作流文档投影"
status: superseded
created: 2026-06-12
updated: 2026-06-12
summary: "已被更细粒度的 Airflow 单来源投影页取代。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - airflow
  - dag
  - agentic-workloads
  - ai-provider
---

> [!WARNING] 已被取代
> 本页已被 [Airflow DAG 文档](apache-airflow-dags-docs.md)、
> [Airflow Dynamic Task Mapping 文档](apache-airflow-dynamic-task-mapping-docs.md)、
> [Airflow Asset Scheduling 文档](apache-airflow-asset-scheduling-docs.md)、
> [Airflow Common AI Provider 博客](apache-airflow-common-ai-provider-blog.md)
> 和 [Airflow Agentic Workloads 博客](apache-airflow-agentic-workloads-blog.md)
> 取代。
> 原因：source page 应投影一个主要上游证据对象，不能把多个独立外链聚合为 n:
> 1 证据锚点。 取代日期：2026-06-12。
> 除修复该提示、链接或证据链外，不要继续更新本页。

## 来源边界

本页汇总 Apache Airflow 的 DAG、Dynamic Task Mapping、Asset Scheduling
文档，以及 Common AI Provider 和 Agentic Workloads 两篇官方博客。
Airflow 的关键信息不在于“有没有 LLM”，而在于它仍然是 DAG/task graph-centric
的编排器，只是借由动态映射、资产调度和 AI provider 把更多工作负载纳入同一套 task
语义。

## 可复用关键主张

- DAG 抽象把 schedule、tasks、dependencies、callbacks
  与其他运行细节组合为一个可执行工作流。
- Dynamic Task Mapping
  把任务创建推迟到运行时，支持基于上游输出动态展开任务数量。
- Asset-aware scheduling 让 DAG 可以由资产更新触发，而不仅仅依赖时间表。
- Common AI Provider 把 LLM/agent 能力、toolsets、HITL 和 durable execution 嵌入
  Airflow；但它仍然是在 DAG/task graph 之内扩展能力，而不是把 Airflow 改造成独立
  agent runtime。

## 限制与冲突

- `apache-airflow-providers-common-ai` 是快速演进的增强层；版本兼容性与 API
  细节应以对应发布说明为准。
- `@task.agent` 与 related operator 只是增强了现有 DAG 语义，没有改变 Airflow
  的核心控制抽象。
- Agentic workloads 博文展示的是显式 fan-out/fan-in task graph，而不是隐藏在单个
  reasoning loop 里的黑箱执行。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dags.html` | DAG、schedule、tasks 与 dependencies 的核心语义；访问时间 2026-06-12。 |
| external | `https://airflow.apache.org/docs/apache-airflow/stable/authoring-and-scheduling/dynamic-task-mapping.html` | 动态任务映射在运行时展开任务；访问时间 2026-06-12。 |
| external | `https://airflow.apache.org/docs/apache-airflow/stable/authoring-and-scheduling/asset-scheduling.html` | 资产更新触发 DAG 的调度语义；访问时间 2026-06-12。 |
| external | `https://airflow.apache.org/blog/common-ai-provider/` | Common AI Provider、LLM/agent operators、toolsets 与 durable execution；访问时间 2026-06-12。 |
| external | `https://airflow.apache.org/blog/agentic-workloads-airflow-3/` | 以 Dynamic Task Mapping + common.ai 形成显式 fan-out/fan-in pipeline；访问时间 2026-06-12。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| Airflow 的核心抽象仍是 DAG/task graph，负责 schedule、task 依赖与执行顺序。 | 上方证据单元 1。 | DAG 语义比数学 DAG 更宽，但核心仍是编排图。 |
| Dynamic Task Mapping 与 asset scheduling 扩展了 runtime adaptation，但仍保持 task graph 语义。 | 上方证据单元 2、3。 | 动态任务仍由 scheduler 作为 task 处理，不是隐藏 reasoning loop。 |
| Common AI Provider 把 agentic 用法纳入 Airflow，但它仍不是 LangGraph/MAF 风格的独立 agent runtime。 | 上方证据单元 4、5。 | provider 与示例属于增强层，不应误读为核心语义已整体转向 agent runtime。 |
