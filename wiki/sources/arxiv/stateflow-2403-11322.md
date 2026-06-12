---
schema_version: 2
page_type: source
title: "arXiv 2403.11322 StateFlow"
status: active
created: 2026-06-12
updated: 2026-06-12
summary: "StateFlow 状态驱动 LLM workflow 论文的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - arxiv
  - stateflow
  - state-machine
  - agent-workflow
---

## 来源边界

本页只投影 arXiv:2403.11322
`StateFlow: Enhancing LLM Task-Solving through State-Driven Workflows`。
原始材料未保存到 `raw/`；本页直接引用 arXiv PDF 作为主证据。

## 可复用关键主张

- StateFlow 将复杂 LLM task-solving process 概念化为 state machine。
- StateFlow 区分 process grounding 和 sub-task solving：
  前者通过 state/state transitions 表达，后者通过 state 内 actions 表达。
- StateFlow 使用状态、初始状态、终止状态、transition function、messages
  和 output functions 建模运行过程。
- 该论文强调状态转移可由 heuristic rules 或 LLM decisions 控制。

## 限制与冲突

- StateFlow 是研究框架，不是通用 workflow engine。
- 实验结果来自特定 benchmark；不应直接外推到所有 agent workflow 场景。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://arxiv.org/pdf/2403.11322` | arXiv:2403.11322；DeepXiv 访问时间 2026-06-12。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| StateFlow 将 LLM task-solving 建模为 state machine。 | 上方证据单元。 | 这是论文提出的框架，不是行业通用定义。 |
| StateFlow 明确分离 process control 和 state 内的 LLM/tool actions。 | 上方证据单元。 | 具体状态设计仍依赖任务理解和人工建模。 |
| StateFlow 的 transitions 可由规则或 LLM 判断控制。 | 上方证据单元。 | LLM 判断会引入不确定性，需要按任务治理。 |
