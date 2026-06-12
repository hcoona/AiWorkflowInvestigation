---
schema_version: 2
page_type: source
title: "arXiv 2605.22566 GraphFlow"
status: active
created: 2026-06-12
updated: 2026-06-12
summary: "GraphFlow LLM-agent serving workflow 管理论文的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - arxiv
  - graphflow
  - agent-serving
  - workflow-management
---

## 来源边界

本页只投影 arXiv:2605.22566
`GraphFlow: A Graph-Based Workflow Management for Efficient LLM-Agent Serving`。
原始材料未保存到 `raw/`；本页直接引用 arXiv PDF 作为主证据。

## 可复用关键主张

- GraphFlow 将 workflow repository 合并为统一 operation graph，即 wGraph。
- wGraph 节点表示 atomic operation，边表示 structural 或 functional dependency。
- GraphFlow 从 wGraph 动态实例化 task-specific workflows。
- GraphFlow 用 topology-aware state management 优化 KV cache/state reuse。

## 限制与冲突

- GraphFlow 关注 LLM-agent serving 的 workflow
  管理与性能优化，不是通用业务流程引擎。
- 论文性能结果来自特定 benchmark 和模型设置。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://arxiv.org/pdf/2605.22566` | arXiv:2605.22566；DeepXiv 访问时间 2026-06-12。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| GraphFlow 将 workflows 表示为共享 operation graph。 | 上方证据单元。 | 这是 serving 系统设计，不是所有 graph workflow 的通用机制。 |
| GraphFlow 动态生成 task-specific workflows。 | 上方证据单元。 | 生成质量取决于其 wGraph 和模型训练设置。 |
| GraphFlow 把 workflow topology 用于 KV cache/state management。 | 上方证据单元。 | 该优化主要服务于 LLM-agent serving 场景。 |
