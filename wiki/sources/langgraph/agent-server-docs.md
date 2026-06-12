---
schema_version: 2
page_type: source
title: "LangGraph Agent Server 文档"
status: active
created: 2026-06-12
updated: 2026-06-12
summary: "LangGraph Agent Server 官方文档的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - langgraph
  - agent-server
  - runtime-architecture
---

## 来源边界

本页只投影 LangGraph Agent Server 文档。
它用于说明 Agent Server 的 graph deployment、persistence、task queue、 runtime
architecture、queue worker 与 distributed runtime 边界。
原始材料未保存到 `raw/`；本页直接引用外部 URL 作为主证据。

## 可复用关键主张

- Agent Server 部署 graphs、persistence database 和 task queue。
- 普通 Agent Server runtime 中，client 创建 run 后，API server 入队，
  queue worker 获取 run、加载 graph 并开始 execution。
- queue worker 是 execution engine：它监听 durable task queue、执行 graph code
  并写入 checkpoints。
- split API and queue 模式把 API server 与 queue workers 分离，queue workers
  在独立 hosts 上处理 run execution。
- distributed runtime 把 graph orchestration 与 graph execution 拆到不同
  process； 这比普通 queue worker
  模式更细，但该文档没有把每个图节点描述为可由用户任意放置到 worker pool
  的一等调度单元。

## 限制与冲突

- 本页解释 Agent Server 文档层的 runtime
  architecture，不覆盖闭源平台内部实现细节。
- 本页使用“图节点”指 graph node；使用 “worker/process/host” 指计算放置位置，
  避免与图中的 node 混淆。
- 文档中的 task queue 是 run/job 层资源；不能仅凭该词推导为 Airflow TaskInstance
  或 Temporal Activity 等价物。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://docs.langchain.com/langsmith/agent-server` | LangGraph Agent Server 官方文档；访问时间 2026-06-12。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| Agent Server 将 graph、persistence database 和 task queue 一起部署。 | 上方证据单元。 | 具体托管形态可因 Cloud/self-hosted/standalone 配置不同。 |
| 普通 Agent Server 模式下，queue worker 获取 run、加载 graph、执行 graph code 并写 checkpoints。 | 上方证据单元。 | 这是 run-level execution 描述，不是图节点级 worker placement 保证。 |
| distributed runtime 拆分 orchestration process 与 execution process。 | 上方证据单元。 | 文档未证明用户可把每个图节点任意调度到不同 machine/host。 |
