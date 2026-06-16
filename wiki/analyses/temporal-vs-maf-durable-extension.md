---
schema_version: 2
page_type: analysis
title: "Temporal 与 MAF Durable Extension 的能力边界"
status: active
created: 2026-06-16
updated: 2026-06-16
summary: "从运行时能力层比较 Temporal 与启用 Durable Extension 的 Microsoft Agent Framework。"
maintenance:
  edit_policy: update
validation:
  body_contract: analysis-answer-memo
tags:
  - temporal
  - microsoft-agent-framework
  - durable-extension
  - workflow
---

## 问题

本页回答：如果不看产品术语，而看运行时能力和源码机制，Temporal 与启用
Durable Extension 的 Microsoft Agent Framework（MAF）到底是不是同一类能力？

本页比较的是 Temporal Server + Task Queue/Worker 协议 + SDK Workflow/Activity
模型，以及 `microsoft/agent-framework` 中 .NET graph workflow 的 Durable Task-backed
durable path。它不比较未启用 Durable Extension 的 MAF core workflow surface，也不做
benchmark、成本或采购建议。

## 答案

**两者都能承载长运行、可恢复、可外部交互的 workflow，但能力边界不等价。**

Temporal 的基本能力单元是 Workflow Execution 的 Event History、server mutable state、
Workflow/Activity Task、Task Queue 和 Worker command 协议。Worker replay workflow code
并返回 commands；History service 校验 commands，把它们物化为 history events、pending
state 和 tasks；Matching service 再把 tasks 交给 polling workers。

MAF Durable Extension 的基本能力单元是 MAF graph/agent surface 到 Durable Task primitives
的适配映射：graph runner 在 Durable Task orchestration 内执行 superstep loop；ordinary
executor 走 activity；agent executor 走 Durable Entity；RequestPort 走 external event；
subworkflow 走 sub-orchestration；Azure Functions hosting 再生成相应 metadata。

所以最短结论是：

- **Temporal 更像通用 durable workflow runtime。** 它的一等语义围绕 Event History、Task
  Queue、Worker Versioning、Signal/Update/Query、Continue-As-New/Reset 和 visibility
  展开。
- **MAF Durable Extension 更像 agent/workflow framework 的 durable adapter。** 它把 MAF
  graph 与 agent 抽象接入 Durable Task-backed execution，尤其适合 MAF-native graph、
  RequestPort/HITL 和 AIAgent session；但当前源码不支持把它写成完整保真所有 MAF graph
  语义，也不支持把 graph/executor resource pool 写成 Temporal Task Queue 那样的一等调度面。
- **底层 Durable Task 能力不能自动归因给 MAF graph surface。** 只有 MAF Durable Extension
  已映射、已暴露或明确调用的能力，才计入本页的 MAF 结论。

## 机制模型

### 1. 控制表示与执行解释器

Temporal 的控制规范是“可重放 workflow code + Event History + worker commands”。History
service 接收 Workflow Task completion 后，校验 command sequence，并处理
`SCHEDULE_ACTIVITY_TASK`、`START_TIMER`、`START_CHILD_WORKFLOW_EXECUTION`、
`CONTINUE_AS_NEW_WORKFLOW_EXECUTION`、`SIGNAL_EXTERNAL_WORKFLOW_EXECUTION` 和 update
protocol messages 等 commands。服务端决定 command 是否合法，并把它们提交到 Event
History、mutable state 和 matching tasks。

MAF Durable Extension 的控制规范是 MAF graph。`DurableWorkflowRunner` 在 Durable Task
orchestration context 中构造 `WorkflowGraphInfo` 和 `DurableEdgeMap`，把输入放入 start
executor queue，然后以最多 100 个 supersteps 循环：收集有消息的 executor、并行 dispatch、
合并状态、路由输出到后继 executor。`DurableExecutorDispatcher` 再把 executor 分派到
activity、entity、sub-orchestration 或 external event。

关键差异不在“代码 vs 图”的表面，而在解释器归属：Temporal 是 worker code 产生 commands、
server 校验并物化 history/state/tasks；MAF Durable Extension 是 Durable orchestration 内的
graph runner 解释 MAF graph 的 durable projection。

MAF 的语义保真限制是本页最重要的源码发现之一：

