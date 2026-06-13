---
schema_version: 2
page_type: source
title: "Temporal Workflow Versioning 文档"
status: active
created: 2026-06-13
updated: 2026-06-13
summary: "Temporal patching/GetVersion workflow versioning 的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - temporal
  - versioning
  - workflow
---

## 来源边界

本页只投影 Temporal Go SDK 的 Workflow versioning 文档中 patching/GetVersion
相关部分。
它用于界定 Workflow Definition 变更如何兼容已有 Event History。
原始材料未保存到 `raw/`；本页直接引用外部 URL 作为主证据。

## 可复用关键主张

- Workflow Definition 变更必须兼容已存在的 Event History。
- Patching/GetVersion 通过显式 marker 和分支让新旧代码在 replay 中可区分。
- 版本化机制支持受控演进和迁移，不等于运行中任意改写当前 Workflow Definition。

## 限制与冲突

- 本页只投影 Go SDK versioning 文档；
  其它 SDK 的 API 形态可能不同。
- Patching/GetVersion 解决的是部署演进与 replay 兼容性，不覆盖 Worker Versioning
  的 task routing。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://docs.temporal.io/develop/go/workflows/versioning#patching` | Temporal Go Workflow versioning / patching 文档；访问时间 2026-06-13。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| Temporal 使用 patching/GetVersion 让 Workflow Definition 变更与已有历史兼容。 | 上方证据单元。 | 这需要显式版本分支，不是任意热替换 Workflow Definition。 |
| Workflow versioning 支持受控演进，不等于运行中 plan mutation。 | 上方证据单元。 | 仍需结合 deterministic constraints 和 worker versioning 文档判断部署边界。 |
