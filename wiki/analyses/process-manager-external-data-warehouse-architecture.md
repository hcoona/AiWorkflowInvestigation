---
schema_version: 2
page_type: analysis
title: "Process Manager 架构：协调事实线与观察事实线"
status: active
created: 2026-06-17
updated: 2026-06-17
summary: "分析 Event History 作为协调命令事实线、外部运维数仓作为观察状态基准时，Temporal 与 MAF Durable Extension 的 reconcile 建模边界。"
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
  - reconciliation
  - data-warehouse
---

## 问题

本页回答：在裸金属 cluster buildout 中，如果 **Temporal Event History / Durable Task history
是协调命令事实线**，而 **外部运维数据仓库是物理状态的观察基准**，Temporal
和 Microsoft Agent Framework Durable Extension（下称 MAF Durable Extension）应如何建模？
这是否需要修正先前把“外部数据仓库是唯一主事实线”的表述？

这里的外部运维数据仓库按用户澄清理解：它汇集监控、探测、日志和运维系统结果，
用于判断机器、节点、网络或验收项实际被观察到的状态。它不自动等于 command ledger、
锁服务或可写操作型资源库；如果需要 operation ledger、idempotency key、租约、inbox/outbox
或命令审计，应作为相邻操作控制面显式设计，不能把这些职责含混地放进“数仓”一词。

## 答案

**需要修正先前分析。准确模型不是“Event History vs 外部数据仓库二选一”，
而是观察驱动的双事实线：Event History 是协调器命令与返回的 source of truth；
外部运维数据仓库是物理世界观察状态的 source of truth。**

在这个架构中，Workflow 发出 `PowerOn(node-001)` 并收到 Activity
`{ success: true }`，只能证明协调器调度过该命令、Activity 曾返回成功，不能证明
`node-001` 已经通电、完成自检、加入网络或达到验收状态。下一步决策必须经过显式观察：
Workflow/graph 安排观察 Activity/executor 查询外部运维数仓，读取带时间、来源、版本和置信边界的
observed state，再比较 desired state 与 observed state，决定继续等待、重试、补偿、跳过或人工介入。

这更接近 Kubernetes controller pattern：

```text
Desired state / spec：workflow 过程目标、命令意图、阶段门禁、幂等操作计划
Observed state / status：外部运维数仓中的监控、探测、日志聚合和验收观察
Controller loop：workflow 或 graph 显式 observe → compare → command → wait/trigger → observe
```

**MAF 的定位不需要再被大幅上调。** 观察驱动架构会缩小“谁保存完整资源状态”的差异，
因为 Temporal Workflow 变量和 MAF graph shared state 都不应成为物理状态主存储。
但两者都必须显式建模 reconcile loop；MAF 不因为外部数仓存在而天然获得本质优势。
Temporal 仍在 Workflow/Child Workflow 身份、Signal/Update/Query、activity Task Queue
路由、Event History 可审计性、Continue-As-New/Reset/Worker Versioning 等过程管理面更直接。
MAF 的优势仍主要在 Agent Framework graph、AIAgent、RequestPort 和 HITL authoring/runtime
集成；只有 graph/hybrid 亲自承担 reconcile loop、资源身份映射、事件解释、补偿和协调审计时，
才是主 process manager 候选。

## 双事实线的语义边界

| 事实线 | 主体 | 记录什么 | 不能证明什么 | 设计后果 |
| --- | --- | --- | --- | --- |
| 协调事实线 | Temporal Event History / Durable Task history / MAF durable graph checkpoint | Workflow/orchestrator 决定了什么、调度了什么 Activity/executor、收到什么返回、等待了什么 timer/event、进入哪个协调阶段。 | 不能单独证明机器此刻真实处于目标状态。 | 作为过程恢复、命令审计、幂等操作关联和 controller loop 的 desired/command 侧依据。 |
| 观察事实线 | 外部运维数据仓库 | 监控、探测、日志聚合、验收任务和运维系统观察到的机器状态、时间、来源、版本、置信度和滞后边界。 | 不能单独说明 workflow 是否已经发过某命令、某 Activity 是否完成、某补偿是否已被协调器接受。 | 作为物理世界 observed state 基准；所有危险决策前后需要重新观察。 |
| 命令返回线 | Activity/executor return value | 命令提交、API 调用、脚本执行或工具调用的本次结果、receipt、operation ID、错误类型。 | `success` 不等于最终状态到达；`failure` 也不一定等于物理状态未变化。 | 命令 Activity 应返回收据和可关联证据，而不是把目标状态当成事实写死。 |
| 对齐线 | Reconcile loop | desired 与 observed 的差异、下一步 delta、等待条件、补偿和人工介入。 | 不能靠单次读取消除监控滞后、外部干预或硬件不确定性。 | 需要 poll、event-triggered wakeup、staleness guard、幂等键和版本化决策。 |

