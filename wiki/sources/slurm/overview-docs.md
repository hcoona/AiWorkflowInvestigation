---
schema_version: 2
page_type: source
title: "Slurm Overview 文档"
status: active
created: 2026-06-16
updated: 2026-06-16
summary: "Slurm cluster management and job scheduling 定位的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - slurm
  - cluster-management
  - scheduler
---

## 来源边界

本页只投影 Slurm overview 文档。
它用于界定 Slurm 作为 Linux clusters 的 cluster management and job scheduling
系统，以及其 nodes、partitions、jobs、job steps 等实体边界。
原始材料未保存到 `raw/`；本页直接引用外部 URL 作为主证据。

## 可复用关键主张

- Slurm 是 open source、fault-tolerant、highly scalable 的 cluster management
  and job scheduling system。
- Slurm 作为 cluster workload manager，分配 compute node resources、
  启动/执行/监控工作，并通过队列仲裁资源竞争。
- Slurm 架构包括 `slurmctld`、`slurmd`、可选 `slurmdbd` 和 `slurmrestd`。
- Slurm 管理的实体包括 nodes、partitions、jobs 和 job steps。

## 限制与冲突

- 本页只投影 overview；
  不覆盖 Slurm 配置、插件、资源拓扑、HA 部署或具体命令行为。
- 在裸金属 buildout 中，Slurm 更适合作为后段集群资源管理和验证作业执行面，
  不替代 provisioning 或硬件管理控制面。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://slurm.schedmd.com/overview.html` | Slurm overview 文档；访问时间 2026-06-16。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| Slurm 是集群资源管理和作业调度系统。 | 上方证据单元。 | 不覆盖所有插件和部署策略。 |
| Slurm 可作为裸金属 buildout 后段验收和资源调度相关控制面。 | 上方证据单元。 | 这是场景映射；不表示 Slurm 负责硬件 provisioning。 |
