---
schema_version: 2
page_type: analysis
title: "Azure Durable Functions 与 MAF Durable Extension 的关系"
status: active
created: 2026-06-16
updated: 2026-06-16
summary: "解释 Azure Durable Functions、Durable Task Scheduler 与 Microsoft Agent Framework Durable Extension 的分层关系。"
maintenance:
  edit_policy: update
validation:
  body_contract: analysis-answer-memo
tags:
  - azure-durable-functions
  - durable-task
  - microsoft-agent-framework
  - durable-extension
---

## 问题

本页回答一个窄问题：Azure Durable Functions 和 Microsoft Agent Framework Durable
Extension 是不是同一回事？
如果使用 MAF Durable Extension， 业务 workflow 的语义主体到底是 Azure Durable
Functions orchestrator function， 还是 MAF workflow？

读者假设：熟悉 MAF 的 workflow、agent、executor、HITL 等概念， 但不了解 Azure
Functions、Durable Functions 和 Durable Task Scheduler 体系。
本页只讨论 graph-based MAF workflows 与 Durable Extension 的关系， 并解释
Function App/host 与 graph 的部署对应边界。
不外推到 MAF functional workflow surface、未来 API surface、MAF 是否适合裸金属
buildout 主 process manager，或 Azure 平台采购建议。
多 graph 场景下的 scale-out 与资源利用效率判断，另见
[MAF Durable Function Apps 与 Temporal 的 Scale-out 边界](maf-durable-functions-vs-temporal-scale-out.md)。

## 答案

这次连续困惑的共性问题是：把 **MAF 建模单元、Durable Task 运行时单元、 Azure
Functions 部署单元、Scheduler/backend 单元** 混成了一个一一对应的“运行单元”。
只要这四类 unit 没有拆开，读者就会自然追问：

- 一个 MAF Graph 是不是必然对应一个 Function App？
- Durable Task activity 到底是不是 Azure Functions 的概念？
- Scheduler 是不是在解释 orchestrator？
- MAF workflow 和 Durable Functions orchestrator function 到底谁才是 workflow？

它们不是同一层东西。 更准确的模型是：

```text
作者/业务建模层
  MAF graph workflow / executor / agent / subworkflow / request port

适配层
  MAF Durable Extension
  - 把 MAF graph workflow 注册/映射到 Durable Task orchestration
  - 把 executor 映射到 activity / entity / sub-orchestration / external event

durable execution 层
  Durable Task orchestration / activity / entity / timer / external event

compute host 层
  Azure Functions hosting 或 self-hosted/BYOC worker

durable backend/storage 层
  Durable Task storage/backend provider 持久化 orchestration history、entity state、
  internal messages；当前 MAF self-hosted 证据指向 Durable Task Scheduler backend，
  Scheduler 还负责派发 work items
```

这里的 Function App 可以先理解成 Azure Functions 中一组 functions 的部署、
配置和宿主边界；它不是 workflow 或 agent 本身。

因此，在 MAF Durable Extension 场景中，
**MAF workflow 是作者和业务语义层的 workflow 语义主体**；Durable Task
orchestration 是运行时持久化和调度层的表示。
如果直接写 Azure Durable Functions，作者面对的 workflow 语义主体才是
orchestrator function。

一句话： **Azure Durable Functions 是 Durable Task 在 Azure Functions 上的
stateful workflow programming/hosting surface；MAF Durable Extension 是把 MAF
graph workflow 接到 Durable Task-backed execution 的集成层。**

## 先分清四种 unit

阅读 MAF Durable Extension 文档时，先不要把 MAF Graph、Durable orchestration、
Function App 和 Durable Task Scheduler 看成同一种东西。

