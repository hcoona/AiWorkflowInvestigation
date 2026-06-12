---
schema_version: 2
page_type: source
title: "Temporal Activities 文档"
status: active
created: 2026-06-12
updated: 2026-06-12
summary: "Temporal Activities 官方文档的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - temporal
  - activities
  - side-effects
---

## 来源边界

本页只投影 Temporal 的 Activities 官方文档。
它用于界定 Activity 作为单一外部工作单元的语义，以及 retry、timeout
和幂等性相关边界。
原始材料未保存到 `raw/`；本页直接引用外部 URL 作为主证据。

## 可复用关键主张

- Activities 是普通函数或方法，用于执行单一、明确的外部工作。
- 官方示例覆盖调用其他服务、发送邮件、写操作、批量写、LLM call、large download
  和 slow-polling read。
- 因为 Activities 可能重试，设计时应考虑幂等性。

## 限制与冲突

- 本页不把所有外部工具调用都等同于可靠执行；可靠性还依赖 Activity retry、timeout
  与业务幂等设计。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://docs.temporal.io/activities` | Temporal Activities 官方文档；访问时间 2026-06-12。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| Temporal Activities 用于执行单一、明确的外部工作。 | 上方证据单元。 | 具体可靠性仍依赖 retry/timeout/幂等配置。 |
| Activities 官方示例覆盖服务调用、邮件、写操作、批量写、LLM call、large download 和 slow-polling read。 | 上方证据单元。 | DB/file I/O 与 Workflow replay 路径边界需要结合 Workflows 和 deterministic constraints source pages。 |
