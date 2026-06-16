---
schema_version: 2
page_type: source
title: "OpenStack Ironic README"
status: active
created: 2026-06-16
updated: 2026-06-16
summary: "OpenStack Ironic 物理机管理与 provisioning 定位的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - ironic
  - bare-metal
  - provisioning
---

## 来源边界

本页只投影 OpenStack Ironic 仓库 README。
它用于界定 Ironic 作为以 API 和 plug-ins 管理、provision physical machines 的服务。
原始材料未保存到 `raw/`；本页直接引用外部 URL 作为主证据。

## 可复用关键主张

- Ironic 由 API 和 plug-ins 组成，用于以 security-aware、fault-tolerant 方式
  管理和 provisioning physical machines。
- Ironic 可作为 Nova hypervisor driver 或 standalone service 使用。
- Ironic 默认使用 PXE 和 IPMI/Redfish 与 bare metal machines 交互，
  并可通过相关项目如 Bifrost 和 Metal3 简化使用。

## 限制与冲突

- 本页只投影 README 的定位描述；
  不覆盖 Ironic driver 细节、状态机、API 调用序列或具体 release 行为。
- GitHub branch URL 是可变来源；强版本判断应补版本化 OpenStack docs。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://raw.githubusercontent.com/openstack/ironic/master/README.rst` | OpenStack Ironic README；访问时间 2026-06-16。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| Ironic 是裸金属 provisioning 控制面候选。 | 上方证据单元。 | 不说明所有 driver 和部署模式的行为。 |
| Ironic 的 PXE/IPMI/Redfish 交互应作为 buildout process manager 的下层领域系统处理。 | 上方证据单元。 | 这是场景映射；具体调用边界需按 Ironic API/driver 设计。 |
