---
schema_version: 2
page_type: overview
title: "LLM-Wiki 概览"
status: active
created: 2026-06-11
updated: 2026-06-11
summary: "本仓库 LLM-Wiki 知识库入口。"
maintenance:
  edit_policy: update
validation:
  body_contract: overview
tags:
  - llm-wiki
---

## 目的

本仓库已初始化为 LLM-Wiki：持久综合分析写入 `wiki/`，精选入库证据保存在 `raw/`，代理操作规则由根目录 [`AGENTS.md`](../AGENTS.md) 维护。

## 当前状态

知识库当前包含根级操作说明、起始模板、追加式日志、[`mise.toml`](../mise.toml) 中声明的可执行校验任务，以及 [`hk.pkl`](../hk.pkl) 中声明的 pre-commit 校验入口。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| user | 用户在 2026-06-11 针对粘贴的 "LLM-Wiki v2 Agent Instructions" 选择 "Integrate them into this repository"。 | 确立初始化请求和操作规则来源。 |
| repo | [`AGENTS.md`](../AGENTS.md)、[`mise.toml`](../mise.toml)、[`hk.pkl`](../hk.pkl) 和 `wiki/log.jsonl`。 | 记录权威说明、校验入口、pre-commit 钩子和持久初始化事件。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| 本仓库使用根目录 `AGENTS.md` 作为 LLM-Wiki 操作权威。 | 用户初始化请求；[`AGENTS.md`](../AGENTS.md)。 | 本页总结初始化状态；未来局部 `AGENTS.md` 可以收窄子树规则，但不能削弱根级权威。 |
| 持久 wiki 变更应使用 `mise run wiki-check` 校验，并在 pre-commit 时通过 hk 的 `check-wiki` 步骤自动执行。 | [`mise.toml`](../mise.toml)；[`hk.pkl`](../hk.pkl)；`wiki/log.jsonl`。 | 当前校验器覆盖 schema、日志、链接、正文证据和 hk pre-commit 入口；后续应随 wiki 工具演进。 |
