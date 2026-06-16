---
schema_version: 2
page_type: source
title: "ASP.NET Core Middleware 文档"
status: active
created: 2026-06-16
updated: 2026-06-16
summary: "ASP.NET Core request pipeline 与 middleware 语义的单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - aspnet-core
  - middleware
  - request-pipeline
---

## 来源边界

本页只投影 Microsoft Learn 的 ASP.NET Core Middleware 文档。
它用于界定 ASP.NET Core 中 HTTP request/response 如何经过由 middleware
组成的 app pipeline，以及 middleware 如何选择传递、前后处理或 short-circuit 请求。
原始材料未保存到 `raw/`；本页直接引用外部 URL 作为主证据。

## 可复用关键主张

- Middleware 是组装进 app pipeline、用于处理 requests 和 responses 的软件。
- 每个 middleware 可以选择是否把 request 传给 pipeline 中的下一个 middleware。
- Middleware 可以在调用下一个 middleware 前后执行工作，也可以 short-circuit pipeline。
- ASP.NET Core request pipeline 由一组按顺序调用的 request delegates 构成。

## 限制与冲突

- 本页只支撑 ASP.NET Core request pipeline/middleware 语义；
  不覆盖 Azure Functions worker middleware 或 API Management policy。
- Middleware 的具体顺序、内置组件和最佳实践需要结合应用类型和 ASP.NET Core 版本判断。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| external | `https://learn.microsoft.com/en-us/aspnet/core/fundamentals/middleware/?view=aspnetcore-10.0` | Microsoft Learn ASP.NET Core Middleware 文档；访问时间 2026-06-16；文档页元数据 `ms.date` 为 2026-06-09，`git_commit_id` 为 `af0bff1088fc577d0758ec188ae1c3d71cd4e116`。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| ASP.NET Core 的 HTTP 请求处理以可组合 middleware pipeline 为核心机制之一。 | 上方证据单元。 | 不说明每个内置 middleware 的细节或最佳顺序。 |
| Middleware 能在请求传递前后处理，也能 short-circuit pipeline，因此适合表达统一横切 HTTP 策略。 | 上方证据单元。 | 横切策略仍需应用设计和测试；pipeline 能力本身不保证治理质量。 |
