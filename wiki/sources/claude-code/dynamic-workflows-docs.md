---
schema_version: 2
page_type: source
title: "Claude Code Dynamic Workflows 文档"
status: active
created: 2026-06-17
updated: 2026-06-17
summary: "Claude Code dynamic workflows 官方文档的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - claude-code
  - dynamic-workflows
  - agent-workflow
---

## 来源边界

本页只投影 Claude Code 官方 dynamic workflows 文档。
它用于界定 Claude Code 中 dynamic workflow 的计划持有者、运行方式和适用场景。
原始材料未保存到 `raw/`；本页直接引用外部 URL 作为主证据。

## 可复用关键主张

- Claude Code dynamic workflow 是由 JavaScript script 编排多个 subagents 的机制。
- 文档明确区分 subagents、skills、agent teams 和 workflows；workflow 的计划由 script
  持有，而不是由 Claude 在每个 turn 中临时决定。
- Dynamic workflows 适合 codebase-wide audit、大规模 migration、cross-checked research
  等需要多 agent、多阶段或可复用 orchestration 的任务。
- Claude 可以为任务生成 workflow script；运行前可查看和批准计划，成功后可保存为可复用命令。

## 限制与冲突

- 本页只投影 Claude Code 产品文档，不代表所有 agent workflow 论文或框架实践。
- Claude Code dynamic workflows 面向软件工程 agent 编排，不直接证明裸金属 buildout
  process manager 的 runtime 选型。
- “dynamic” 在此处主要表示 workflow script 可由 Claude 生成并可按任务运行；
  不表示运行中的 durable workflow topology 可由 agent 任意自修改。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://code.claude.com/docs/en/workflows` | Claude Code dynamic workflows 官方文档；访问时间 2026-06-17。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| Claude Code dynamic workflow 把 orchestration plan 放入可执行 script，而不是让一个 agent 在每个 turn 中自由临时决定所有后续步骤。 | 上方证据单元。 | 文档仍允许 Claude 生成该 script；这不是静态人工手写流程的唯一形态。 |
| Claude Code dynamic workflows 用于多 subagent、大规模、可复用和可交叉验证的任务。 | 上方证据单元。 | 不直接等同于生产业务 process manager。 |