- `WorkflowBuilder.AddFanInBarrierEdge` 和 `FanInEdgeData` 声明的是等所有 source 有数据；
  durable runner 只在目标 queue 当前 `Count > 1` 时聚合已有消息，不等待所有 predecessor。
- `FanOutEdgeData` 保存 `EdgeAssigner` / target selector；`WorkflowAnalyzer` 与
  `DurableEdgeMap` 只保留 successor/sink 信息和 direct edge condition，未使用 selector，
  多 successor durable routing 更接近 broadcast。
- MAF core workflow context 有 targeted `SendMessageAsync(targetId)` 语义；durable runner
  主要按 edge map 路由 executor output，不能把 per-message target routing 写成完整保真。
- 多前驱 direct edge 与 fan-in barrier 在 durable projection 中容易被 predecessor count
  压扁，fan-in 聚合也会把来源/类型信息弱化为序列化消息集合。

因此可以说 MAF Durable Extension 有真实 graph-to-Durable Task mapping，但不能说它完整复刻
MAF in-process graph runtime。

### 2. 状态真源与恢复对象

Temporal 的恢复对象是 Workflow Execution。服务端 mutable state 明确持有 pending activities、
timers、child executions、signals、request-cancel info、signal request IDs、execution
info/state、history builder 和待插入 tasks。Event History 是 durable recovery 与 audit 的基础；
worker 通过 replay history 重建本地 workflow 状态，再继续生成 commands。

MAF Durable Extension 的恢复对象分三层：

1. Durable Task runtime 负责 orchestration/activity/entity 层的 durable execution。
2. `DurableWorkflowRunner.SuperstepState` 在 orchestration 中保存 message queues、last results、
   shared state、accumulated events 和 live status。
3. `AgentEntity` 使用 Durable Entity state 保存 agent conversation history 与 TTL。

所以 MAF 并不是没有持久状态，也不是没有 replay。更准确的说法是：两者都属于 durable
orchestration/replay 家族，都会把外部事实持久化，再用确定性代码恢复运行态；差异在于
Temporal 把 Event History、mutable state、Reset、visibility 和 task dispatch 投影成更一等的平台面，
而 MAF Durable Extension 把 durable runtime history 隐在 Durable Task 层，并在 Agent Framework
层暴露 `SuperstepState`、custom status、shared state 和 agent entity state。

custom status 不能被写成 MAF 的完整事实源。源码注释说明 custom status 是运行中外部客户端可读的
orchestration state，完成后会被 framework 清理；runner 因而还把 events 放入最终
`DurableWorkflowResult`。

### 3. 调度与放置单元

Temporal 的调度/放置一等对象是 Task Queue 与外部 Worker Process。`matching_engine.go`
中的 `AddWorkflowTask` / `AddActivityTask` 会按 namespace、task queue、task type 构造
partition，并把 `TaskInfo` 交给 task queue partition manager；`PollWorkflowTaskQueue` 和
`PollActivityTaskQueue` 由 workers 长轮询取 task，并处理 sticky queue、build id / deployment
directive、obsolete task drop 和 history start record。

MAF Durable Extension 的调度/放置单元来自 Durable Task 和 host。`RegisterTasksFromOptions`
把 graph workflows 注册为 orchestrations，把 ordinary executors 注册为 activities，并把 agent
entities 注册到 Durable Task registry。Azure Functions metadata transformer 遍历同一 host 配置中的
workflows，为 workflow、HTTP/status/respond、activity 和 entity 生成 metadata。

MAF 可以横向扩展，也可以借助 Durable Task Scheduler/backend 派发 work items；如果部署者按
Function App、worker app、task hub/backend、identity 和网络边界手动拆分，资源隔离和横向扩容能力会改善。
但当前 MAF graph surface 没有提供 Temporal Task Queue 那样的一等 per-executor/per-subgraph
resource-pool routing 面。反过来，Temporal 也不是自动 placement optimizer；task queue 命名、
worker 注册一致性、容量、依赖访问、autoscaling 和 versioning 仍需人工治理。

### 4. 副作用与 agent 执行边界

Temporal 的副作用边界是 commands。Workflow code 必须 deterministic；Activity、Timer、Child
Workflow、Signal External、Continue-As-New 等通过 command 进入服务端状态机。Activity 是明确的外部工作单元，
运行在 worker 侧，可配置 retry/timeout，并要求业务考虑幂等性。

MAF Durable Extension 也有清楚的 Durable Task-backed 执行边界：

