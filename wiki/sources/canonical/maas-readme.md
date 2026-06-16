---
schema_version: 2
page_type: source
title: "Canonical MAAS README"
status: active
created: 2026-06-16
updated: 2026-06-16
summary: "Canonical MAAS README 对 Metal as a Service 定位的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - maas
  - bare-metal
  - provisioning
---

## 来源边界

本页只投影 Canonical MAAS 仓库 README。
它用于界定 MAAS 如何把 physical servers 作为 cloud-like bare metal resources 管理。
原始材料未保存到 `raw/`；本页直接引用外部 URL 作为主证据。

## 可复用关键主张

- MAAS 是 Metal as a Service，让用户像云中的虚拟机一样对待物理服务器。
- MAAS 将 bare metal 转换为 elastic cloud-like resource。
- MAAS 可 boot、check、deploy、tear down、redeploy 机器，并把节点交给上层工具使用。

## 限制与冲突

- 本页只投影 README 中的产品定位；
  不覆盖 MAAS API 细节、版本差异、控制器部署、网络设计或故障恢复策略。
- GitHub branch URL 是可变来源；重要版本判断应补 tag/commit 或版本化文档。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://raw.githubusercontent.com/canonical/maas/master/README.rst` | Canonical MAAS README；访问时间 2026-06-16。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| MAAS 是裸金属机器生命周期和资源池管理控制面候选。 | 上方证据单元。 | README 是产品定位，不替代目标版本的 API/运维文档。 |
| MAAS 应被 buildout process manager 协调，而不是被 workflow 平台重写。 | 上方证据单元。 | 这是场景映射；具体职责划分取决于部署架构。 |
