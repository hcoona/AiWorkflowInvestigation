---
schema_version: 2
page_type: source
title: "来源标题"
status: seed
created: YYYY-MM-DD
updated: YYYY-MM-DD
summary: "仅用于路由和定位的一句话摘要。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - 主题
---

## 来源边界

说明该来源是什么、为什么重要，以及原始材料是否已保存在 `raw/`。
如果直接引用外部资料而未写入 `raw/`，说明外部访问路径和未入库原因。

## 可复用关键主张

只记录未来综合分析可能复用的主张。

## 限制与冲突

说明已知来源限制、不确定性、权限约束、冲突和时效性风险。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://example.invalid/source` | 替换为主要 raw、external、session 或 user 证据引用；外部来源不必复制到 `raw/`，但本 source page 需要承载证据链。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| 本 source page 基于主要证据。 | 上方证据单元。 | 入库前替换所有占位内容。 |
