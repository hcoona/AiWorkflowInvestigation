---
schema_version: 2
page_type: source
title: "Tinkerbell README"
status: active
created: 2026-06-16
updated: 2026-06-16
summary: "Tinkerbell bare metal provisioning engine 定位的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - tinkerbell
  - bare-metal
  - provisioning
---

## 来源边界

本页只投影 Tinkerbell 仓库 README。
它用于界定 Tinkerbell 作为 bare metal provisioning engine 的定位、
网络/ISO 启动、BMC interactions、metadata service 和 workflow engine 能力。
原始材料未保存到 `raw/`；本页直接引用外部 URL 作为主证据。

## 可复用关键主张

- Tinkerbell 是 bare metal provisioning engine。
- Tinkerbell 支持 network 和 ISO booting、BMC interactions、metadata service
  和 provisioning workflow engine。
- Tinkerbell 功能包括 cloud-init integration、DHCP/ProxyDHCP、Redfish/IPMI/IntelAMT
  等 BMC 支持、Hardware auto-discovery 和 Serial over SSH。

## 限制与冲突

- 本页只投影 README；
  不覆盖 Tinkerbell 各 service 的 API、状态机、Kubernetes 部署或版本差异。
- Tinkerbell 自带 workflow engine，但在本 wiki 场景中仍按裸金属 provisioning
  领域控制面处理，不自动成为全局 buildout process manager。
- GitHub branch URL 是可变来源；强版本判断应补 tag/commit 或版本化文档。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://raw.githubusercontent.com/tinkerbell/tinkerbell/main/README.md` | Tinkerbell README；访问时间 2026-06-16。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| Tinkerbell 是裸金属 provisioning 控制面候选，并自身包含 provisioning workflow engine。 | 上方证据单元。 | 不等同于全局 cluster buildout process manager。 |
| Tinkerbell 应被上层 process manager 协调和观察，而不是被当成普通 shell 命令。 | 上方证据单元。 | 这是场景映射；具体边界取决于采用哪些 Tinkerbell components。 |