| unit 类型 | 回答的问题 | 例子 | 是否与其它 unit 天然一一对应 |
| --- | --- | --- | --- |
| 作者/业务建模单元 | 业务流程怎么表达。 | MAF graph workflow、executor、agent、subworkflow、request port。 | 否。一个建模单元可能映射到一个或多个 runtime handlers/work items，具体 topology-dependent。 |
| durable runtime 单元 | 持久执行时调度什么、等待什么、恢复什么。 | orchestration、activity、entity、sub-orchestration、external event。 | 否。它是运行时表示，不是部署包。 |
| compute/deployment 单元 | 代码部署到哪里、用什么身份、配置、包和宿主生命周期运行。 | Azure Functions Function App、self-hosted worker app/process。 | 否。它可以承载多个已注册 workflows，也可以复制为多个 worker/hosts；实际伸缩粒度取决于 hosting plan、trigger/scale group 和部署拓扑。 |
| backend/storage 单元 | 状态、history、messages 和 work item dispatch 由谁负责。 | Durable Task Scheduler、Azure Storage、MSSQL、Netherite 等 storage/backend provider。 | 否。它不是 workflow 作者，也不是 Function App。 |

本页前一版已经说明 “MAF workflow 是语义主体”，但没有充分回答
unit/cardinality/deployment correspondence。
下面补齐这些读者最容易卡住的问题。

## 分层解释

### Azure Durable Functions 是什么

Azure Durable Functions 是 Azure Functions 的扩展，用于在 serverless environment
中构建 stateful workflows。
直接使用它时，开发者编写 orchestrator functions、 activity functions 和 entity
functions。
orchestrator function 以代码定义长期、 可靠的 orchestration instance，并通过
Durable Task 的 event sourcing、 execution history 和 replay 恢复本地流程状态。

这意味着 Azure Durable Functions 提供的是一种作者可直接使用的 durable workflow
编程模型。
它不是 Durable Task Scheduler 本身，也不是所有 Durable Task 应用的唯一 hosting
model。
Durable Task 还支持 standalone SDKs，让 worker 运行在 Azure Functions 之外的
compute platform 上，但这些 SDK 仍连接 Durable Task Scheduler managed backend。

还需要分清 Durable Functions 与 backend/storage provider。
Durable Functions 支持 Durable Task Scheduler、Azure Storage、Netherite、 MSSQL
等 storage provider；因此不能把 Azure Durable Functions 简化为 “一定使用
Scheduler”。
Scheduler 是 Durable Task 体系中的重要 managed backend， 但不是 Durable
Functions 唯一 storage/backend 选项。

### Durable Task activity 是什么

先消除一个命名误会： **activity 不是 plain Azure Functions 的基础概念**。
Plain Azure Functions 主要讨论 function、trigger、binding 和 Function App；
activity function 是 Durable Functions 这个扩展引入的 function role。

在 Durable Task 层，activity 是 orchestrator 调用的 durable runtime 工作项。
orchestrator 通过 `CallActivityAsync`、`call_activity`、`Invoke-DurableActivity`
等 API 调用 activity；runtime/backend 负责调度这个 work
item、记录完成或失败结果， 并让 orchestrator replay 时从 execution history
读取已完成 activity 的结果， 而不是重复执行已经完成的 activity。

所以在 MAF Durable Extension 中说“ordinary executor 注册为
activity”，准确含义是： MAF 把 ordinary executor 包装成 Durable Task activity。
它不是说普通 Azure Functions 本来就有一个通用的 activity 概念，也不是说所有 MAF
executor 都是 activity。
agent executor、subworkflow 和 request port 分别走 Durable Entity、
sub-orchestration 和 external event 路径。

### Durable Task Scheduler 做什么

Durable Task Scheduler 是 backend，不是业务 workflow 作者。
它派发 orchestrator、activity 和 entity work items，管理 orchestrations/entities
state，并把 work items push 给 connected apps。

所以 Scheduler 不负责“写 orchestrator”或决定业务下一步。
真正的控制逻辑在应用侧：直接使用 Durable Functions 时在 orchestrator function
中； 使用 MAF Durable Extension 时在 MAF workflow 和 extension 的 Durable Task
映射中。
Scheduler 负责让这些控制逻辑能够被持久化、唤醒、派发和恢复。

### MAF Durable Extension 是什么

