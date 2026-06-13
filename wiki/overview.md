---
schema_version: 2
page_type: overview
title: "LLM-Wiki 概览"
status: active
created: 2026-06-11
updated: 2026-06-12
summary: "本仓库 LLM-Wiki 知识库入口。"
maintenance:
  edit_policy: update
validation:
  body_contract: overview
tags:
  - llm-wiki
---

## 目的

本仓库已初始化为 LLM-Wiki：持久综合分析写入 `wiki/`，精选入库证据保存在
`raw/`，代理操作规则由根目录 [`AGENTS.md`](../AGENTS.md) 维护。

## 当前状态

知识库当前包含根级操作说明、起始模板、追加式日志、[`mise.toml`](../mise.toml)
中声明的可执行校验任务，以及 [`hk.pkl`](../hk.pkl) 中声明的 pre-commit
校验入口。
当前 active synthesis 包括
[工作流概念比较](analyses/workflow-concepts-comparison.md)，并已将该分析引用的外部证据拆成
one-source-object-per-page 的 source projections。
该分析现在也回补了 KG-style 概念页和产品级实体页，
用于承载跨问题复用的概念节点与系统身份。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| user | 用户在 2026-06-11 针对粘贴的 "LLM-Wiki v2 Agent Instructions" 选择 "Integrate them into this repository"。 | 确立初始化请求和操作规则来源。 |
| repo | [`AGENTS.md`](../AGENTS.md)、[`mise.toml`](../mise.toml)、[`hk.pkl`](../hk.pkl) 和 `wiki/log.jsonl`。 | 记录权威说明、校验入口、pre-commit 钩子和持久初始化事件。 |
| wiki | [工作流概念比较](analyses/workflow-concepts-comparison.md) | 当前 active analysis 示例，展示分析页如何引用单来源 source projections。 |
| wiki | [工作流控制表示面](concepts/workflow-control-representation-surface.md)、[工作流执行放置单元](concepts/workflow-execution-placement-unit.md)、[工作流恢复模型](concepts/workflow-recovery-model.md)、[工作流副作用边界](concepts/workflow-side-effect-boundary.md)、[工作流时间与触发语义](concepts/workflow-time-trigger-semantics.md) | 当前 KG-style concept page 示例，展示 analysis 中可复用概念节点的拆分边界。 |
| wiki | [Temporal](entities/temporal.md)、[Apache Airflow](entities/apache-airflow.md)、[Microsoft Agent Framework](entities/microsoft-agent-framework.md)、[LangGraph](entities/langgraph.md) | 当前 entity page 示例，展示产品级实体页的检索边界。 |
| wiki | [Temporal Workflows 文档](sources/temporal/workflows-docs.md)、[Airflow DAG 文档](sources/apache-airflow/dags-docs.md)、[Microsoft Agent Framework Overview 文档](sources/microsoft-agent-framework/overview-docs.md)、[LangGraph Overview 文档](sources/langgraph/overview-docs.md) | 当前 source projection 粒度示例；每页投影一个主要上游证据对象。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| 本仓库使用根目录 `AGENTS.md` 作为 LLM-Wiki 操作权威。 | 用户初始化请求；[`AGENTS.md`](../AGENTS.md)。 | 本页总结初始化状态；未来局部 `AGENTS.md` 可以收窄子树规则，但不能削弱根级权威。 |
| 持久 wiki 变更应使用 `mise run wiki-check` 校验，并在 pre-commit 时通过 hk 的 `check-wiki` 步骤自动执行。 | [`mise.toml`](../mise.toml)；[`hk.pkl`](../hk.pkl)；`wiki/log.jsonl`。 | 当前校验器覆盖 wiki schema、日志、链接和正文证据结构；`hk.pkl` 的 `check-wiki` 步骤会调用 `mise run wiki-check`。 |
| 当前 wiki 已包含一个 workflow 概念比较分析，并采用单一上游证据对象粒度的 source projections。 | [工作流概念比较](analyses/workflow-concepts-comparison.md)；上方 source projection 示例。 | 本页只列入口示例，不维护完整页面索引。 |
| 当前 workflow synthesis 已回补 KG-style 概念页和产品级实体页。 | 上方 concept/entity page 示例；[工作流概念比较](analyses/workflow-concepts-comparison.md)。 | 组件级实体、执行解释器和状态真源等更细粒度候选仍按独立检索价值 deferred。 |
