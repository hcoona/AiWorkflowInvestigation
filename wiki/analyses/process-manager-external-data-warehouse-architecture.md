---
schema_version: 2
page_type: analysis
title: "Process Manager 架构：Workflow Event History 与外部事实仓库"
status: active
created: 2026-06-17
updated: 2026-06-17
summary: "分析外部数据仓库作为资源主事实线时，Temporal 与 MAF Durable Extension 的建模边界。"
maintenance:
  edit_policy: update
validation:
  body_contract: analysis-answer-memo
tags:
  - architecture
  - process-manager
  - temporal
  - microsoft-agent-framework
  - durable-extension
  - data-warehouse
---

## 问题

本页回答：当业务已经假定“资源事实状态在外部数据仓库”时，Temporal
和 Microsoft Agent Framework Durable Extension（下称 MAF Durable Extension）应如何建模？
该假设是否改变裸金属 buildout process manager 选型页中对 MAF 的定位？

这里的“外部数据仓库”按用户语境理解为可被 workflow/activities 读写的外部资源事实层，
包括资源当前状态、状态历史、审计记录、幂等键、事件 inbox/outbox、锁或租约。
如果它只是离线分析型 data warehouse，不能直接承担操作控制面的事实源。

## 答案

**架构 B 会缩小 MAF 与 Temporal 在“资源状态由谁持有”上的差异，
但不会消除两者在 process manager runtime 语义上的差异。**

在架构 B 下，workflow 不需要把 node/rack/fabric 的完整资源状态写成 workflow
内部变量或 graph checkpoint 的主事实。
它仍必须持有或主责 **过程控制事实线**：
当前协调位置、等待哪个事件、哪些副作用已经发出、下一步如何读外部事实并决策、
局部失败如何追平、补偿由谁决定、协调过程如何被审计。

因此，MAF 的定位应 **条件性上调**：
它不再需要“亲自持有资源事实状态”才能进入候选；
但只有当 Durable Extension-backed graph/hybrid 稳定引用外部资源身份，
并亲自承担过程控制路径、事件解释、局部追平、补偿决策和副作用边界时，
才是 process manager 候选。
如果这些职责由另一个 domain process service 承担，
MAF 仍只是 agent/HITL/durable workflow adapter。

**明确判断**：架构 B 让 MAF 从“除非亲自持有资源事实线，否则默认 adapter”
上调为“可进入 Temporal 相邻的 coordinator POC”；
但不默认升级为与 Temporal 同强的主 baseline。
Temporal 在 activity 级 Task Queue 路由、Signal/Update/Query、Child Workflow 身份、
Continue-As-New/Reset/Worker Versioning 和 Event History 可审计性上仍更一等。
MAF 的优势仍主要是 Agent Framework graph、AIAgent 和 HITL authoring/runtime integration。

## 两条事实线

架构 A 与架构 B 的核心区别不是“有没有外部系统”，
而是资源事实线与协调事实线是否重合。

| 事实线 | 架构 A：Workflow Event History 为主 | 架构 B：外部事实仓库为主 |
| --- | --- | --- |
| 资源当前状态 | Workflow 变量经 replay 重建；外部系统是 projection/query view。 | 外部事实仓库保存；workflow 只读取快照并做下一步决策。 |
| 资源状态历史与业务审计 | Event History 或由它投影出的审计线。 | 外部事实仓库/审计表保存；workflow history 是协调执行审计。 |
| 协调状态 | Workflow history/checkpoint 持有。 | Workflow history/checkpoint 仍持有。 |
| 副作用边界 | Activity/command 执行外部 I/O，结果进入 history。 | Activity/executor 读写外部事实仓库和设备；结果也进入协调 history。 |
| 恢复策略 | replay history 重建资源过程变量并继续。 | replay/checkpoint 恢复协调器；在显式决策点重新查询外部事实并继续。 |

架构 B 不等于“不需要 process manager”。
如果外部事实仓库只是被动事实层，workflow 仍是 long-running coordinator / process manager。
如果外部事实仓库背后还有一个 domain service 负责解释事件、决定下一步、追平失败、补偿和审计，
那套 domain service 才是主 process manager；Temporal 或 MAF 只是它调用的 durable execution layer。

