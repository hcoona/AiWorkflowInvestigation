---
schema_version: 2
page_type: analysis
title: "MAF Durable Function Apps 与 Temporal 的 Scale-out 边界"
status: active
created: 2026-06-16
updated: 2026-06-16
summary: "比较 MAF Durable Extension on Azure Functions 与 Temporal 在多 graph workload 下的 scale-out 粒度和资源利用边界。"
maintenance:
  edit_policy: update
validation:
  body_contract: analysis-answer-memo
tags:
  - microsoft-agent-framework
  - azure-functions
  - temporal
  - scale-out
---

## 问题

本页回答一个窄问题：如果 graph 数量变多、不同 graph 的负载和依赖差异变大， MAF
Durable Extension 跑在 Azure Function Apps 上，是否会比 Temporal 更早遇到
scale-out 粒度或资源利用效率问题？

本页只讨论运行时放置、调度边界和资源池粒度。
不评价 MAF workflow 表达力、 Azure Durable Functions 可靠性、Temporal
采购建议、云平台成本，或具体 benchmark。

## 答案

**方向性判断是：在多 graph、异构 workload、冷热不均或不同 SLA/依赖的场景下， MAF
Durable Function Apps 更容易比 Temporal 先遇到 scale-out
粒度和资源利用效率问题。**
原因不是 Durable Task 不能扩，也不是 MAF graph 不能持久化执行，而是 MAF Azure
Functions hosting 更容易把多个 workflow/executor 的代码、metadata、 依赖、host
资源、部署生命周期和有效伸缩拓扑耦合在同一组 Function App/host 里。

Temporal 的优势也不是“自动把一个 graph 切成多个子图”。
它的优势是 Task Queue、Worker Entity、Worker Process、Activity、Child Workflow
这些一等对象 已经把 execution routing、资源池和状态/history 边界拆得更清楚。
开发者可以显式把 不同 workload 放到不同 Task Queues 和 worker fleets；Worker
只在有 spare capacity 时轮询任务，Task Queue 还能承担 load balancing、routing 和
Activity Task 的 server-side throttling。

因此更精确的结论是：

- **逻辑子图不等于 runtime partition。**
  只是把 graph 画成子图，既不会自动改善扩容， 也不会自动隔离资源。
- **MAF Durable Functions 能横向扩容，但默认不是 per-graph resource pool。**
  当许多 graph 共享同一 Function App/host 时，冷启动、内存、依赖、发布和
  plan/trigger scale group 边界容易一起移动。
- **Temporal 的 partition surface 更细。**
  Workflow/Activity/Child Workflow 可以路由到 Task Queue，Task Queue
  再由一个或多个 Worker Entities/Processes 轮询。
- **差距在 workload 异构时扩大。**
  如果 graph 少、负载相似、依赖简单， Function App 横向扩容可以工作得很好；如果
  graph 多、冷热不均、资源依赖差异大， Temporal 的 queue/worker-pool
  模型通常更容易提高资源利用率和隔离性。

## 对齐四个层次

| 层次 | MAF Durable Function Apps | Temporal | 对 scale-out 的含义 |
| --- | --- | --- | --- |
| 作者/建模层 | MAF graph workflow、executor、agent、subworkflow。 | Workflow Definition、Activity Definition、Child Workflow。 | 这层决定业务结构，但不直接决定资源池。 |
| runtime work item 层 | Durable Task orchestration、activity、entity、sub-orchestration、external event。 | Workflow Task、Activity Task、Child Workflow Execution。 | 这层决定可调度、可持久化和可恢复的单位。 |
| dispatch/resource-pool 层 | Durable Task Scheduler dispatches work items 到 connected apps；Azure Functions host 承载 generated function metadata。 | Task Queue 被 Worker Entities/Processes 轮询，支持 load balancing、routing 和 throttling。 | 这是 MAF Functions 与 Temporal 最关键的差异轴。 |
| deployment/host 层 | Function App 是 deployment/config/package/identity 边界，可包含多个 durable workflows；实际 scale 粒度依赖 hosting plan 与 trigger/scale group。 | Worker Processes 在 Temporal Service 外部运行，可按 Task Queue/workload 组成 worker fleet。 | host 与 scale group 越粗，多 graph 异构负载下越容易资源浪费。 |

这张表只比较抽象机制，不代表某个具体部署一定慢或一定贵。
真正的瓶颈取决于 graph 数量、activity 粒度、依赖体积、冷启动成本、host plan、
worker 并行度、backend capacity、queue/backlog 和组织拆分方式。

## 为什么 graph 多时 MAF Function Apps 更容易变粗

MAF Azure Functions hosting 的源码路径显示，一个 host 的 metadata transformer
会遍历 configured durable workflows，为每个 workflow 生成 orchestration/HTTP
trigger metadata，并为 executor 生成 activity/entity trigger metadata；共享
executor 的 function metadata 会去重。
这排除了“一图一 Function App”的必然关系，也说明 一个 Function App/host
可以承载多个 durable workflows。

