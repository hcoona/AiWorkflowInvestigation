---
schema_version: 2
page_type: source
title: "Microsoft Agent Framework Durable Extension 文档"
status: active
created: 2026-06-12
updated: 2026-06-12
summary: "Microsoft Agent Framework Durable Extension 文档的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - microsoft-agent-framework
  - durable-extension
  - durable-task
---

## 来源边界

本页只投影 Microsoft Agent Framework 的 Durable Extension 文档。
它用于说明 Durable Task-backed durability 如何进入 agents、multi-agent
orchestrations 与 workflows。
原始材料未保存到 `raw/`；本页直接引用外部 URL 作为主证据。

## 可复用关键主张

- Durable Extension 是 Microsoft Agent Framework 的持久化执行集成层。
- Durable Extension 引入 Durable Task-backed execution、checkpoint、resume
  与 HITL 等能力。
- 它是 hosting/integration layer，不是替代所有 workflow surface 的核心 API。

## 限制与冲突

- 没有 Durable Extension 时，不应假定 workflow 具备同等跨进程恢复语义。
- Durable Extension 的宿主和包状态需要随具体部署目标复核。
- 安装示例中的 `--pre` / `--prerelease` 是包分发状态信号；
  不能单独推导整个 Agent Framework 或全部 workflow API 的 GA 状态。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://learn.microsoft.com/en-us/agent-framework/integrations/durable-extension` | Microsoft Agent Framework Durable Extension 文档；访问时间 2026-06-12。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| Durable Extension 把 Durable Task-backed durability 引入 Agent Framework workflows。 | 上方证据单元。 | 这是 integration/hosting 层，不是全框架唯一运行方式。 |
| 跨进程恢复语义需要明确是否使用 Durable Extension。 | 上方证据单元。 | 具体后端和宿主会影响可用性与稳定性。 |