## Temporal 在架构 B 下的建模

### Workflow 变量

Temporal Workflow 变量在架构 B 下是 **可 replay 的协调状态和过期风险可控的快照**，
不是资源状态的主事实。

- 变量可保存 `nodeId`、`operationId`、`currentGate`、`lastReadVersion`、
  `pendingApprovalId`、`childWorkflowIds` 等协调字段。
- 变量也可短暂保存某次 `readNodeState` Activity 的结果，
  但该结果只表示“决策时读到的外部事实版本”。
- Workflow 代码必须 deterministic；直接读数据库、文件、网络或真实设备应放在 Activity。
- replay 会用 Event History 中已完成 Activity 的结果重建变量，
  不会自动绕过 history 去读外部事实仓库。

所以架构 B 需要显式的 **reconcile / decision fence**：
在危险副作用前、长等待后、人工修复后、retry/Reset/Continue-As-New 后，
由 Workflow 安排新的 Activity 读取外部事实仓库和必要的真实设备状态，
再决定是否继续、跳过、补偿或等待。

### Event History

Temporal Event History 在架构 B 下仍是 Workflow Execution 的恢复与协调审计日志，
但不是资源事实仓库。
它记录的是：Workflow Task、Activity schedule/start/complete/fail/timeout、Timer、Signal、Update、
Child Workflow、Continue-As-New、Reset 相关事件等 runtime facts。
这些事件能证明“协调器曾调度什么、收到什么、Activity 返回过什么”，
不能单独证明“外部资源此刻处于什么状态”。

因此，架构 B 下 Event History 的语义是：

1. 恢复 workflow code 的 deterministic control state。
2. 审计协调器对外部世界发出过哪些命令和收到过哪些响应。
3. 给 projection / dashboard 提供 runtime 观察资料。
4. 与外部事实仓库中的资源状态版本、operation ledger 和审计记录相互关联。

### Activity 职责

Activity 是架构 B 的外部事实和真实副作用边界。
常见拆分是：

- `ReadNodeState(nodeId, expectedVersion?)`：读外部事实仓库。
- `ReserveOperation(nodeId, operationId, precondition)`：写幂等操作记录或锁。
- `PowerOn/FlashFirmware/InstallOS/ValidateFabric`：调用 BMC、provisioning、网络或验证系统。
- `PersistObservedState(operationId, observedState, evidence)`：把结果、设备读回、错误和审计写回外部事实仓库。
- `ReleaseOrCompensate(operationId, reason)`：释放锁、标记补偿或等待人工。

Activity retry 不等于 exactly-once。
架构 B 必须让外部事实仓库支持幂等键、条件写、状态版本、operation ledger、读后校验和补偿记录。

### 恢复行为

Temporal worker 崩溃后，服务端仍保存 Workflow Execution、pending activities/timers/children/signals 等 mutable state；
worker 恢复时 replay Event History，SDK workflow code 重建本地变量并继续生成 commands。

关键限制是：**已完成的外部读取 Activity 在 replay 中返回历史里的旧结果，不会自动重新查询。**
若要使用最新外部状态，Workflow 必须在 replay 到达可执行边界后安排新的读取 Activity，
或通过 Signal/Update/Timer 唤醒后进入新的 reconcile 步骤。

因此架构 B 的恢复路径应写成：

```text
replay Event History
→ 恢复协调状态、未决 timer/activity/child/message
→ 到达下一个决策 fence
→ Activity 读取外部事实仓库和必要设备状态
→ 按当前事实决定继续、等待、补偿或跳过
```

### Child Workflow 与资源身份

架构 B 下，Child Workflow 不需要持有资源事实本身，
但仍是长期、可寻址、可局部追平的过程分区。
常见映射是：

```text
Cluster Workflow ID       = buildout/{clusterId}
Rack Child Workflow ID    = buildout/{clusterId}/rack/{rackId}
Node Child Workflow ID    = buildout/{clusterId}/node/{nodeId}/gen/{resourceGeneration}
External warehouse row    = nodeId + resourceGeneration + workflowId + runId + currentFactVersion
```