| MAF graph executor 类型 | Durable path | 关键限制 |
| --- | --- | --- |
| ordinary executor | `CallActivityAsync` -> `DurableActivityExecutor.ExecuteAsync` | dispatcher 调用点未体现 per-executor retry/timeout/cancel policy；可靠性仍需外层配置或业务设计。 |
| AIAgent executor | `DurableAIAgent` -> Durable Entity `AgentEntity.Run` | cancellation 不支持；true streaming 不支持；graph executor path 默认创建新 session，不能直接等同于通用 durable agent session 复用能力。 |
| RequestPort | custom status + `WaitForExternalEvent` | 无内建 timeout；pending request status 不是完整事实源。 |
| subworkflow | `CallSubOrchestratorAsync` | 子 workflow 不共享父 workflow shared state。 |

MAF 的强项是把 agent、HITL、subworkflow 这些 MAF-native authoring objects 直接映射到 Durable
Task primitives。Temporal 的强项是副作用 taxonomy、commands 与 Event History/mutable state
的统一物化。

### 5. 外部交互语义

Temporal 的外部交互不是一个机制。Signal、Update、Query 和 Cancellation 的能力边界不同：

- Signal 写入 `WorkflowExecutionSignaled` event，通常创建 Workflow Task，让 worker 在 replay/handler
  中处理异步消息。
- Update 通过 update registry admit/attach，可创建 speculative Workflow Task，并能返回处理结果。
- Query 是只读交互，不应改变 workflow state；它可按一致性条件直接通过 matching dispatch 或 buffer
  到 Workflow Task response。Temporal 文档允许在 retention 内查询 completed、failed、timed out
  workflow；terminated workflow 不支持该 closed-workflow Query 语义。
- Cancellation 是协作式取消请求，不是立即终止。

MAF Durable Extension 的外部交互核心是 RequestPort。dispatcher 遇到 RequestPort executor 时，
把 pending request 写入 `DurableWorkflowLiveStatus.PendingEvents`，调用 `SetCustomStatus` 让外部客户端发现需要输入，
然后等待 `WaitForExternalEvent<string>(eventName)`；`DurableStreamingWorkflowRun` 轮询
`SerializedCustomStatus` 产出 waiting-for-input event，并通过 `RaiseEventAsync(runId,
requestPort.Id, response)` 恢复 orchestration。

不要把 MAF RequestPort/HITL 入口写成 Temporal Signal/Update/Query 的等价物：

- Pending status 是 discovery projection，不是“响应已被业务接受、处理完成或失败”的事实源。
- RequestPort wait 没有内建 timeout；限时审批要在 wrapper executor 中组合 timer 和 `Task.WhenAny`。
- 响应绑定键是 `runId + RequestPort.Id`，不是 per-request id；同一 RequestPort 在同一 run
  中重复出现时，审批任务 id、提交 id、actor、版本和幂等键必须进入 payload、外部任务表或业务状态。
- MAF respond 的 HTTP `Accepted` 只表示 external event 已提交给 Durable Task client，不等待 workflow
  对 response 的业务处理结果，因此不是 Temporal Update。

因此不能简单写成强弱关系：面向 MAF graph 的 HITL/审批/外部输入发现，RequestPort + status/respond
更贴近“workflow 主动向外部要输入”；面向通用 workflow API，Temporal 的 Signal/Update/Query/Cancellation
面更完整。

### 6. 长运行、历史治理与版本演进

Temporal 有围绕长运行 Workflow Execution 的显式治理面：

- Continue-As-New 把最新相关状态交给新的 run，保留同一 Workflow ID、生成新的 Run ID 和新的 Event
  History，用于避免过长历史或让长运行过程越过旧代码版本。
- Reset 基于 reset point 创建新的 Workflow Execution，复制历史前缀，不是原地改写已有 history。
- Workflow versioning / patching 通过显式 marker 和分支让新旧代码兼容已有 Event History。
- Worker Versioning 管理 Workflow Task 到 worker code version / Build ID / deployment 的路由。

MAF Durable Extension 借助 Durable Task backend 也能长运行、等待 external event、恢复
orchestration，并可调用 sub-orchestration。MAF durable agents 文档也说明 agent state 可跨
process restarts、failures 和 scale-out events 存活，HITL 可等待 days/weeks with zero compute。

