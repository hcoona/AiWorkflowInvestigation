---
schema_version: 2
page_type: source
title: "Cobbler README"
status: active
created: 2026-06-16
updated: 2026-06-16
summary: "Cobbler Linux installation server 定位的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - cobbler
  - bare-metal
  - installation
---

## 来源边界

本页只投影 Cobbler 仓库 README。
它用于界定 Cobbler 作为 Linux installation server、
network installation automation 和 power/configuration orchestration 边界。
原始材料未保存到 `raw/`；本页直接引用外部 URL 作为主证据。

## 可复用关键主张

- Cobbler 是 Linux installation server，用于快速建立 network installation environments。
- Cobbler 自动化安装、DNS、DHCP、package updates、power management、
  configuration management orchestration 等相关任务。
- Cobbler 用于系统 rollout 或修改 existing systems 时减少手工跨命令/应用操作。

## 限制与冲突

- 本页只投影 README；
  不覆盖 Cobbler data model、API、Power Management provider 或具体发行版集成。
- GitHub branch URL 是可变来源；强版本判断应补 tag/commit 或版本化文档。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://raw.githubusercontent.com/cobbler/cobbler/main/README.md` | Cobbler README；访问时间 2026-06-16。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| Cobbler 是裸金属安装/provisioning 子系统候选。 | 上方证据单元。 | 不覆盖所有外部集成和部署模式。 |
| Cobbler 应被 buildout process manager 协调，而不是被当成无状态 shell 命令集合。 | 上方证据单元。 | 这是场景映射；具体职责边界取决于 Cobbler 使用范围。 |