这与传统 saga/orchestration 的关键差别在于：传统 saga 往往把每个步骤的成功/失败返回作为推进或补偿的主要信号；
观察驱动 buildout 把命令返回当成 **命令执行证据**，把外部观察当成 **状态推进证据**。
Activity 成功只让 controller 进入下一轮观察，不直接让状态机无条件前进。

Activity 返回值不能作为状态决策依据，原因包括：

- 裸金属操作常是异步的。BMC 或 provisioning API 接受命令后，硬件可能还在启动、自检或重装。
- 物理状态只能通过监控、探测、日志或运维系统间接观察，存在采样延迟、聚合延迟和缺失。
- 外部干预可能在 Activity 返回后发生，例如现场换线、人工重启、供应商维修或另一个系统修改配置。
- 部分失败很常见：命令成功提交，但 PXE、RAID、NIC、firmware、交换机或电源状态只完成了一部分。
- retry 与 timeout 不能直接映射到物理状态；Activity 超时后设备可能已执行成功，Activity 成功后设备也可能随后失败。

## Temporal 在观察驱动架构下的建模

### Workflow 变量

Temporal Workflow 变量应保存 **replayable coordination state**，并可缓存带版本的观察快照，
但不能把缓存快照当成当前物理状态真源。

适合保存：

- desired state：目标阶段、目标节点状态、计划版本、门禁、验收策略、补偿策略。
- coordination state：`clusterId`、`nodeId`、`operationId`、`idempotencyKey`、`currentGate`、
  `pendingCommand`、`lastCommandReceipt`、`childWorkflowIds`、`processedSignalIds`。
- observed snapshot：最近一次 `ObserveNodeState` 的 `state`、`warehouseVersion`、`observedAt`、
  `source`、`confidence`、`staleness`，用于解释本次决策；下一次危险决策前应重新 observe。

不适合保存：

- 把 `PowerOn` Activity 的 `success: true` 写成 `node.poweredOn = true` 并据此跳过观察。
- 把旧观察快照在 replay 后当成最新事实。
- 在 Workflow deterministic code 中直接读数据库、监控、BMC 或文件系统；这些 I/O 应放入 Activity。

### Activity 设计模式

命令 Activity 与观察 Activity 应分离。

```typescript
type CommandReceipt = {
  operationId: string;
  idempotencyKey: string;
  accepted: boolean;
  submittedAt: string;
  commandedState: "POWERED_ON";
  rawEvidenceRef?: string;
};

// 命令 Activity：只证明命令提交/调用结果，不证明目标状态已到达。
async function PowerOnNode(input: {
  nodeId: string;
  operationId: string;
  idempotencyKey: string;
}): Promise<CommandReceipt>;

type NodeObservation = {
  nodeId: string;
  state: "OFF" | "POWERING_ON" | "POWERED_ON" | "FAILED" | "UNKNOWN";
  warehouseVersion: string;
  observedAt: string;
  sources: string[];
  confidence: "confirmed" | "likely" | "weak" | "unknown";
  stalenessSeconds: number;
};

// 观察 Activity：读取外部运维数仓，返回可审计的观察快照。
async function ObserveNodeState(input: {
  nodeId: string;
  minFreshnessSeconds?: number;
}): Promise<NodeObservation>;
```

命令 Activity 的理想返回是 receipt、operation ID、幂等键、提交时间、错误分类和外部证据引用。
观察 Activity 的理想返回是 observed state、观察时间、数仓版本、来源、置信度和滞后边界。
两者可以关联同一 `operationId`，但语义不能合并。

### Reconcile loop 模式