这对简单部署是优点：多个 MAF workflows 可以共享 host、配置、依赖和发布流程。
但 graph 多起来后，这种共享也会变成 coupling：

| 耦合面 | 可能后果 |
| --- | --- |
| 部署包和依赖 | 一个冷 graph 的依赖也可能进入同一 host 包；启动、内存和安全扫描边界变粗。 |
| function metadata | 多 workflow/executor 共享 host metadata 生成路径；host 启动和管理面复杂度随注册集合增长。 |
| host 资源 | CPU、内存、连接池、线程池、并发限制和冷启动成本更容易在 graph 之间共享。 |
| scale/resource-pool 信号 | 如果多个 graph 共用 Function App/host，实际扩容会受 hosting plan、trigger/scale group 和 host 资源约束影响，而不是天然按单个 graph 的资源画像拆分。 |
| 发布和身份 | 不同 graph 的发布节奏、权限、网络和密钥边界更容易被同一 Function App 绑定。 |

这些不是 MAF 的语义错误，而是 hosting topology 的自然后果。
要缓解它，通常需要人为拆 Function Apps、worker apps、backend/task
hub、身份和网络边界；这属于部署设计， 不是 MAF graph 自动给出的 partition。

## 为什么 Temporal 更适合显式资源池拆分

Temporal Task Queue 是轻量、按需创建的队列，一个或多个 Worker Entities
可以轮询它。
文档明确把 Task Queue 与 load balancing、Task Routing、Activity Task server-side
throttling 和 worker down 后任务保留关联起来。
Temporal Workers 文档也把 Worker Program、Worker Entity 和 Worker Process
拆开：Worker Entity 监听单个 Task Queue； Worker Process 在 Temporal Service
外部轮询队列、执行用户代码，并把结果返回 Temporal
Service；生产应用可以按需运行一组 Worker Processes。

这使 Temporal 的资源池拆分更自然：

- 可以按 graph 类型、资源类型、SLA、租户或依赖，把 Workflow/Activity/Child
  Workflow 路由到不同 Task Queues。
- 可以让不同 Worker Processes 只注册某个 Task Queue 上需要的 Workflow/Activity
  handlers，避免把所有 graph 的依赖装进同一进程。
- 可以独立扩 Activity-heavy worker pool、GPU/网络/credential 特殊 worker pool，
  或高优先级 workflow queue。
- Child Workflow 还能提供独立 Workflow Execution 和 Event
  History，用于把资源实体或大任务 拆成独立运行时状态边界。

因此 Temporal 不是“比 MAF 更会画子图”，而是更容易把业务拆分映射成可调度队列、
worker fleet 和 history boundary。

## 不能过度推出的结论

不能把上述判断写成“MAF Durable Functions scale-out 差”。 更安全的说法是：

- 如果主要瓶颈是大量同质 activity throughput，MAF Durable Functions 借助 Azure
  Functions hosting 和 Durable Task Scheduler 仍可以横向扩展。
- 如果 graph 少、依赖相近、发布节奏一致、SLA 相同，把多个 workflows 放在同一
  Function App/host 可能是合理简化。
- 如果团队愿意按 workload 手动拆 Function Apps/worker apps、身份、网络和 backend
  边界，MAF Durable Extension 的资源隔离可以改善。
- 但是当 graph 数量和异构性继续增加时，Temporal 的 Task Queue/Worker Process
  模型 通常更容易维持细粒度扩容、依赖隔离和资源利用率。

换句话说，MAF Durable Function Apps 的潜在瓶颈是
**execution unit 与 deployment unit 解耦不如 Temporal 自然**；Temporal
的潜在成本是你必须显式设计 Task Queue、 worker 注册、版本、容量和运维治理。

## 判断清单

如果出现以下信号，应优先担心 MAF Durable Function Apps 的资源利用效率：

| 信号 | 为什么重要 |
| --- | --- |
| graph 数量多且冷热差异大 | 冷 graph 可能仍被同一 host 的依赖、metadata 和部署边界携带。 |
| graph 依赖差异大 | 一个 graph 需要的 SDK、网络或 credential 可能污染整个 Function App 包。 |
| activity 资源画像差异大 | CPU-heavy、IO-heavy、GPU、慢外部 API 不宜共享同一粗资源池。 |
| 不同 graph 有不同 SLA 或租户边界 | host、trigger/scale group 和 identity 可能不足以表达隔离需求。 |
| 发布节奏不同 | 同一 Function App 内共享发布会增加回归面和冷启动/回滚成本。 |