MAF Durable Extension 是 Microsoft Agent Framework 的持久化执行集成层。
它把 Durable Task-backed durability 引入 Agent Framework agents、 multi-agent
orchestrations 和 graph-based workflows，并支持 Azure Functions 与 self-hosted
worker 两种 hosting model。

在 MAF Durable Extension 中，作者通常不直接手写底层原生 orchestrator function。
作者建模的是 MAF graph workflow。
源码证据显示，Durable Extension 会配置 durable graph workflows，注册
orchestrations 和 activities；普通 executor 被注册为 Durable Task
activity，agent、subworkflow 和 request port 走专门 dispatch 路径。
进一步的 dispatcher 源码显示，普通 executor 使用 `CallActivityAsync`，
subworkflow 使用 `CallSubOrchestratorAsync`，agent executor 走 Durable Entity，
request port 等待 external event。

这就是为什么不能把它简单说成“Azure Durable Functions 但是每个 Function App
里面都是 MAF”。
更准确地说，如果选择 Azure Functions hosting， MAF durable workflow 可以部署在
Azure Functions 应用运行面上； 但 Function App 是 hosting/deployment/trigger
容器，不是 MAF workflow 的业务本体。
在这个 hosting 选择下，业务作者仍建模 MAF graph workflow， 而不是改为手写底层
orchestrator function。

### MAF Graph 与 Function App 的 cardinality：先分清 replica 和 partition

**MAF Azure Functions hosting 的开源实现已经能排除“一图一 Function
App”的必然关系，但这个结论只解决 host 可承载多个 workflows 的问题；
它不能被误读成单个 graph 自动被拆成多个 Function Apps partition。**

Function App 是 Azure Functions 的 host/deployment/config/package/identity
边界；实际伸缩粒度还取决于 hosting plan、trigger/scale group 和 runtime/backend
配置；MAF graph workflow 是 authoring/modeling 边界。
使用 MAF Durable Extension 时，应用启动配置会把 graph workflows、ordinary
executors、agents 和 subworkflows 注册成 Durable Task runtime handlers。
源码证据显示，durable options 支持 additive 配置，多次调用会组合配置；在 base
DurableTask worker registration path 中，注册逻辑会遍历已配置
workflows，并递归把 subworkflows 注册为 separate orchestrations。
Azure Functions hosting 路径也有专门的 function metadata transformer：它遍历
`workflowOptions.Workflows`，为每个已配置 workflow 注册 orchestration trigger 和
HTTP trigger，并为 executor 注册 activity/entity trigger metadata。

因此，cardinality 要按方向拆开说：

| 关系 | 当前结论 | 含义 |
| --- | --- | --- |
| Function App / host 配置 -> MAF durable workflows | **1:N** | 一个 host 配置可以包含多个 durable workflows；Azure Functions metadata transformer 会遍历 `workflowOptions.Workflows` 并为每个 workflow 生成 trigger metadata。 |
| 同一个 MAF graph definition -> 多个 Function Apps / app instances | **1:N replica** | 可以把同一 graph definition 作为重复部署/副本放到多个 Function Apps 或 instances；这是 replica，不是把 graph 内部子图划给不同 Function Apps。 |
| MAF graph 内部 subgraph / executor -> Function Apps | **没有自动 1:N partition 证据** | 当前证据支持 executor/subworkflow 被映射成 Durable Task activity/entity/sub-orchestration 等 runtime handlers；不支持“任意 executor 自动跨 Function Apps 分区”。 |
| Function App / worker app -> Durable Task backend/task hub | **topology-dependent** | 多个 apps 可以连接 backend 并处理 work items，但要结合 task hub/backend、registration、identity、网络和 routing 配置验证。 |

所以，“一个 MAF Graph 不必然对应一个 Function App”不是在说
`Graph -> Function Apps` 天然是 partitioned 1:N。 更精确的说法是：

- **Function App / host -> workflows 可以是 1:N。**
- **同一 graph definition -> 多个 Function Apps 只能先理解为 replica /
  重复部署。**