但这支撑的是 Durable Task-backed long-running execution，不是 Temporal 等价的 history
governance/version evolution surface。在当前 MAF graph runner 源码里，能直接看到 `MaxSupersteps = 100`、
Durable Task orchestration replay、RequestPort、subworkflow、agent entity state 和 host/backend 配置；
没有看到 MAF graph-level Continue-As-New、graph reset、history-chain governance、workflow version marker
或 worker-code-version routing。超过 `MaxSupersteps` 的开放式 graph loop 不能被写成无限运行；需要业务层 handoff、
拆分 run 或等待未来 graph-level 机制。

### 7. 可观测性与审计边界

Temporal 的审计边界是 Event History；visibility/search attributes/query 是围绕 Workflow
Execution 的运行状态、检索和读取能力。Event History 作为 append-only log 用于 recovery 和 audit；
Task Queue、Worker、Build ID、Search Attributes 和 history APIs 共同支撑运维定位。

MAF Durable Extension 的可观测边界分三层：

1. MAF runner 把 workflow events 和 pending RequestPort 写入 `DurableWorkflowLiveStatus`，通过
   `SetCustomStatus` 暴露给 streaming/status 客户端。
2. `DurableStreamingWorkflowRun` 轮询 orchestration metadata 和 custom status，产出 events、
   waiting-for-input、completed/failed events。
3. Durable Task Scheduler dashboard 可观察 orchestration/entity instances、activities、
   sub-orchestrations 和 runtime status。

差异是：Temporal Event History 是 workflow execution 的事实日志；MAF custom status 更像 live
projection，完成后会被清理，最终 events 还需从 `DurableWorkflowResult` 输出中读取。Durable Task
dashboard 是 runtime-level observability，不等于 MAF 业务 graph 的完整审计日志。

### 8. Agent-first 抽象

这是 MAF 的差异化强项。Temporal 可以承载 agent workload：workflow 管控制流程，activities 调
LLM/tool/external services，signals/updates 传入外部消息，queries 读取状态，child workflows 拆分长任务。
但 Temporal runtime 本身不理解 AIAgent、conversation session、memory 或 agent response schema；这些需要业务层建模。

MAF Durable Extension 把 agent session 做成 Agent Framework 层的一等 durable surface：
`AIAgentBinding` 把 `AIAgent` 纳入 workflow executor binding；Durable Extension 注册阶段把
`AIAgentBinding` 从 ordinary activity 中排除；orchestration 内可通过 `context.GetAgent` 获取
`DurableAIAgent`，并用 deterministic-safe `NewAgentSessionId` 创建 session；`DurableAIAgent` 调
Durable Entity `AgentEntity.Run`；`AgentEntity` 用 `AgentSessionId` 作为 entity identity，保存
conversation history 和 TTL。

限制也同样重要：Durable Task/Azure Functions 底层并不原生理解 agent；MAF graph executor path
默认创建新 session，不能直接等同于所有 agent 调用自动复用同一 long-lived conversation；durable agent
cancellation 不支持；streaming 是把完整响应转成单次 update，不是 true streaming；conversation
history/TTL 也不是任意 tool side effects 的 exactly-once 边界。

## 总结矩阵

| 比较维度 | Temporal | MAF Durable Extension | 结论 |
| --- | --- | --- | --- |
| 控制表示/解释器 | Worker replay code 生成 commands，服务端校验并物化 history/state/tasks。 | Durable orchestration 内的 graph superstep runner 调用 Durable Task primitives。 | 不等价；MAF durable adapter 解释 graph 子集。 |
| 状态真源/恢复对象 | Event History + mutable state + worker replay。 | Durable Task orchestration state + `SuperstepState` + agent Durable Entity state。 | 都有 durable recovery，但状态边界不同。 |
| 调度/放置 | Task Queue、poller、sticky/versioning、worker fleet 是一等对象。 | Durable Task work items + Function App/worker host metadata/registry。 | MAF 可 scale，但 graph/executor resource pool 不如 Temporal Task Queue 一等。 |
| 副作用边界 | Activity/Timer/Child Workflow/Signal External/Continue-As-New 等 commands 进入 history/state。 | ordinary executor/activity、agent/entity、RequestPort/external event、subworkflow/sub-orchestration。 | MAF 映射清晰但部分策略需外层补足；Temporal taxonomy 更统一。 |
| 外部交互 | Signal/Update/Query/Cancellation 是不同 runtime contracts。 | RequestPort/status/respond 专注 HITL/external input。 | MAF 更贴近 graph HITL；不能等价为 Temporal 通用 message surface。 |
| 长运行/版本演进 | Continue-As-New、Reset、patching、Worker Versioning 是显式治理面。 | Durable Task-backed long run；graph runner 有 `MaxSupersteps=100`，未见 graph-level Continue-As-New。 | Temporal 的长历史和版本治理更一等。 |
| 可观测/审计 | Event History、visibility、search attributes、queries。 | custom status streaming、workflow result events、Durable Task runtime status/dashboard。 | Temporal 更接近事实日志；MAF live/status 更像投影。 |
| Agent-first | 通用 workflow 可承载 agent，但 agent session 业务自管。 | AIAgent + Durable Entity conversation history/TTL 是一等集成。 | MAF 在 agent-native ergonomics 上更强；Temporal 在通用 runtime 治理上更强。 |