`Workflow ID` 是稳定业务过程身份；`Run ID` 是 Temporal run 身份，
会随 Continue-As-New 或 Reset 改变。
外部事实仓库应保存 workflow ID / run ID / operation ID 的关联，
并在硬件替换、节点重用或资源 generation 变化时避免把旧过程误映射到新机器。

## MAF Durable Extension 在架构 B 下的建模

### Graph workflow state

MAF Durable Extension 的 graph workflow state 在架构 B 下应是 **协调状态和 graph 消息状态**，
不是资源事实主存储。
当前 .NET durable runner 的 `SuperstepState` 保存 edge map、executor bindings、message queues、last results、
shared state、accumulated events 和 live status。
这些适合保存：

- resource ID / operation ID / external fact version；
- 当前 graph/superstep 到达哪个协调点；
- 待发送给后继 executor 的消息；
- pending HITL request 的关联信息；
- 为恢复 graph execution 所需的轻量 shared state。

不宜把完整 node/rack/fabric 事实状态长期塞进 graph shared state 当主事实。
如果 shared state 保存外部事实快照，应标注版本和过期边界，
并在副作用前重新读外部事实仓库。

### Executor context

普通 MAF executor 运行时拿到的是 `IWorkflowContext` / `DurableWorkflowContext`，
不是完整 `TaskOrchestrationContext`。
`IWorkflowContext` 暴露的是 graph 层能力：发消息、输出事件、读取/排队更新 workflow state、请求 halt 等。
Durable dispatcher 在 executor 外层把普通 executor 调成 Durable Task `CallActivityAsync`；
RequestPort 调成 `SetCustomStatus` + `WaitForExternalEvent`；
subworkflow 调成 `CallSubOrchestratorAsync`；agent executor 调成 Durable Entity 路径。

这对架构 B 的含义是：

- 一个普通 executor 本身就是 Durable Task activity 边界，
  可以在 executor/activity 代码中调用外部事实仓库和设备系统。
- 不应把普通 executor 中的 `IWorkflowContext` 写成可任意调用底层 Durable primitives 的 orchestration context。
- 如果需要显式 timer、sub-orchestration、direct Durable client、custom retry policy 或复杂 fan-out，
  需要通过 MAF 已映射的 graph/subworkflow/RequestPort/agent surface、
  `DurableAgentContext`、服务层 `DurableTaskClient`、自写 Durable orchestrator，或 hybrid composition 接入。

### Custom status projection

MAF `SetCustomStatus` / `DurableWorkflowLiveStatus` 在架构 B 下是 live coordination projection：
用于 streaming events、pending RequestPort discovery 和运行中状态观察。
源码注释明确 completed orchestration 的 `SerializedCustomStatus` 会被 Durable Task framework 清理，
runner 因此把 accumulated events 放入最终 `DurableWorkflowResult`。

所以业务 dashboard 的主状态不应来自 custom status。
正确分层是：

```text
外部事实仓库：资源状态、操作账本、业务审计、验收结果
MAF custom status：当前 graph run 的 pending input / live stream / runtime hint
Durable Task dashboard：orchestration/activity/entity runtime 观察面
```

### 恢复行为

MAF Durable Extension 的恢复首先恢复 Durable Task orchestration，
再恢复 MAF graph runner 的 superstep/message/shared-state 进度。
跨 stateless workers 的 checkpoint/recover 能恢复“graph workflow 执行到哪里”，
但不自动证明外部资源当前状态。

与 Temporal 类似，已完成 executor/activity 的输出会作为 durable history 的一部分参与 replay；
它不是自动重新读外部事实仓库。
需要最新资源事实时，graph 必须显式进入新的 read/reconcile executor，
或由外部事件/RequestPort/agent/tool path 触发后再读外部事实。

### Subworkflow 与资源身份

MAF subworkflow 映射为 Durable Task sub-orchestration。
架构 B 下可以把 graph workflow instance / durable orchestration instance 与外部资源 ID 关联：

```text
Durable graph workflow instance = buildout/{clusterId}
Subworkflow orchestration       = buildout/{clusterId}/node/{nodeId}/gen/{resourceGeneration}
External fact row               = nodeId + resourceGeneration + orchestrationInstanceId + operationId
```