- **graph 内部 subgraph/executor -> Function Apps 的 partition
  不能从当前证据推出。**
- **在 base DurableTask worker registration path 中，subworkflow 会成为 separate
  orchestration registration，但 separate orchestration registration 也不等于
  separate Function App partition。**

但反过来，也不要在没有额外证据时声称“单个 MAF Graph 内部任意 executor
可以无条件拆到多个 Function Apps 运行”。
这种拆分需要额外验证 worker routing、task hub/backend 配置、跨 app registration
和调度语义。
多 Function Apps / worker apps 更安全的理解是部署拓扑选择：
可以按服务边界、发布生命周期、权限/identity、伸缩、成本、网络隔离和 backend/task
hub 边界来拆，但这不是 MAF Graph 本身强制给出的语义。

### Scale-out 与资源利用不是由逻辑子图决定

用户后续追问的另一个共性问题是：如果 graph 多起来，MAF Durable Function Apps
是否比 Temporal 更早遇到 scale-out 或资源利用效率瓶颈。
这里仍要沿用同一分层模型： **逻辑子图只是 authoring/modeling 层概念；是否
partition、是否能细粒度扩容， 取决于它是否被映射成独立 runtime work
item、dispatch boundary、history/state boundary 或 host/resource-pool
boundary。**

在 MAF Durable Extension 中，ordinary executor、agent executor、subworkflow 和
request port 分别映射到 activity、entity、sub-orchestration 和 external event；
这些会影响 Durable Task 层的调度和恢复。
但 Azure Functions hosting 下的 Function App 仍是
host/deployment/config/package/identity 边界；实际 scale 粒度 还取决于 hosting
plan、trigger/scale group 和 runtime/backend 配置。
多个 workflows 放进 同一 Function App/host
时，部署包、依赖、metadata、冷启动、身份和 host 资源会更容易 一起移动。

因此不能说 MAF Durable Functions 无法横向扩展；Durable Task Scheduler 可以
dispatch work items，connected apps 也可以并行处理。
但如果 graph 数量多、冷热不均、依赖异构 或 SLA/租户边界不同，MAF Durable
Function Apps 的默认资源池拓扑不天然按单个 graph 拆分，需要人为拆 Function
Apps、worker apps、backend/task hub、身份和网络边界。
Temporal 的 Task Queue / Worker Process 模型则把 dispatch/resource-pool boundary
作为更直接的一等对象。 详细比较见
[MAF Durable Function Apps 与 Temporal 的 Scale-out 边界](maf-durable-functions-vs-temporal-scale-out.md)。

## 两种使用方式的本体差异

| 使用方式 | 作者写的 workflow 语义主体 | 底层持久化执行表示 | backend 职责 |
| --- | --- | --- | --- |
| 直接使用 Azure Durable Functions | Orchestrator function，配套 activity/entity functions。 | Durable Task orchestration、activity、entity、timer、external event。 | storage provider 持久化 runtime state/history/messages；Scheduler 等 backend 负责相应调度/管理能力。 |
| 使用 MAF Durable Extension + Azure Functions hosting | MAF graph workflow、executor、agent、subworkflow、request port。 | 由 extension 映射出的 Durable Task orchestration、activity/entity/sub-orchestration/external event。 | backend 只负责 Durable Task 层的持久化、唤醒和派发；不拥有业务 workflow 定义。 |
| 使用 MAF Durable Extension + self-hosted/BYOC worker | MAF graph workflow、executor、agent、subworkflow、request port。 | 同样是 Durable Task-backed runtime 表示。 | self-hosted worker 自管 compute；当前证据显示 Durable Task Scheduler 仍是 managed backend。 |

这张表的关键点是：同一个 Durable Task runtime 对象可能由不同作者层生成。
直接写 Durable Functions 时，作者层就是 orchestrator function； 使用 MAF Durable
Extension 时，作者层是 MAF workflow，orchestration 是 extension
生成和维护的运行时映射。

## 术语映射