如果这些信号不明显，使用 MAF Durable Extension on Azure Functions
可能仍是合理路线； 它换来的是 Azure Functions hosting、Durable Task-backed
recovery 和 MAF graph 建模之间的集成便利。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| wiki | [Azure Functions Scale and Hosting 文档](../sources/azure-functions/scale-hosting-docs.md) | Azure Functions hosting option 会影响 function app 的 scale、资源、网络/容器支持和成本；实际 scale 粒度依赖 hosting plan 与 trigger/scale group。 |
| wiki | [Durable Task Hosting Model 文档](../sources/azure-durable-functions/hosting-model-docs.md) | Durable Functions 与 standalone Durable Task SDKs 共享核心 durable execution capabilities，但 hosting/scaling/deployment 不同。 |
| wiki | [Durable Task Scheduler 文档](../sources/microsoft-durable-task/scheduler-docs.md) | Scheduler dispatches orchestrator/activity/entity work items，connected apps 可并行处理 work items，并与 scheduler 独立伸缩。 |
| wiki | [Microsoft Agent Framework Durable Workflow Registration 源码](../sources/microsoft-agent-framework/durable-workflow-registration-source.md) | MAF Durable Extension 支持 additive 多 workflow 配置，注册 graph workflows、activities、agents 和 subworkflows。 |
| wiki | [Microsoft Agent Framework Azure Functions Durable Workflow Metadata Transformer 源码](../sources/microsoft-agent-framework/azure-functions-durable-workflows-metadata-transformer-source.md) | Azure Functions hosting 路径遍历 configured durable workflows 并生成 per-workflow / per-executor metadata。 |
| wiki | [Microsoft Agent Framework Durable Executor Dispatcher 源码](../sources/microsoft-agent-framework/durable-executor-dispatcher-source.md) | ordinary executor、agent、subworkflow、request port 到 activity/entity/sub-orchestration/external event 的运行时映射。 |
| wiki | [Temporal Task Queues 文档](../sources/temporal/task-queues-docs.md) | Temporal Task Queue 的轻量、按需、load balancing、routing、throttling、worker polling 和 partitions 语义。 |
| wiki | [Temporal Workers 文档](../sources/temporal/workers-docs.md) | Temporal Worker Entity/Process 与 Task Queue、Temporal Service 和外部 worker fleet 的关系。 |
| wiki | [Temporal Child Workflows 文档](../sources/temporal/child-workflows-docs.md) | Child Workflow 是独立 Workflow Execution，有自己的 Event History，可用于大问题或资源实体拆分。 |
| wiki | [Temporal Activities 文档](../sources/temporal/activities-docs.md) | Temporal Activity 是单一外部工作单元，适合承载副作用和可重试工作。 |
| user | 用户在 2026-06-16 追问：“MAF Durable Function Apps 这种做法会比 Temporal 在 scale out 方面更早遇到瓶颈？比如说图多起来之后。或者说资源利用效率更低”。 | 确定本页问题边界和判断需求；不是第三方技术事实证据。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| 多 graph、异构 workload 下，MAF Durable Function Apps 更容易先遇到 scale-out 粒度和资源利用效率问题。 | Azure Functions Scale and Hosting；Durable Task Hosting Model；MAF Metadata Transformer；MAF Registration；Temporal Task Queues；Temporal Workers。 | 这是基于机制的架构判断，不是性能 benchmark；Azure Functions 实际 scale 粒度依赖 hosting plan 与 trigger/scale group，少量同质 graph 或手动拆分 Function Apps/worker apps 时差距可能缩小。 |
| MAF Azure Functions hosting 可让一个 host 配置包含多个 durable workflows，这排除一图一 Function App 的必然关系，但也会带来 host-level coupling。 | MAF Metadata Transformer；MAF Registration。 | 该证据不证明单个 graph executor 可任意跨 Function Apps 自动 partition。 |
| Temporal 的 Task Queue/Worker 模型提供更自然的 dispatch/resource-pool 边界。 | Temporal Task Queues；Temporal Workers。 | 同一 Task Queue 上 worker 注册通常必须一致；Task Queue 设计和 worker 治理仍需人工负责。 |
| 逻辑子图本身不决定扩容；只有变成 runtime work item、queue、worker pool、sub-orchestration/child workflow 或 host/backend 边界时，才影响 partition 和资源利用。 | MAF Executor Dispatcher；Temporal Task Queues；Temporal Child Workflows；Temporal Activities；Durable Task Scheduler。 | 这是跨系统归纳；具体产品 API 细节需要按版本复查。 |
| Durable Task Scheduler 和 Azure Functions hosting 仍能横向扩展，不能把本文结论写成 MAF Durable Functions 无法 scale。 | Durable Task Scheduler；Azure Functions Scale and Hosting；Durable Task Hosting Model。 | 文档支撑扩展机制，但不提供当前场景的容量上限、成本或冷启动数据。 |
| Temporal 的优势不是自动切 graph，而是显式 Task Queue、Worker Process、Activity 和 Child Workflow 让资源池和 history boundary 更容易被架构设计表达。 | Temporal Task Queues；Temporal Workers；Temporal Child Workflows；Temporal Activities。 | 这会带来 queue 命名、worker 注册、版本、容量和运维复杂度。 |