## 判断规则

如果问题是“能否用 MAF Durable Extension 做可靠的 agent graph / HITL workflow”，答案是可以，
但需要接受 Durable Task backend、MAF graph durable runner 的语义保真边界，以及 Azure Functions/self-hosted
worker 的部署拓扑约束。

如果问题是“它是否等价于 Temporal 作为通用 durable workflow runtime”，答案是否定的。Temporal 把
Event History、mutable state、Task Queue、worker routing、Signal/Update/Query、Continue-As-New、
Reset 和 versioning 统一成 Workflow Execution runtime；MAF Durable Extension 当前更像把 MAF
graph/agent surface 投射到 Durable Task runtime 的 adapter。

如果问题是“哪个更强”，不能脱离目标：面向 agent session、AIAgent ergonomics、MAF graph HITL，
MAF Durable Extension 更贴近作者语义；面向长期业务过程审计、细粒度 worker/resource pool、历史治理、
版本演进和通用 workflow API，Temporal 的 runtime surface 更完整。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| user | 用户在 2026-06-16 要求基于完整源码对 Temporal 和 MAF Durable Extension enabled 做能力层比较，并要求多代理正反审查。 | 确定本页问题边界和方法要求。 |
| raw | `raw/git/github.com/temporalio/temporal/service/history/api/respondworkflowtaskcompleted/workflow_task_completed_handler.go:168-385, 463-568, 764-835, 1029-1245, 1536-1584` | Temporal Workflow Task completed 后的 command validation、command dispatch 和 history/mutable-state mutation。 |
| raw | `raw/git/github.com/temporalio/temporal/service/history/workflow/mutable_state_impl.go:127-245, 4200-4270, 5390-5445, 6128-6170` | Temporal mutable state 字段、Activity/Timer/Signal event application 与 pending state 更新。 |
| raw | `raw/git/github.com/temporalio/temporal/service/matching/matching_engine.go:580-856, 940-1096` | Temporal Workflow/Activity Task 入队、polling、sticky/build-id/versioning dispatch 和 obsolete task 处理。 |
| raw | `raw/git/github.com/temporalio/temporal/service/history/api/signalworkflow/api.go`、`updateworkflow/api.go`、`queryworkflow/api.go`、`requestcancelworkflow/api.go` | Temporal Signal、Update、Query 与 Cancellation 服务端路径。 |
| raw | `raw/git/github.com/temporalio/temporal/service/history/api/resetworkflow/api.go`、`command_attr_validator.go:386-450`、`common/worker_versioning/worker_versioning.go` | Temporal Reset、Continue-As-New validation 与 worker versioning 机制。 |
| raw | `raw/git/github.com/temporalio/documentation/docs/encyclopedia/workflow-message-passing/workflow-message-passing.mdx`、`docs/develop/go/workflows/message-passing.mdx`、`docs/encyclopedia/workers/task-queues.mdx`、`docs/production-deployment/worker-deployments/worker-versioning.mdx` | Temporal message passing、Task Queue 和 Worker Versioning 文档证据。 |
| raw | `raw/git/github.com/microsoft/agent-framework/dotnet/src/Microsoft.Agents.AI.DurableTask/Workflows/DurableWorkflowRunner.cs:72, 138-216, 254-323, 365-515` | MAF durable graph runner 的 deterministic orchestration、MaxSupersteps、superstep state、routing、status 和 final result。 |
| raw | `raw/git/github.com/microsoft/agent-framework/dotnet/src/Microsoft.Agents.AI.Workflows/WorkflowBuilder.cs:369-535`、`FanInEdgeData.cs`、`FanOutEdgeData.cs`、`Execution/FanInEdgeState.cs`、`Execution/FanOutEdgeRunner.cs` | MAF core graph authoring 与 in-process fan-in/fan-out 语义。 |
| raw | `raw/git/github.com/microsoft/agent-framework/dotnet/src/Microsoft.Agents.AI.DurableTask/Workflows/WorkflowAnalyzer.cs:50-168`、`EdgeRouters/DurableEdgeMap.cs:85-190`、`DurableWorkflowContext.cs:83-96`、`IWorkflowContext.cs:25-35` | MAF durable projection、edge routing 和 targeted message 语义保真限制。 |
| raw | `raw/git/github.com/microsoft/agent-framework/dotnet/src/Microsoft.Agents.AI.DurableTask/Workflows/DurableExecutorDispatcher.cs:41-216`、`DurableActivityExecutor.cs:28-72` | MAF ordinary executor、RequestPort、agent executor、subworkflow 到 Durable Task API 的 dispatch 映射。 |
| raw | `raw/git/github.com/microsoft/agent-framework/dotnet/src/Microsoft.Agents.AI.DurableTask/ServiceCollectionExtensions.cs:50-90, 125-147, 196-273, 275-340`、`Hosting.AzureFunctions/Workflows/DurableWorkflowsFunctionMetadataTransformer.cs:48-165` | MAF workflow/activity/entity registration 与 Azure Functions metadata generation。 |
| raw | `raw/git/github.com/microsoft/agent-framework/dotnet/src/Microsoft.Agents.AI.DurableTask/Workflows/DurableStreamingWorkflowRun.cs:63-247`、`BuiltInFunctions.cs:77-180`、`PendingRequestPortStatus.cs`、`DurableWorkflowLiveStatus.cs` | MAF status polling、waiting-for-input、respond endpoint、eventName 绑定和 custom status 限制。 |
| raw | `raw/git/github.com/microsoft/agent-framework/dotnet/src/Microsoft.Agents.AI.Workflows/AIAgentBinding.cs`、`ExecutorBindingExtensions.cs:416-432`、`DurableAIAgent.cs:12-40, 89-195`、`AgentEntity.cs:32-227`、`State/DurableAgentStateData.cs`、`TaskOrchestrationContextExtensions.cs:21-46` | MAF durable agent/session、conversation history、TTL、entity-backed execution 和 graph executor 限制。 |
| raw | `raw/git/github.com/microsoft/agent-framework/docs/features/durable-agents/README.md`、`durable-agents-ttl.md`、`raw/git/github.com/MicrosoftDocs/semantic-kernel-docs/agent-framework/workflows/checkpoints.md` | MAF durable agents、TTL、checkpoint/recovery 文档证据。 |
| wiki | [Temporal Task Queues 文档](../sources/temporal/task-queues-docs.md)、[Temporal Workers 文档](../sources/temporal/workers-docs.md)、[Temporal Message Passing 文档](../sources/temporal/message-passing-docs.md)、[Temporal Continue-As-New 文档](../sources/temporal/continue-as-new-docs.md)、[Temporal Reset 文档](../sources/temporal/reset-docs.md)、[Temporal Workflow Versioning 文档](../sources/temporal/workflow-versioning-docs.md)、[Temporal Worker Versioning 文档](../sources/temporal/worker-versioning-docs.md) | 既有 Temporal source projections。 |
| wiki | [Microsoft Agent Framework Durable Extension 文档](../sources/microsoft-agent-framework/durable-extension-docs.md)、[Durable Workflow Registration 源码](../sources/microsoft-agent-framework/durable-workflow-registration-source.md)、[Durable Executor Dispatcher 源码](../sources/microsoft-agent-framework/durable-executor-dispatcher-source.md)、[Azure Functions Durable Workflow Metadata Transformer 源码](../sources/microsoft-agent-framework/azure-functions-durable-workflows-metadata-transformer-source.md)、[Durable Task Scheduler 文档](../sources/microsoft-durable-task/scheduler-docs.md)、[Durable Task SDKs Overview 文档](../sources/microsoft-durable-task/sdk-overview-docs.md) | 既有 MAF/Durable Task source projections。 |
| session | 维度讨论、逐维 Temporal/MAF 正反代理，以及技术、公平性、provenance 审查代理输出。 | 用于维度收敛和反方检查；事实主证据仍回 raw/wiki。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| Temporal 与 MAF Durable Extension 都能承载 durable、可恢复、可外部交互的 workflow，但 runtime 能力边界不等价。 | Temporal command/mutable state/matching raw evidence；MAF runner/dispatcher/registration raw evidence；Durable Extension 与 Durable Task source pages。 | 不比较未启用 Durable Extension 的 MAF core workflow；不做性能或成本 benchmark。 |
| Temporal 的核心运行模型是 worker replay code 生成 commands，服务端校验并物化为 Event History、mutable state 和 tasks。 | `workflow_task_completed_handler.go`；`mutable_state_impl.go`；Temporal deterministic constraints source page。 | SDK 细节按语言不同；本文只抽象服务端/worker 协议边界。 |
| MAF Durable Extension 的核心运行模型是 MAF graph runner 在 Durable Task orchestration 内执行 superstep，并把 executor 映射到 activity/entity/sub-orchestration/external event。 | `DurableWorkflowRunner.cs`；`DurableExecutorDispatcher.cs`；`ServiceCollectionExtensions.cs`。 | 这是 .NET graph workflow durable path；functional workflow surface 和未来实现需另行取证。 |
| MAF Durable Extension 当前没有完整保真所有 MAF graph edge/message 语义，特别是 fan-in barrier、fan-out target selector 与 per-message target routing。 | `WorkflowBuilder.cs`；`FanInEdgeData.cs`；`FanOutEdgeData.cs`；`WorkflowAnalyzer.cs`；`DurableEdgeMap.cs`；`DurableWorkflowRunner.cs`；`DurableWorkflowContext.cs`。 | 源码可能在未来版本修复；本结论只针对当前导入快照。 |
| Temporal 的调度/放置边界比 MAF Durable Extension 的 graph surface 更一等、更细，因为 Task Queue/Worker Process/Build ID routing 是 runtime surface。 | `matching_engine.go`；Temporal Task Queues/Workers/Worker Versioning source pages。 | Temporal 也需要人工设计 task queue、worker 注册、capacity、versioning 和幂等策略；MAF/Durable Task/Azure Functions 也可横向扩容。 |
| MAF RequestPort/HITL 外部入口适合 durable HITL 发现和 response，但不能等价为 Temporal Update/Signal/Query/Cancellation 通用 message surface。 | `DurableExecutorDispatcher.cs`；`BuiltInFunctions.cs`；`PendingRequestPortStatus.cs`；`DurableWorkflowLiveStatus.cs`；`DurableStreamingWorkflowRun.cs`；Temporal message passing raw/wiki evidence。 | 主张限于 durable graph HTTP/status/respond/streaming RequestPort path；不否定 Durable Task 底层 timer/history 能力。 |
| MAF Durable Extension 的长运行执行证据很强，但长历史治理和版本演进主要依赖 Durable Task/host/业务层；Temporal 把这些治理面做成 Workflow Execution runtime 的一等机制。 | MAF durable agents docs；`DurableWorkflowRunner.cs`；Temporal Continue-As-New/Reset/Versioning raw/wiki evidence。 | Durable Task SDK 底层也支持 continue-as-new；本页只说当前 MAF graph runner 未见同等 graph-level surface。 |
| MAF 在 agent-first abstraction 上更强，因为 AIAgent session 与 conversation history 是 Agent Framework 层的一等 durable integration。 | `AIAgentBinding.cs`；`DurableAIAgent.cs`；`AgentEntity.cs`；`DurableAgentStateData.cs`；durable agents docs。 | 底层 Durable Task 不原生理解 agent；graph executor 默认 session 复用、cancellation 和 streaming 有限制。 |
| 可观测性上，Temporal Event History 更接近 workflow execution 事实日志；MAF custom status 更像 live projection，Durable Task dashboard 是 runtime-level 观测。 | Temporal Event History/Reset evidence；`DurableWorkflowLiveStatus.cs`；`DurableStreamingWorkflowRun.cs`；Durable Task Scheduler source page。 | Temporal visibility/search/query 也需要业务设计；Query 本身不是审计日志。 |