| MAF / Azure 词 | 所属层 | 在本文中的含义 |
| --- | --- | --- |
| MAF graph workflow | 作者/业务建模层 | 业务流程图和控制结构；不是 Function App。 |
| ordinary executor | 作者/业务建模层，经 MAF Durable Extension 适配 | 当前 .NET graph workflow Durable Extension 中映射为 Durable Task activity。 |
| agent executor | 作者/业务建模层，经 MAF Durable Extension 适配 | 走 Durable Entity 路径，不应简化为 ordinary activity。 |
| subworkflow | 作者/业务建模层，经 MAF Durable Extension 适配 | 注册/调用为 sub-orchestration，拥有独立 orchestration instance。 |
| request port / HITL | 作者/业务建模层，经 MAF Durable Extension 适配 | 映射到 external event 等待路径。 |
| activity function | Durable Functions 层 | Durable Functions extension 引入的 function role；被 orchestrator 调用。 |
| activity | Durable Task 层 | Durable runtime 的 work item 类型；plain Azure Functions 本身没有这个通用概念。 |
| Function App | compute/deployment 层 | 一组 functions 的部署、配置、host、package 和 identity 边界；不是 workflow 或 graph。实际 scale 粒度依赖 hosting plan、trigger/scale group 和 runtime/backend 配置。 |
| Durable Task Scheduler | backend/storage 层 | 管理 durable state 并派发 orchestrator/activity/entity work items；不解释业务流程图。 |

## 容易混淆的说法

“MAF Durable Extension 就是 Azure Durable Functions”不准确。
二者共享或借用 Durable Task-backed execution 语义，但一个是 Azure Functions 上的
durable workflow programming/hosting surface，另一个是 MAF 到 Durable Task
的集成层。

“MAF Durable Extension 依赖 Azure Durable Functions”也不精确。
官方文档显示它支持 Azure Functions 和 self-hosted worker 两种 hosting model； 在
self-hosted 模型中，host process 启动 Durable Task worker 并连接 Durable Task
Scheduler backend。
也就是说，它依赖 Durable Task-backed infrastructure， 但不必把所有部署都理解成
Azure Functions-hosted Durable Functions。

“Durable Task Scheduler 负责 orchestrator”同样不准确。
Scheduler 是持久化和调度后端；业务控制逻辑由应用侧的 orchestrator code 或 MAF
Durable Extension 的 mapping/dispatcher 执行。
Scheduler 可以让它们重放、 恢复和派发 work item，但不替业务定义流程图。

## 影响

对熟悉 MAF 的读者，最实用的理解方式是：

- 你仍然从 MAF workflow 建模业务流程，不需要先把思维切换成手写 Durable Functions
  orchestrator function。
- 启用 Durable Extension 后，MAF workflow 会获得 Durable Task-backed 的
  checkpoint/recover、跨 stateless workers 恢复和 HITL 等 durable execution
  能力。
- 你需要明确 hosting 选择：Azure Functions hosting 和 self-hosted/BYOC worker
  是部署/运行面差异，不是业务 workflow 语义主体差异。
- 你需要明确部署粒度：Function App/worker app 是 host 边界， 不是 MAF Graph
  的天然一一对应物；一个 host 配置可以包含多个 durable workflows， 但单个 graph
  内部跨多个 Function Apps 拆分需要额外设计和验证。
- 你需要明确 scale-out 粒度：逻辑子图不自动成为资源池 partition；多 graph、
  异构 workload 下的资源利用效率取决于 runtime work item、dispatch boundary、
  host/scale group/resource-pool 和 backend/task hub 的拆分。
- 你需要明确 backend 选择和约束：当前证据中的 self-hosted worker 仍连接 Durable
  Task Scheduler managed backend；这不同于完全自带生产级 durable backend。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| wiki | [Azure Functions Overview 文档](../sources/azure-functions/overview-docs.md) | Azure Functions 的 serverless/event-driven 定位、triggers/bindings 和 HTTP trigger REST endpoint 场景。 |