```typescript
export async function BuildoutNodeWorkflow(input: {
  clusterId: string;
  nodeId: string;
  target: "POWERED_ON";
}) {
  const desired = {
    state: input.target,
    planVersion: "buildout-plan-v7",
  };

  let reconcileRequested = false;
  wf.setHandler(reconcileSignal, () => {
    reconcileRequested = true;
  });

  while (true) {
    const observed = await wf.executeActivity(ObserveNodeState, {
      nodeId: input.nodeId,
      minFreshnessSeconds: 120,
    });

    if (matches(observed, desired)) {
      return { status: "reached", observed };
    }

    const delta = computeDelta(observed, desired);

    if (delta.requiresHuman) {
      await wf.executeActivity(CreateRepairTicket, {
        nodeId: input.nodeId,
        observed,
        desired,
      });
    } else if (delta.command === "POWER_ON") {
      await wf.executeActivity(PowerOnNode, {
        nodeId: input.nodeId,
        operationId: wf.uuid4(),
        idempotencyKey: `${input.nodeId}:${desired.planVersion}:power-on`,
      });
    }

    reconcileRequested = false;
    await Promise.race([
      wf.sleep("30s"),
      wf.condition(() => reconcileRequested),
    ]);
  }
}
```

关键点：

1. `PowerOnNode` 返回成功后，loop 仍回到 `ObserveNodeState`。
2. `wf.sleep` 表达周期性 reconcile；`reconcileSignal` 表达外部事件触发的非周期 reconcile。
3. 每轮命令都使用幂等键、operation ID 和观察版本防止重复危险副作用。
4. 如果 loop 很长，应使用 Child Workflow 分区、Continue-As-New 截断历史，并在 Run 边界交接 desired state、
   pending operation、last observed snapshot metadata 和 processed external event IDs。

### Event History 的语义和恢复

Event History 记录两类历史：

- 命令历史：Workflow schedule 了 `PowerOnNode`，Activity 返回了某个 receipt。
- 观察历史：Workflow schedule 了 `ObserveNodeState`，Activity 返回了当时的 observed snapshot。

但它们都是 **历史事实**，不是“当前物理状态”。恢复时 Temporal replay 会用历史中的 Activity
结果重建变量；已完成的观察 Activity 不会因为 replay 自动重新查询外部数仓。
因此恢复路径应是：

```text
replay Event History
→ 恢复 desired/coordination state、pending timer/activity/signal/child
→ 到达下一次 decision fence
→ 安排新的 ObserveNodeState Activity
→ 用最新观察与 desired state reconcile
```

## MAF Durable Extension 在观察驱动架构下的建模

### Graph workflow state

MAF Durable Extension 的 graph shared state 应保存 graph 级协调状态和轻量观察快照，而不是观察状态真源。

适合保存：

- desired state / plan version / target milestone。
- `clusterId`、`nodeId`、`resourceGeneration`、`operationId`、`idempotencyKey`。
- 当前 graph/superstep、待处理消息、pending RequestPort、agent/HITL correlation ID。
- 最近一次观察快照的 `warehouseVersion`、`observedAt`、`state` 和 stale 标记。

不适合保存：

- 把 graph shared state 当成 node/rack/fabric 当前状态数据库。
- 用 executor 返回的 `success` 直接推进到“物理状态已达成”。
- 让 custom status 成为业务 dashboard 的资源状态真源。

### Executor 设计模式

MAF 也应拆成命令 executor 与观察 executor：

```text
ObserveNodeStateExecutor
  input:  nodeId, minFreshnessSeconds
  output: NodeObservation(state, warehouseVersion, observedAt, sources, confidence, staleness)

CompareDesiredObservedExecutor
  input:  desired state from shared state, NodeObservation
  output: Done | NeedCommand(delta) | NeedHuman(reason) | Wait(reason)

PowerOnNodeExecutor
  input:  nodeId, operationId, idempotencyKey, precondition
  output: CommandReceipt(accepted, operationId, submittedAt, rawEvidenceRef)

DelayOrWakeupExecutor / RequestPort
  input:  poll interval or external wakeup request
  output: ReconcileAgain
```