但这需要应用显式约定。
MAF graph node / executor id 不天然等于裸金属 node id；
RequestPort 的 event name 主要来自 `RequestPort.Id`，
同一 request port 在同一 run 多次出现时，审批任务 ID、actor、版本、幂等键和 resource ID
必须进入 payload、外部事实仓库或专门任务表，不能只依赖 request port id。

### “多层映射”是否仍成立

仍成立，但范围变窄。

- 对 **资源事实状态**：多层映射压力明显下降，因为主事实不在 graph checkpoint 中。
- 对 **过程控制路径**：多层映射仍存在。事件要从外部事实仓库或 UI 路由到 Durable Task instance、
  RequestPort/subworkflow/agent/entity，再回到 graph executor 和外部事实仓库；
  诊断也要跨 Agent Framework graph、Durable Task orchestration/activity/entity、host/backend 和业务事实层。

因此不能再说“MAF 必须亲自持有资源事实线”；
但仍可以说“MAF 作为 process manager 必须证明 graph/executor/Durable Task/外部事实仓库的映射不会破坏资源身份、事件路由、局部追平和审计”。

## 架构 B 下的差异对比

| 维度 | Temporal | MAF Durable Extension | 判断 |
| --- | --- | --- | --- |
| 资源事实状态 | 由 Activity 读写外部事实仓库；Workflow 变量是 replayable 协调状态和快照。 | 由 executor/activity 读写外部事实仓库；shared state 是 graph 协调状态和快照。 | 差异缩小。 |
| 恢复 | replay Event History；已完成 Activity 结果来自 history；最新事实需新 Activity 查询。 | Durable Task replay + graph superstep state；已完成 executor 输出来自 history；最新事实需新 executor/activity 查询。 | 同属“恢复协调器，再显式 reconcile 外部事实”。 |
| 资源身份 | Workflow ID / Child Workflow ID 可直接按 cluster/node/rack 映射。 | Graph workflow instance / subworkflow orchestration 可映射，但要穿过 graph/executor/Durable Task 命名。 | Temporal 更直接；MAF 可行但需约定。 |
| 外部事件入口 | Signal 异步；Update 可验证、可追踪并返回结果；Query 只读。 | RequestPort/status/respond 适合 HITL input discovery；底层 Durable external event 是单向异步。 | 通用 command surface Temporal 更完整；HITL authoring MAF 更自然。 |
| Activity/worker 路由 | Activity/Child 可设置或继承 Task Queue。 | Ordinary executor 注册为 activity；资源池主要依赖 Durable Task/host/function app/worker 拓扑。 | 动态资源池路由 Temporal 更强。 |
| 长历史治理 | Continue-As-New、Reset、Workflow/Worker Versioning 是一等讨论面。 | 继承 Durable Task 长运行；当前 graph runner 可见 `MaxSupersteps=100`，未见等价 graph-level history governance surface。 | Temporal 更一等。 |
| 可观测/审计 | Event History 是协调事实日志；业务事实仍在外部仓库。 | custom status 是 live projection，最终 events 在 output；Durable dashboard 是 runtime 观察面。 | 架构 B 下两者都需外部业务审计；Temporal runtime audit 更直接。 |
| Agent/HITL | 通过 Activity、Signal/Update 和外部 agent platform 集成。 | AIAgent、Durable Entity-backed agent state、RequestPort 和 graph workflow 是一等 surface。 | MAF 在 agent/HITL ergonomics 上更强。 |

## 对现有文档的修改建议

现有表述：

> 只有当 graph/hybrid 亲自持有资源过程身份、事件解释、局部追平、补偿决策、副作用边界和审计事实线时，才进入主 process manager baseline。

建议改为：

> 如果目标架构把 workflow Event History 作为资源事实主线，
> graph/hybrid 只有在亲自持有资源过程身份、事件解释、局部追平、补偿决策、副作用边界和审计事实线时，
> 才能进入主 process manager baseline。
> 如果业务已假定外部事实仓库是资源状态、资源历史和业务审计的主事实线，
> graph/hybrid 不需要亲自保存完整资源事实；
> 但它仍必须稳定引用外部资源身份，
> 并亲自承担过程控制路径：事件解释与路由、等待与恢复、局部追平、补偿决策、副作用边界、
> 协调状态和协调审计，并把结果写回外部事实仓库。
> 若这些过程控制职责由另一个 domain process service 承担，
> 那个 service 才是主 process manager，MAF 只是 agent/HITL/durable workflow adapter。

