---
schema_version: 2
page_type: source
title: "xCAT Documentation Index"
status: active
created: 2026-06-16
updated: 2026-06-16
summary: "xCAT 集群部署与管理能力的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - xcat
  - bare-metal
  - cluster-management
---

## 来源边界

本页只投影 xCAT stable documentation index。
它用于界定 xCAT 作为集群、HPC、datacenter 等环境的部署与管理工具包定位。
原始材料未保存到 `raw/`；本页直接引用外部 URL 作为主证据。

## 可复用关键主张

- xCAT 是 Extreme Cloud Administration Toolkit。
- xCAT 面向 clouds、clusters、HPC、grids、datacenters 等环境管理。
- xCAT 文档列出的能力包括 hardware discovery、remote system management、
  physical/virtual machines OS provisioning、stateful/stateless provisioning、
  application installation/configuration、parallel system management 和 cloud integration。

## 限制与冲突

- 本页只投影 documentation index 的能力列表；
  不覆盖 xCAT 具体命令、状态模型、支持矩阵或 Confluent 迁移建议。
- xCAT 项目状态和推荐迁移路径可能变化；
  新建部署决策应另查当前项目状态与替代方案。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://xcat-docs.readthedocs.io/en/stable/` | xCAT stable documentation index；访问时间 2026-06-16。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| xCAT 是裸金属/集群部署与管理控制面候选。 | 上方证据单元。 | 不评价 xCAT 当前生态健康度或是否适合新项目。 |
| xCAT 覆盖硬件发现、OS provisioning 和并行系统管理等 buildout 子领域。 | 上方证据单元。 | 具体能力和支持矩阵需查更细文档。 |