普通 executor 最终由 Durable Extension 映射到底层 Durable Task activity；因此它可以执行 DB/监控/BMC
I/O，但这些 I/O 的返回值仍应按“命令 receipt”或“观察 snapshot”分类。若需要 direct Durable primitives、
复杂 timer、sub-orchestration、DurableTaskClient 或 custom retry policy，应通过 MAF 已暴露的
subworkflow/RequestPort/agent surface、服务层 client、自写 Durable orchestrator 或 hybrid composition 接入。

### 等待观察到目标状态

RequestPort 适合表达“等待外部输入、人工确认或外部系统回调”，不应单独被理解为
“等待物理状态已达成”。等待目标状态应表达为 graph loop：

```text
ObserveNodeState
→ CompareDesiredObserved
→ if Done: finish
→ if NeedCommand: PowerOnNode → DelayOrWakeup → ObserveNodeState
→ if NeedHuman: RequestPort(operator/repair/vendor input) → ObserveNodeState
→ if Wait: durable timer / external wakeup → ObserveNodeState
```

如果外部运维数仓或监控系统能发出事件，可以用 Durable external event / RequestPort respond / service-layer
RaiseEvent 唤醒 graph，提前进入下一轮 `ObserveNodeState`。事件本身只说明“值得重新观察”，
最终状态仍以观察 executor 读到的数仓快照为准。

等价的 MAF graph 伪代码可以写成：

```text
sharedState.desired = { nodeId, state: POWERED_ON, planVersion }

ObserveNodeStateExecutor
  → returns NodeObservation

CompareDesiredObservedExecutor
  → if observation matches desired: route Done
  → if observation is stale/unknown: route DelayOrWakeup
  → if command is needed: route PowerOnNodeExecutor
  → if human repair is needed: route RequestPort

PowerOnNodeExecutor
  → returns CommandReceipt only
  → route DelayOrWakeup

DelayOrWakeup / RequestPort
  → on timer or external response
  → route ObserveNodeStateExecutor
```

### Custom status projection

MAF custom status 应是 **协调 live projection**，不是 desired state 或 observed state 的唯一真源。
可以投影：

- 当前 graph 阶段、pending RequestPort、最近一次命令 receipt、下一次 poll 时间。
- 最近一次 observed snapshot 的摘要、`warehouseVersion`、`observedAt` 和 `stale` 标记。
- 当前 loop 是 waiting、commanding、observing、human-blocked 还是 done。

业务 dashboard 的资源状态应直接查询外部运维数仓；custom status 只能作为运行中 workflow/graph 的辅助观察面。

## 与 Kubernetes controller pattern 的对比

Kubernetes controller 的核心是 `spec` 与 `status` 分离：controller 观察集群实际状态，
与 desired spec 对齐，然后更新外部世界或 status。裸金属 buildout 的观察驱动 process manager
可以借用同一模式，但要注意差异：

| 维度 | Kubernetes controller | Temporal / MAF 观察驱动 process manager |
| --- | --- | --- |
| Desired state | API server 中的 spec。 | Workflow/graph 的 desired state、plan version、阶段门禁；也可引用外部 blueprint，但要在协调事实线中记录接受版本。 |
| Observed state | controller 观察 cluster 并写 status。 | 外部运维数仓汇集监控、探测和日志；Workflow/graph 通过 observation Activity/executor 读取。 |
| Loop 承载者 | controller manager 中的 controller。 | Temporal Workflow / Child Workflow 或 MAF durable graph / subworkflow。 |
| Timer | workqueue rate limit、resync period。 | Temporal timer / Durable timer / graph delay；长 loop 需 history governance。 |
| 外部事件触发 | watch/informer 入队。 | Temporal Signal/Update、Durable external event、MAF RequestPort/respond、service-layer RaiseEvent。 |
| 历史治理 | controller 通常无 per-object event-sourced command history。 | Event History / Durable history 记录协调器命令、timer、activity/executor 返回和观察快照。 |

Temporal 和 MAF 都能表达 continuous reconcile loop，但都不应写成忙等无限循环。
长周期 buildout 应按 resource partition 拆分、使用 durable timers、处理外部 wakeup，并定期压缩历史或换 Run/instance 边界。

## 对既有分析的影响

本次已修正的点：

1. `process-manager-external-data-warehouse-architecture.md` 不应再写成“外部数据仓库是唯一 source of truth”
   或“资源状态、资源历史、业务审计全部由外部事实仓库主责”。准确表述是：
   Event History/Durable history 是协调命令与返回的事实线；外部运维数仓是观察状态事实线；
   两条事实线需要通过 reconcile loop 对齐。
