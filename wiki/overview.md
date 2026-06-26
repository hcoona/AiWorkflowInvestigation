---
schema_version: 2
page_type: overview
title: "LLM-Wiki 概览"
status: active
created: 2026-06-11
updated: 2026-06-26
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
[工作流概念比较](analyses/workflow-concepts-comparison.md)、
[Agent Orchestration 与传统 Workflow 的边界](analyses/agent-orchestration-vs-workflow.md)，
以及
[裸金属 Cluster Buildout 的 Process Manager 平台选型](analyses/bare-metal-cluster-buildout-process-manager-selection.md)
和
[Azure Functions 与 ASP.NET Core REST API 的边界](analyses/azure-functions-vs-aspnet-core-rest-api.md)，
以及
[Azure Durable Functions 与 MAF Durable Extension 的关系](analyses/azure-durable-functions-and-maf-durable-extension.md)，
以及
[MAF Durable Function Apps 与 Temporal 的 Scale-out 边界](analyses/maf-durable-functions-vs-temporal-scale-out.md)，
以及
[Temporal 与 MAF Durable Extension 的能力边界](analyses/temporal-vs-maf-durable-extension.md)，
并已将这些分析引用的外部证据拆成 one-source-object-per-page 的 source
projections。
workflow 相关分析现在也回补了 KG-style 概念页和产品级实体页，
用于承载跨问题复用的概念节点与系统身份。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| user | 用户在 2026-06-11 针对粘贴的 "LLM-Wiki v2 Agent Instructions" 选择 "Integrate them into this repository"。 | 确立初始化请求和操作规则来源。 |
| repo | [`AGENTS.md`](../AGENTS.md)、[`mise.toml`](../mise.toml)、[`hk.pkl`](../hk.pkl) 和 `wiki/log.jsonl`。 | 记录权威说明、校验入口、pre-commit 钩子和持久初始化事件。 |
| wiki | [工作流概念比较](analyses/workflow-concepts-comparison.md) | 当前 active analysis 示例，展示分析页如何引用单来源 source projections。 |
| wiki | [Agent Orchestration 与传统 Workflow 的边界](analyses/agent-orchestration-vs-workflow.md) | 当前 active analysis 示例，记录 agent orchestration 与传统 workflow 的控制权边界。 |
| wiki | [裸金属 Cluster Buildout 的 Process Manager 平台选型](analyses/bare-metal-cluster-buildout-process-manager-selection.md) | 当前 active analysis 示例，记录裸金属 buildout 场景中 Temporal、Azure Durable Functions、Dapr Workflow、Airflow 与 LangGraph 的主 process manager 选型边界。 |
| wiki | [Azure Functions 与 ASP.NET Core REST API 的边界](analyses/azure-functions-vs-aspnet-core-rest-api.md) | 当前 active analysis 示例，记录 Azure Functions HTTP trigger 与 ASP.NET Core REST API 在 HTTP 入口和应用模型上的边界。 |
| wiki | [Azure Durable Functions 与 MAF Durable Extension 的关系](analyses/azure-durable-functions-and-maf-durable-extension.md) | 当前 active analysis 示例，记录 Azure Durable Functions、Durable Task Scheduler 与 MAF Durable Extension 的分层关系。 |
| wiki | [MAF Durable Function Apps 与 Temporal 的 Scale-out 边界](analyses/maf-durable-functions-vs-temporal-scale-out.md) | 当前 active analysis 示例，记录多 graph、异构 workload 下 Function App hosting topology 与 Temporal Task Queue/Worker Process 模型的 scale-out 边界。 |
| wiki | [Temporal 与 MAF Durable Extension 的能力边界](analyses/temporal-vs-maf-durable-extension.md) | 当前 active analysis 示例，基于 raw/git 源码比较 Temporal 与启用 Durable Extension 的 MAF 在控制解释器、状态、调度、外部交互、长运行治理和 agent-first 抽象上的能力边界。 |
| wiki | [工作流控制表示面](concepts/workflow-control-representation-surface.md)、[工作流执行放置单元](concepts/workflow-execution-placement-unit.md)、[工作流恢复模型](concepts/workflow-recovery-model.md)、[工作流副作用边界](concepts/workflow-side-effect-boundary.md)、[工作流时间与触发语义](concepts/workflow-time-trigger-semantics.md)、[图工作流 Super-step](concepts/graph-workflow-super-step.md) | 当前 KG-style concept page 示例，展示 analysis 中可复用概念节点的拆分边界。 |
| wiki | [Temporal](entities/temporal.md)、[Dapr Workflow](entities/dapr-workflow.md)、[Apache Airflow](entities/apache-airflow.md)、[Microsoft Agent Framework](entities/microsoft-agent-framework.md)、[LangGraph](entities/langgraph.md) | 当前 entity page 示例，展示产品级实体页的检索边界。 |
| wiki | [Temporal Workflows 文档](sources/temporal/workflows-docs.md)、[Airflow DAG 文档](sources/apache-airflow/dags-docs.md)、[Microsoft Agent Framework Overview 文档](sources/microsoft-agent-framework/overview-docs.md)、[LangGraph Overview 文档](sources/langgraph/overview-docs.md) | 当前 source projection 粒度示例；每页投影一个主要上游证据对象。 |
| wiki | [Temporal Child Workflows 文档](sources/temporal/child-workflows-docs.md)、[Durable Task Orchestrations 文档](sources/azure-durable-functions/orchestrations-docs.md)、[Dapr Workflow Architecture 文档](sources/dapr/workflow-architecture-docs.md)、[Airflow Deferrable Operators 文档](sources/apache-airflow/deferrable-operators-docs.md)、[LangGraph Persistence 文档](sources/langgraph/persistence-docs.md)、[DMTF Redfish Standards 页面](sources/dmtf/redfish-standards-page.md)、[OpenStack Ironic README](sources/openstack/ironic-readme.md)、[Slurm Overview 文档](sources/slurm/overview-docs.md) | 裸金属 buildout 选型分析新增的 source projection 示例，覆盖 durable orchestration、Dapr sidecar/actor architecture、等待/事件/人工输入、agent graph persistence 和下层裸金属控制面。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| 本仓库使用根目录 `AGENTS.md` 作为 LLM-Wiki 操作权威。 | 用户初始化请求；[`AGENTS.md`](../AGENTS.md)。 | 本页总结初始化状态；未来局部 `AGENTS.md` 可以收窄子树规则，但不能削弱根级权威。 |
| 持久 wiki 变更应使用 `mise run wiki-check` 校验，并在 pre-commit 时通过 hk 的 `check-wiki` 步骤自动执行。 | [`mise.toml`](../mise.toml)；[`hk.pkl`](../hk.pkl)；`wiki/log.jsonl`。 | 当前校验器覆盖 wiki schema、日志、链接和正文证据结构；`hk.pkl` 的 `check-wiki` 步骤会调用 `mise run wiki-check`。 |
| 当前 wiki 已包含 workflow 概念比较分析、agent orchestration 与传统 workflow 的边界分析，以及裸金属 buildout process manager 选型分析，并采用单一上游证据对象粒度的 source projections。 | [工作流概念比较](analyses/workflow-concepts-comparison.md)；[Agent Orchestration 与传统 Workflow 的边界](analyses/agent-orchestration-vs-workflow.md)；[裸金属 Cluster Buildout 的 Process Manager 平台选型](analyses/bare-metal-cluster-buildout-process-manager-selection.md)；上方 source projection 示例。 | 本页只列入口示例，不维护完整页面索引。 |
| 当前 workflow synthesis 已回补 KG-style 概念页和产品级实体页，并将图工作流 Super-step 作为非显然领域名词单独成页。 | 上方 concept/entity page 示例；[工作流概念比较](analyses/workflow-concepts-comparison.md)。 | 组件级实体、执行解释器、状态真源、deterministic replay 等更细粒度候选仍按独立检索价值 deferred。 |
| 裸金属 buildout 选型分析将 AI 调研草稿降权为线索，技术事实由 Temporal、Azure Durable Functions、Dapr Workflow、Airflow、LangGraph 和裸金属控制面的一手 source projections 支撑。 | [裸金属 Cluster Buildout 的 Process Manager 平台选型](analyses/bare-metal-cluster-buildout-process-manager-selection.md)；上方裸金属 buildout source projection 示例。 | 本页不重复该分析的决策内容；具体条件、限制和 POC 边界见分析页。 |
| Azure Functions 与 ASP.NET Core REST API 的边界分析将 HTTP trigger 视为薄入口/事件触发模型，将 ASP.NET Core 视为完整 Web API 应用模型。 | [Azure Functions 与 ASP.NET Core REST API 的边界](analyses/azure-functions-vs-aspnet-core-rest-api.md)。 | 本页只作为入口导航；具体证据和限制见分析页。 |
| Azure Durable Functions 与 MAF Durable Extension 的关系分析将 MAF workflow 视为作者/业务语义层本体，将 Durable Task orchestration 视为运行时持久化映射，并把 Durable Task Scheduler 限定为 backend。 | [Azure Durable Functions 与 MAF Durable Extension 的关系](analyses/azure-durable-functions-and-maf-durable-extension.md)。 | 本页只作为入口导航；具体证据和限制见分析页。 |
| MAF Durable Function Apps 与 Temporal 的 scale-out 边界分析将逻辑子图区分于 runtime partition，并将资源利用差异定位到 Function App hosting topology 与 Temporal Task Queue/Worker Process 模型的 dispatch/resource-pool 粒度。 | [MAF Durable Function Apps 与 Temporal 的 Scale-out 边界](analyses/maf-durable-functions-vs-temporal-scale-out.md)。 | 本页只作为入口导航；具体证据和限制见分析页。 |
| Temporal 与 MAF Durable Extension 的能力边界分析将 Temporal 归为 Event History / Task Queue / Worker command runtime，将 MAF Durable Extension 归为 MAF graph/agent surface 到 Durable Task primitives 的 durable adapter。 | [Temporal 与 MAF Durable Extension 的能力边界](analyses/temporal-vs-maf-durable-extension.md)。 | 本页只作为入口导航；具体源码证据、反方限制和适用条件见分析页。 |
