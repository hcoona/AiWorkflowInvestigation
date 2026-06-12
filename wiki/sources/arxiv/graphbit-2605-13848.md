---
schema_version: 2
page_type: source
title: "arXiv 2605.13848 GraphBit"
status: active
created: 2026-06-12
updated: 2026-06-12
summary: "GraphBit 确定性图式 agent orchestration 论文的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - arxiv
  - graphbit
  - deterministic-orchestration
  - agent-workflow
---

## 来源边界

本页只投影 arXiv:2605.13848
`GraphBit: A Graph-based Agentic Framework for Non-Linear Agent Orchestration`。
原始材料未保存到 `raw/`；本页直接引用 arXiv PDF 作为主证据。

## 可复用关键主张

- GraphBit 将 workflows 显式定义为 typed directed acyclic graphs。
- GraphBit 使用 Rust-based execution engine 控制 routing、state transitions
  和 tool invocation。
- GraphBit 将 agents 表达为 typed functions，并让 control node decisions
  由执行引擎基于 structured state predicates 评估。
- GraphBit 的三层 memory architecture 包含 ephemeral scratch、structured state
  和 external connectors。

## 限制与冲突

- 该论文是预印本系统论文，性能和对比结论需要独立复现。
- GraphBit 的 deterministic engine 语义不等价于 Temporal 的 Event History/replay
  durability。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://arxiv.org/pdf/2605.13848` | arXiv:2605.13848；DeepXiv 访问时间 2026-06-12。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| GraphBit 用 typed DAG 表达 agent workflow。 | 上方证据单元。 | 这是一种研究系统设计，不是所有 agent framework 的共同语义。 |
| GraphBit 将 routing、state transitions 和 tool invocation 交给执行引擎控制。 | 上方证据单元。 | 不应等同于 Temporal 的 durable execution guarantee。 |
| GraphBit 用分层 memory architecture 控制 context 与 state。 | 上方证据单元。 | 该设计的通用性需要更多系统验证。 |