2. 裸金属选型页中“若外部事实仓库是资源主事实线，MAF 不必保存完整资源事实”的表述应收紧为：
   若外部运维数仓是 **观察状态基准**，MAF/Temporal 都不应把 Activity success 当成物理状态；
   graph/hybrid 要成为主 process manager，必须亲自持有 desired/coordination 侧过程控制路径，
   并显式实现 observe/compare/command/wait loop。
3. POC gate 应增加：危险副作用前后必须用 observation Activity/executor 查询外部数仓；
   Activity/executor success 只能进入命令审计，不得直接推进物理状态。
4. MAF 定位只需从旧的“必须亲自持有资源事实线”修正为“必须亲自持有协调事实线和 reconcile loop”。
   观察驱动架构让 MAF 更接近 Temporal 的状态放置模型，但两者都要显式建模 reconcile，
   因而不存在 MAF 的本质优势反转。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| user | 用户在 2026-06-17 本次澄清：“Event History 确实是执行的主线，但是具体 cluster buildout 的状态要以外部数据仓库为观察基准（没法直接观察机器情况，只能依赖运维数仓）”。 | 确立双事实线：协调命令事实线与观察状态事实线。 |
| wiki | [裸金属 Cluster Buildout 的 Process Manager 平台选型](bare-metal-cluster-buildout-process-manager-selection.md) | 提供被修正的 MAF baseline 条件和裸金属 buildout scope。 |
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
| 正确架构是协调事实线与观察事实线并存，而不是外部数据仓库替代 Event History 成为唯一事实线。 | 用户本次澄清；Temporal/Durable Task/MAF source pages；裸金属选型页。 | 外部运维数仓的具体 schema、延迟、保真度和权限模型未在本文设计。 |
| Activity/executor success 不能作为物理状态到达的决策依据；它只证明命令调用或工具执行结果。 | 用户本次澄清；Temporal Activities 与 Durable Task/MAF executor 边界证据。 | 某些下层系统可提供强一致 operation status，但仍应作为观察证据读取并记录版本，而不是默认为 Activity success。 |
| Temporal Workflow 变量应保存 desired/coordination state 和带版本观察快照；最新 observed state 必须通过新的 observation Activity 读取外部数仓。 | Temporal Workflows、determinism、Activities source pages；Temporal mutable state 与 command handling raw evidence。 | SDK 细节按语言不同；伪代码只表达模式。 |
| Temporal Event History 同时记录命令历史和观察 Activity 返回的历史快照，但这些都是历史事实，不是当前物理状态真源。 | Temporal Workflows、Reset、Continue-As-New source pages；mutable state raw evidence；用户澄清。 | Event History 可关联外部审计和观察版本；它仍不是业务 dashboard 的资源状态替代。 |
| MAF Durable Extension 的 graph/shared state 应保存 desired/coordination state、资源身份映射和轻量观察快照；等待目标状态应通过观察 executor + graph loop，而不是只靠 RequestPort 或 custom status。 | MAF Durable Extension、checkpoint/state、dispatcher source pages；`DurableWorkflowRunner.SuperstepState` raw evidence。 | MAF graph loop 的长期 history、superstep、timer 和 versioning 边界仍需目标版本 PoC。 |
| Custom status 是运行中协调投影，不应作为外部观察状态真源；业务 dashboard 的资源状态应对齐外部运维数仓。 | `DurableWorkflowRunner.cs`、`DurableWorkflowResult.cs`、`DurableStreamingWorkflowRun.cs` raw evidence；MAF 能力边界页。 | 可以展示 last observed snapshot，但必须标注版本、观察时间和 stale 边界。 |
| 观察驱动架构让 MAF 在“资源状态不放在 graph state”这一点更接近 Temporal，但不会改变两者都必须显式实现 reconcile loop 的事实；MAF 不因此获得本质优势。 | 本页机制对比；Temporal-vs-MAF 能力边界；Temporal Task Queues、Message Passing、Continue-As-New/Reset source pages；MAF Durable Extension source pages。 | 最终排序仍依赖资源池路由、HITL/agent 比重、Durable Task hosting/backend、数仓延迟与 PoC 结果。 |
