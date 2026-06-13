---
schema_version: 2
page_type: source
title: "Microsoft Agent Framework Python Workflow Runner 源码"
status: active
created: 2026-06-13
updated: 2026-06-13
summary: "Microsoft Agent Framework Python workflow runner 源码的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - microsoft-agent-framework
  - workflow-runner
  - source
---

## 来源边界

本页只投影 Microsoft Agent Framework Python workflow runner 源码。
它用于界定 checkpoint restore 对 workflow graph 兼容性的约束。
原始材料未保存到 `raw/`；本页直接引用 GitHub raw/source URL 作为主证据。

## 可复用关键主张

- Python workflow runner 在恢复 checkpoint 时会校验 workflow graph 兼容性。
- 如果恢复时 graph 已改变，runner 会报出 workflow graph changed 相关错误。
- 这支持把 MAF graph workflow 描述为 build 后受 graph 兼容性约束的执行结构，
  而不是运行中任意 mutable graph。

## 限制与冲突

- 本页只投影 Python 实现源码；
  .NET API 的公开 mutator 和兼容性约束需要单独核对。
- 源码随 main 分支演进，未来 release 可能改变具体错误或校验方式。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://raw.githubusercontent.com/microsoft/agent-framework/main/python/packages/core/agent_framework/_workflows/_runner.py` | Microsoft Agent Framework Python workflow runner 源码；访问时间 2026-06-13。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| MAF Python workflow runner 对 checkpoint restore 的 graph 兼容性有约束。 | 上方证据单元。 | 该结论不自动覆盖所有语言实现和 future release。 |
| MAF graph workflow 不应被描述为运行中任意 mutable graph。 | 上方证据单元。 | 可通过重新 build 或 declarative authoring 创建新 workflow，但不是当前 execution 原地改图。 |
