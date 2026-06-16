---
schema_version: 2
page_type: source
title: "ASP.NET Core Web API 文档"
status: active
created: 2026-06-16
updated: 2026-06-16
summary: "ASP.NET Core 创建 Web API 的 controller/minimal API 与 API-specific 行为的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - aspnet-core
  - web-api
  - rest-api
---

## 来源边界

本页只投影 Microsoft Learn 的 Create web APIs with ASP.NET Core 文档。
它用于界定 ASP.NET Core 作为 Web API 应用框架时的 controllers、Minimal APIs、
ControllerBase、attribute routing、HTTP verb attributes、model validation、
automatic 400 responses 和 ProblemDetails 等 API-specific 行为。
原始材料未保存到 `raw/`；本页直接引用外部 URL 作为主证据。

## 可复用关键主张

- ASP.NET Core 支持用 controllers 或 Minimal APIs 创建 Web APIs。
- Controller-based Web API 由一个或多个继承 `ControllerBase` 的 controller classes 构成。
- `Microsoft.AspNetCore.Mvc` 提供 attributes，用于配置 controller/action 行为，
  包括 route、HTTP verb、consumes 和 produces 等。
- `[ApiController]` 启用 API-specific behaviors，包括 attribute routing requirement、
  automatic HTTP 400 responses、binding source parameter inference 和 ProblemDetails。

## 限制与冲突

- 本页只支撑 ASP.NET Core Web API 应用模型；
  middleware pipeline 由独立 source page 支撑。
- 文档覆盖 .NET 10 及多 moniker；具体行为可能随 ASP.NET Core 版本变化。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://learn.microsoft.com/en-us/aspnet/core/web-api/?view=aspnetcore-10.0` | Microsoft Learn Create web APIs with ASP.NET Core 文档；访问时间 2026-06-16；文档页元数据 `ms.date` 为 2026-05-06，`git_commit_id` 为 `5352338e22b3821e5162730784f574341317e9a9`。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| ASP.NET Core 的 Web API 应用模型围绕 controllers 或 Minimal APIs 组织 HTTP API。 | 上方证据单元。 | 不覆盖应用托管平台选择，例如 Container Apps、App Service 或 AKS。 |
| ASP.NET Core 为 Web API 提供 routing、HTTP verb、binding/validation 和错误响应等 API-specific 框架行为。 | 上方证据单元。 | 版本化、网关策略和组织治理可能还需要额外库、配置或 API Management。 |
