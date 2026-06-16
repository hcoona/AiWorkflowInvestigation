---
schema_version: 2
page_type: source
title: "Azure Functions HTTP Trigger 文档"
status: active
created: 2026-06-16
updated: 2026-06-16
summary: "Azure Functions HTTP trigger 调用模型与 HTTP endpoint 能力的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - azure-functions
  - http-trigger
  - http-api
---

## 来源边界

本页只投影 Microsoft Learn 的 Azure Functions HTTP trigger 文档。
它用于界定 HTTP trigger 可以用 HTTP request 调用 function、可用于 serverless APIs
和 webhooks、可配置 HTTP response/output binding、并可按语言模型声明方法和 route。
原始材料未保存到 `raw/`；本页直接引用外部 URL 作为主证据。

## 可复用关键主张

- HTTP trigger lets you invoke a function with an HTTP request。
- HTTP trigger 可用于构建 serverless APIs 和响应 webhooks。
- HTTP-triggered function 的响应可通过 output binding 或语言特定响应对象配置。
- 文档示例展示了按 HTTP method、route parameter、query string 和 request body
  处理请求。

## 限制与冲突

- 本页只支撑 HTTP trigger 本身的调用模型；
  不证明 Azure Functions 提供与 ASP.NET Core 等价的完整 middleware pipeline。
- 不同语言 worker 和 Functions programming model 的 API 形态不同；
  本页只抽取与 HTTP API 边界有关的通用主张。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://learn.microsoft.com/en-us/azure/azure-functions/functions-bindings-http-webhook-trigger` | Microsoft Learn Azure Functions HTTP trigger 文档；访问时间 2026-06-16；文档页元数据 `ms.date` 为 2025-05-02，`git_commit_id` 为 `1a48602ec3642c208cab5511d31eff670cf17e32`。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| Azure Functions HTTP trigger 将 HTTP request 作为触发 function 的机制，可用于 serverless APIs 和 webhooks。 | 上方证据单元。 | 不覆盖 API Management、Functions hosting plan 或 ASP.NET Core integration 的全部行为。 |
| HTTP trigger 能处理 method、route、query string、body 和 response，但其文档边界仍是 function trigger/binding。 | 上方证据单元。 | 这是从多个语言示例归纳的通用能力，不代表每个语言 worker 的 API 细节相同。 |
