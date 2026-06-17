---
schema_version: 2
page_type: source
title: "Claude Agent SDK Todo Tracking 文档"
status: active
created: 2026-06-17
updated: 2026-06-17
summary: "Claude Agent SDK todo/task tracking 官方文档的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - claude-code
  - todo-tracking
  - task-tracking
---

## 来源边界

本页只投影 Claude Agent SDK 的 Todo Lists / Task tools 文档。
它用于界定 Claude Code / Agent SDK 如何用结构化任务列表跟踪复杂任务进展。
原始材料未保存到 `raw/`；本页直接引用外部 URL 作为主证据。

## 可复用关键主张

- Todo/task tracking 为复杂 workflow 提供结构化任务管理和进度展示。
- 文档描述 task 生命周期：created/pending、in_progress、completed、removed。
- 新版本将单次重写 todo array 的 `TodoWrite` 迁移为 `TaskCreate`、`TaskUpdate`、
  `TaskGet`、`TaskList` 等结构化任务工具。
- Task tools 以创建、更新和读取任务状态的方式维护计划状态；这更接近受控 plan/task
  patch，而不是任意修改运行中 workflow topology。

## 限制与冲突

- 本页是 Claude Agent SDK 的任务跟踪机制投影，不说明所有 Claude Code 内部计划策略。
- Todo/task tracking 是 agent session/task 管理面，不是 durable workflow runtime。
- 任务列表可动态变化，但文档没有把它定义为任意业务工作流图的拓扑迁移机制。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://code.claude.com/docs/en/agent-sdk/todo-tracking.md` | Claude Agent SDK todo/task tracking 官方文档；访问时间 2026-06-17。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| Claude Agent SDK 用结构化 task/todo 状态跟踪复杂任务进展。 | 上方证据单元。 | 这是 agent session 管理机制，不是业务领域事实层。 |
| 任务更新更接近受控 plan/task patch，而不是运行中 workflow topology 任意自修改。 | 上方证据单元。 | 该解释是本 wiki 的机制映射，不是 Claude 文档原文术语。 |
