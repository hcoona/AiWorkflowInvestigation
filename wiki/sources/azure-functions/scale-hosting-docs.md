---
schema_version: 2
page_type: source
title: "Azure Functions Scale and Hosting 文档"
status: active
created: 2026-06-16
updated: 2026-06-16
summary: "Azure Functions hosting plans 与 scale 行为的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - azure-functions
  - hosting
  - scale
---

## 来源边界

本页只投影 Microsoft Learn 的 Azure Functions Scale and Hosting 文档。
它用于界定 Azure Functions app 的 hosting options、scale behavior、resource
availability、 network/container support、cost、plan 选择影响，以及不同 plan 下
function app、 function trigger group 与 host instances 的伸缩粒度。
原始材料未保存到 `raw/`；本页直接引用外部 URL 作为主证据。

## 可复用关键主张

- 创建 Azure Functions function app 时必须选择 hosting option。
- Hosting option 会影响 function app 如何 scale、可用资源、advanced
  functionality 支持、Linux container support 和成本。
- Azure Functions hosting options 包括 Flex Consumption、Premium、Dedicated、
  Container Apps 和 legacy Consumption 等。
- Flex Consumption plan 中，scale decisions 按 per-function basis 计算；但 HTTP
  triggers 作为一组 scale，Blob storage (Event Grid) triggers 作为一组 scale，
  Durable Functions triggers 也共享 instances 并一起 scale。
- Premium 和 Container Apps plan 通过添加 Functions host instances 基于触发事件
  自动扩展；Dedicated plan 使用 manual/autoscale。
- Premium 和 Dedicated 等 plan
  适合不同的持续运行、控制、网络、容器或可预测计费场景。

## 限制与冲突

- 本页只支撑 Azure Functions hosting/scale 边界；
  不覆盖 Durable Functions orchestration 语义本身。
- 本来源只说明 Azure Functions hosting/scale 边界；
  不评价任何业务 process manager 适配性。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale` | Microsoft Learn Azure Functions Scale and Hosting 文档；访问时间 2026-06-16。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| Azure Functions hosting option 会影响 scale、资源、网络/容器支持和成本。 | 上方证据单元。 | 具体计划能力随 Azure Functions 版本与区域支持变化。 |
| Azure Functions 的实际 scale 粒度依赖 hosting plan 和 trigger/scale group；Flex Consumption 支持 per-function scaling，但 Durable Functions triggers 共享 instances 并一起 scale。 | 上方证据单元。 | 本页不展开 Durable Functions 内部 task hub、control queue 或 backend capacity 细节。 |
| Premium、Container Apps 和 Consumption 等计划可通过添加 Functions host instances 基于事件扩展。 | 上方证据单元。 | 最大实例数、区域、私有端点和 quota 约束会影响可用扩展范围。 |