对应 POC gate 也应增加架构 B 专项：

1. 外部事实仓库必须是操作型事实层，而非只读分析仓库。
2. 每个 resource/process/subprocess 必须有稳定 ID、generation 和 workflow/orchestration instance 映射。
3. 所有外部事件必须有 inbox/outbox、幂等键、资源版本、actor、审计和 ordering/concurrency 策略。
4. 每个危险副作用前后必须有 explicit read/reconcile fence。
5. recovery、retry、Reset、Continue-As-New、checkpoint/recover 后不能无条件重放危险副作用。
6. dashboard 应以外部事实仓库为业务真源，并用 Temporal/MAF runtime status 做补充观察。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| user | 用户在 2026-06-17 明确：“我们业务上已经假定了事实状态是外部数据仓库”。 | 确立架构 B 的业务前提。 |
| wiki | [裸金属 Cluster Buildout 的 Process Manager 平台选型](bare-metal-cluster-buildout-process-manager-selection.md) | 提供被修正的 MAF baseline 表述和裸金属 buildout scope。 |
| wiki | [Temporal 与 MAF Durable Extension 的能力边界](temporal-vs-maf-durable-extension.md) | 提供两者在 Event History、Task Queue、Signal/Update/Query、RequestPort、custom status、graph runner 和 agent surface 上的机制比较。 |
| wiki | [Temporal Workflows 文档](../sources/temporal/workflows-docs.md)、[Temporal Workflow 确定性约束文档](../sources/temporal/workflow-deterministic-constraints-docs.md)、[Temporal Activities 文档](../sources/temporal/activities-docs.md) | 支撑 Temporal workflow replay、deterministic workflow code 与 Activity 外部 I/O 边界。 |
| wiki | [Temporal Message Passing 文档](../sources/temporal/message-passing-docs.md)、[Temporal Child Workflows 文档](../sources/temporal/child-workflows-docs.md)、[Temporal Task Queues 文档](../sources/temporal/task-queues-docs.md)、[Temporal Continue-As-New 文档](../sources/temporal/continue-as-new-docs.md)、[Temporal Reset 文档](../sources/temporal/reset-docs.md) | 支撑 Temporal 运行中交互、资源分区、worker routing 和历史治理语义。 |
| wiki | [Durable Task Orchestrations 文档](../sources/azure-durable-functions/orchestrations-docs.md)、[Durable Task Code Constraints 文档](../sources/azure-durable-functions/code-constraints-docs.md)、[Durable Task External Events 文档](../sources/azure-durable-functions/external-events-docs.md)、[Durable Task Instance Management 文档](../sources/azure-durable-functions/instance-management-docs.md) | 支撑 Durable Task event sourcing/replay、determinism、external events 和 instance ID 边界。 |
| wiki | [Microsoft Agent Framework Durable Extension 文档](../sources/microsoft-agent-framework/durable-extension-docs.md)、[Durable Workflow Registration 源码](../sources/microsoft-agent-framework/durable-workflow-registration-source.md)、[Durable Executor Dispatcher 源码](../sources/microsoft-agent-framework/durable-executor-dispatcher-source.md)、[Workflow Checkpoints 文档](../sources/microsoft-agent-framework/checkpoints-docs.md)、[Workflow State 文档](../sources/microsoft-agent-framework/state-docs.md) | 支撑 MAF Durable Extension 的 graph workflow、executor dispatch、checkpoint/state 和 Durable Task-backed 恢复边界。 |
| raw | `raw/git/github.com/temporalio/temporal/service/history/workflow/mutable_state_impl.go:127-162,4200-4265,5390-5443`、`raw/git/github.com/temporalio/temporal/service/history/api/respondworkflowtaskcompleted/workflow_task_completed_handler.go:168-223,1029-1088`、`raw/git/github.com/temporalio/temporal/service/matching/matching_engine.go:580-660` | Temporal mutable state、Activity/Timer event application、command handling、Continue-As-New validation 和 Task Queue task dispatch 的源码证据。 |
| raw | `raw/git/github.com/microsoft/agent-framework/dotnet/src/Microsoft.Agents.AI.Workflows/IWorkflowContext.cs:13-197`、`raw/git/github.com/microsoft/agent-framework/dotnet/src/Microsoft.Agents.AI.DurableTask/Workflows/DurableWorkflowContext.cs:10-120`、`raw/git/github.com/microsoft/agent-framework/dotnet/src/Microsoft.Agents.AI.DurableTask/Workflows/DurableExecutorDispatcher.cs:41-129,172-186`、`raw/git/github.com/microsoft/agent-framework/dotnet/src/Microsoft.Agents.AI.DurableTask/Workflows/DurableWorkflowRunner.cs:67-210,254-284`、`raw/git/github.com/microsoft/agent-framework/dotnet/src/Microsoft.Agents.AI.DurableTask/Workflows/DurableWorkflowResult.cs:5-23`、`raw/git/github.com/microsoft/agent-framework/dotnet/src/Microsoft.Agents.AI.DurableTask/Workflows/DurableStreamingWorkflowRun.cs:100-150`、`raw/git/github.com/microsoft/agent-framework/dotnet/src/Microsoft.Agents.AI.DurableTask/DurableAgentContext.cs:80-122` | MAF ordinary executor context、graph state、executor-to-Durable Task dispatch、RequestPort external event、subworkflow orchestration、custom status/result、streaming status 读取和 durable agent context 的源码证据。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| 架构 B 将资源事实线外移，workflow 仍可能持有过程控制事实线。 | 用户输入；裸金属选型页；Temporal/Durable Task/MAF source pages。 | “外部数据仓库”必须具备操作型事实层能力；若只是分析仓库，需另建 operational store。 |
| Temporal 在架构 B 下的 Workflow 变量是 replayable 协调状态和快照；最新资源事实必须通过 Activity 显式读取。 | Temporal Workflows、determinism、Activities source pages；Temporal mutable state 与 command handling raw evidence。 | SDK 细节按语言不同；本文不设计具体 schema。 |
| Temporal Event History 在架构 B 下是协调恢复和 runtime 审计日志，不是资源事实仓库。 | Temporal Workflows、Reset、Continue-As-New source pages；mutable state raw evidence。 | Event History 可与外部审计关联；它仍不是业务 dashboard 的完整替代。 |
| MAF Durable Extension 在架构 B 下可把 graph/shared state 收缩为协调状态，不必保存完整资源事实，因此建模扭曲缩小。 | MAF Durable Extension、checkpoint/state、dispatcher source pages；`DurableWorkflowRunner.SuperstepState` raw evidence。 | 缩小不等于消失；graph/executor/Durable Task/外部事实层映射仍需 POC。 |
| 普通 MAF executor 的 `IWorkflowContext` 不是完整 `TaskOrchestrationContext`；外部 DB/设备 I/O 应在 executor/activity 或 hybrid 边界中实现。 | `IWorkflowContext.cs`、`DurableWorkflowContext.cs`、`DurableExecutorDispatcher.cs` raw evidence。 | Agent/tool context 和服务层可暴露额外能力；本文只描述普通 executor path。 |
| MAF custom status 是 live projection，不应作为业务审计主事实。 | `DurableWorkflowRunner.cs`、`DurableWorkflowResult.cs`、`DurableStreamingWorkflowRun.cs` raw evidence；MAF 能力边界页。 | 业务仍可把 custom status 作为 dashboard 辅助信号。 |
| 架构 B 条件性上调 MAF：可进入 coordinator POC，但不默认与 Temporal 同强。 | 本页机制对比；Temporal-vs-MAF 能力边界；Temporal Task Queues、Message Passing、Continue-As-New/Reset source pages；MAF Durable Extension source pages。 | 最终排序仍依赖目标资源池路由、HITL/agent 比重、Durable Task hosting/backend 和 PoC 结果。 |
| 文档应把“亲自持有资源事实线”改为“稳定引用外部事实线并亲自持有过程控制路径”。 | 用户架构假设；本页两条事实线分析；裸金属选型页。 | 只适用于架构 B；架构 A 仍需要 workflow/history 自己承载资源事实线。 |