| wiki | [Azure Durable Functions Overview 文档](../sources/azure-durable-functions/overview-docs.md) | Durable Functions 作为 Azure Functions stateful workflow extension 的定位，以及 orchestrator/activity/entity functions、runtime state/checkpoint/retry/recovery。 |
| wiki | [Durable Task Orchestrations 文档](../sources/azure-durable-functions/orchestrations-docs.md) | Orchestrator function、long-running workflow、event sourcing、execution history、checkpoint/replay、sub-orchestration 和 deterministic code 语义。 |
| wiki | [Durable Task Hosting Model 文档](../sources/azure-durable-functions/hosting-model-docs.md) | Durable Functions 与 standalone Durable Task SDKs 的 hosting/scaling/deployment 差异，以及两者共享核心 durable execution capabilities。 |
| wiki | [Durable Task Storage Providers 文档](../sources/azure-durable-functions/storage-providers-docs.md) | Durable Functions / Durable Task SDKs 的 storage providers，以及 orchestration history、entity state 和 internal messages 持久化边界。 |
| wiki | [Azure Functions Scale and Hosting 文档](../sources/azure-functions/scale-hosting-docs.md) | Azure Functions function app 的 hosting option、scale、资源和网络/容器支持边界；实际 scale 粒度依赖 plan 与 trigger/scale group。 |
| wiki | [Durable Task SDKs Overview 文档](../sources/microsoft-durable-task/sdk-overview-docs.md) | Standalone Durable Task SDKs 可在 Azure Functions 之外运行 worker，但仍连接 Durable Task Scheduler managed backend。 |
| wiki | [Durable Task Scheduler 文档](../sources/microsoft-durable-task/scheduler-docs.md) | Scheduler 作为 backend dispatch orchestrator/activity/entity work items，管理 durable state，并通过 gRPC 连接 apps。 |
| wiki | [Microsoft Agent Framework Durable Extension 文档](../sources/microsoft-agent-framework/durable-extension-docs.md) | MAF Durable Extension 的 Durable Task-backed execution、Azure Functions/self-hosted hosting、checkpoint/recover、HITL 和 Scheduler backend 边界。 |
| wiki | [Microsoft Agent Framework Durable Workflow Registration 源码](../sources/microsoft-agent-framework/durable-workflow-registration-source.md) | Durable Extension 将 graph workflows 注册为 orchestrations，将普通 executors 注册为 activities，并为 agent/subworkflow/request-port binding 使用专门 dispatch 路径。 |
| wiki | [Microsoft Agent Framework Azure Functions Durable Workflow Metadata Transformer 源码](../sources/microsoft-agent-framework/azure-functions-durable-workflows-metadata-transformer-source.md) | MAF Azure Functions hosting 中为每个 configured durable workflow 生成 orchestration/HTTP trigger metadata，并为 executor 生成 activity/entity trigger metadata。 |
| wiki | [Microsoft Agent Framework Durable Executor Dispatcher 源码](../sources/microsoft-agent-framework/durable-executor-dispatcher-source.md) | MAF executor 到 activity/entity/sub-orchestration/external-event 的细粒度映射。 |
| wiki | [MAF Durable Function Apps 与 Temporal 的 Scale-out 边界](maf-durable-functions-vs-temporal-scale-out.md) | 多 graph、异构 workload 下 Function App hosting topology 与 Temporal Task Queue/Worker Process 模型的 scale-out 边界分析。 |
| user | 用户在 2026-06-16 的连续提问：MAF Durable Extension 是否依赖 Azure Durable Functions、Durable Task Scheduler 是否只是 backend、workflow 本体到底是谁，继续追问 MAF Graph 与 Function App 的部署对应关系、Durable Task activity 是否是 Azure Functions 概念，以及 graph 多起来后 MAF Durable Function Apps 是否比 Temporal 更早遇到 scale-out 或资源利用效率瓶颈；随后指出 “MAF Azure Functions hosting 的开源实现已经能排除‘一图一 Function App’的必然关系” 一节仍未更新 replica/partition 表述。 | 确定本页问题边界和读者困惑；不是第三方产品事实证据。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| 直接使用 Azure Durable Functions 时，作者面对的 workflow 语义主体是 orchestrator function。 | Azure Durable Functions Overview；Durable Task Orchestrations。 | 不覆盖所有语言 SDK 的语法细节；本页只讨论抽象层级。 |
| 使用 MAF Durable Extension 时，作者和业务语义层的 workflow 语义主体是 MAF graph workflow，底层 Durable Task orchestration 是运行时映射。 | MAF Durable Extension 文档；Durable Workflow Registration 源码；Durable Executor Dispatcher 源码。 | 当前源码证据是 .NET 实现；functional workflow surface 和未来版本需另行取证。 |
| Durable Task Scheduler 不是 orchestrator 作者或业务流程解释器，而是 managed backend，负责 durable state 管理和 work item dispatch；history/message 持久化属于 Durable Task storage provider 边界。 | Durable Task Scheduler 文档；Durable Task Storage Providers；Durable Task SDKs Overview。 | Scheduler dashboard 可观察和管理 runtime instances，但不替代业务 dashboard 或领域事实库。 |
| MAF Durable Extension 可使用 Azure Functions hosting，也可使用 self-hosted/BYOC worker；因此不能简单写成“就是 Azure Durable Functions”。 | MAF Durable Extension 文档；Durable Task Hosting Model；Durable Task SDKs Overview。 | self-hosted/BYOC 指 worker compute 自管；当前证据仍显示连接 Durable Task Scheduler managed backend，不等于完全离线或完全自带后端。 |
| Azure Durable Functions 与 MAF Durable Extension 的关系应按 authoring/modeling、adapter/mapping、durable runtime、compute host、durable backend/storage 五层理解。 | 上方所有证据单元综合。 | 这是分析归纳，不是官方术语；用于避免把 hosting surface、workflow source 和 backend scheduler 混成同一层。 |
| 用户的共性困惑来自把 authoring/modeling unit、durable runtime unit、compute/deployment unit 和 backend/storage unit 混成一一对应运行单元。 | 用户提问；上方所有证据单元综合。 | 这是对问题模式的分析归纳，用于组织解释结构；不是官方产品术语。 |
| MAF Graph 与 Function App 的 cardinality 必须区分 host-to-workflows、graph replica 和 graph partition：一个 host 配置可包含多个 durable workflows；同一 graph definition 跨多个 Function Apps 只能先理解为 replica；当前证据不支持 graph 内部 subgraph/executor 自动跨 Function Apps partition。 | Azure Functions Durable Workflow Metadata Transformer 源码；Durable Workflow Registration 源码；MAF Durable Extension 文档；用户对 replica/partition 表述的纠正。 | replica/partition 是本文的架构解释；实际跨 app 部署仍需验证 worker routing、task hub/backend、registration、identity 和网络配置。 |
| Durable Task activity 不是 plain Azure Functions 的基础概念；它在 Durable Functions 中表现为 activity function，在 Durable Task 中是可调度 work item，在 MAF Durable Extension 中是 ordinary executor 的一种 runtime 映射。 | Azure Functions Overview；Azure Durable Functions Overview；Durable Task Orchestrations；Durable Workflow Registration 源码；Azure Functions Durable Workflow Metadata Transformer 源码；Durable Executor Dispatcher 源码；Durable Task Scheduler 文档。 | 该映射限于当前 graph workflow Durable Extension/.NET 证据；agent、subworkflow 和 request port 走专门路径。 |
| 逻辑子图不自动决定 partition 或扩容；多 graph 场景下的资源利用效率取决于 runtime work item、dispatch boundary、host/scale group/resource-pool 和 backend/task hub 的拆分。 | Durable Task Scheduler 文档；Durable Executor Dispatcher 源码；Azure Functions Durable Workflow Metadata Transformer 源码；Azure Functions Scale and Hosting；MAF Durable Function Apps 与 Temporal 的 Scale-out 边界。 | 这是机制归纳；具体性能和成本仍需 benchmark、host plan、backend capacity 和部署拓扑验证。 |
