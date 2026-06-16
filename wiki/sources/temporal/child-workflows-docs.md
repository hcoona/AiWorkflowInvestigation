---
schema_version: 2
page_type: source
title: "Temporal Child Workflows 文档"
status: active
created: 2026-06-16
updated: 2026-06-16
summary: "Temporal Child Workflow Execution 的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - temporal
  - child-workflows
  - workflow
---

## 来源边界

本页只投影 Temporal Child Workflows 文档。
它用于界定 Child Workflow Execution 与 Parent Workflow Execution 的关系、
适用场景、Parent Close Policy 边界，以及用 Child Workflow 按资源分区的语义。
原始材料未保存到 `raw/`；本页直接引用外部 URL 作为主证据。

## 可复用关键主张

- Child Workflow Execution 是由同一 Namespace 内另一个 Workflow 启动的
  Workflow Execution。
- Child Workflows 可用于把大问题拆成更小块，因为 Child Workflow 有自己的
  Event History。
- Child Workflow 可以与单个资源一对一映射；文档示例提到按 host 启动
  Child Workflow，并用 host 名作为 Workflow ID 来串行化该 host 的操作。
- Child Workflow 不应仅为代码组织使用；如果问题规模受限，文档建议先从单个
  Workflow Definition 与 Activities 开始。

## 限制与冲突

- 本页只支撑 Child Workflow 的资源分区和 Event History 隔离语义；
  不支撑把 Child Workflow 写成自动局部回滚机制。
- Parent 使用 Continue-As-New 时，Child Workflows 不会自动转移到新的 Parent
  instance；裸金属 buildout 设计必须显式处理 Parent/Child 的边界和定位。
- Child Workflow 会增加 Event History 事件成本；大规模资源建模仍需容量与历史长度设计。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://docs.temporal.io/child-workflows` | Temporal Child Workflows 文档；访问时间 2026-06-16。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| Temporal Child Workflow Execution 可作为 Parent Workflow 内启动的独立 Workflow Execution。 | 上方证据单元。 | 仍在同一 Namespace 内；具体 SDK API 不在本页范围。 |
| Child Workflows 可用于按资源或大规模工作负载分区。 | 上方证据单元。 | 文档同时建议不要仅为代码组织使用，且需关注 Event History 成本。 |
| 在裸金属 buildout 中，Child Workflow 可支撑按 host/node/rack 等资源实体拆分长期过程状态。 | 上方证据单元。 | 这是场景映射；资源依赖、失败传播和补偿仍是业务建模问题。 |
