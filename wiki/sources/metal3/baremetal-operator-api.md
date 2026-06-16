---
schema_version: 2
page_type: source
title: "Metal3 Baremetal Operator API 文档"
status: active
created: 2026-06-16
updated: 2026-06-16
summary: "Metal3 BareMetalHost 与裸金属资源 API 的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - metal3
  - bare-metal
  - kubernetes
---

## 来源边界

本页只投影 Metal3 baremetal-operator 的 API 文档。
它用于界定 BareMetalHost、provisioning 前置条件、BMC details、
firmware/hardware 相关资源和 Kubernetes CRD 风格的裸金属资源边界。
原始材料未保存到 `raw/`；本页直接引用外部 URL 作为主证据。

## 可复用关键主张

- Metal3 引入 BareMetalHost resource，用于定义 physical host 及其属性。
- 启动 provisioning 需要有效 image URL、`online: true` 和 BMC details。
- 没有 BMC details 的 hosts 会处于 unmanaged 状态，不能 provisioning。
- Metal3 还定义 HostFirmwareSettings、FirmwareSchema、HardwareData、
  PreprovisioningImage 和 BareMetalSwitch 等资源，承载 firmware、hardware
  与网络交换机相关状态。

## 限制与冲突

- 本页只投影 baremetal-operator API 文档；
  不覆盖 Cluster API Provider Metal3、Ironic 集成部署或全部状态迁移。
- Metal3 是 Kubernetes/CRD 生态的裸金属控制面；
  本页不把它作为默认全局 buildout process manager。
- GitHub branch URL 是可变来源；强版本判断应补 tag/commit 或版本化文档。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://raw.githubusercontent.com/metal3-io/baremetal-operator/main/docs/api.md` | Metal3 baremetal-operator API 文档；访问时间 2026-06-16。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| Metal3 BareMetalHost 是 Kubernetes/CRD 风格的物理主机资源边界。 | 上方证据单元。 | 不覆盖完整 provisioning state machine。 |
| Metal3 可以作为 buildout 过程中的裸金属资源控制面或子系统。 | 上方证据单元。 | 是否采用取决于是否已有 Kubernetes/Ironic 管理平面。 |
