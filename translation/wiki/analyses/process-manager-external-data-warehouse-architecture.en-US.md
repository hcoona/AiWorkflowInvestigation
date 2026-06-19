---
schema_version: 2
page_type: analysis
title: "Process Manager Architecture: Coordination-Command and Observation Source-of-Truth Streams"
status: active
created: 2026-06-17
updated: 2026-06-17
summary: "Analyzes the reconcile modeling boundaries for Temporal and the MAF Durable Extension when Event History is the coordination-command source-of-truth stream and the external operational data warehouse is the observed-state source of truth."
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

## Question

This page answers: in a bare-metal cluster buildout,
if **Temporal Event History / Durable Task history is the coordination-command
source-of-truth stream**, while **the external operational data warehouse is the
observation baseline for physical state**, how should Temporal and Microsoft
Agent Framework Durable Extension (referred to below as MAF Durable Extension)
model this?
Does this require correcting the previous statement
that "the external data warehouse is the only primary source-of-truth stream"?

On this page, the external operational data warehouse is understood according to
the user's clarification: it aggregates monitoring, probes, logs, and results
from operations systems, and is used to determine the actual observed state of
machines, nodes, networks, or acceptance items.
It is not automatically equivalent to a command ledger, lock service,
or writable operational resource store.
If an operation ledger, idempotency key, lease, inbox/outbox,
or command audit is required,
it must be explicitly designed as an adjacent operational control plane.
These responsibilities must not be ambiguously folded into the term "data
warehouse".

## Answer

**The previous analysis needs to be corrected.**
**The accurate model is not an either-or choice between Event History and an
external data warehouse.**
**It is an observation-driven dual source-of-truth stream model: Event History
is the source of truth for coordination commands and command returns; the
external operational data warehouse is the source of truth for the physical
world's observed state.**

In this architecture, when a Workflow issues `PowerOn(node-001)`
and receives Activity `{ success: true }`,
that only proves the orchestrator scheduled the command and
that the Activity returned success.
It does not prove that `node-001` has powered on, completed self-test,
joined the network, or reached the acceptance state.
The next decision must go through explicit observation:
the Workflow/graph schedules an observation Activity/executor to query the
external operational data warehouse, reads the observed state with time, source,
version, and confidence/staleness boundaries, then compares desired state with
observed state to decide whether to keep waiting, retry, compensate, skip, or
request human intervention.

This is closer to the Kubernetes controller pattern:

```text
Desired state / spec: workflow process goal, command intent, phase gate, idempotent operation plan
Observed state / status: monitoring, probes, log aggregation, and acceptance observations in the external operational data warehouse
Controller loop: workflow or graph explicitly observe -> compare -> command -> wait/trigger -> observe
```

**MAF's positioning does not need to be substantially upgraded.**
An observation-driven architecture narrows the difference around "who stores
complete resource state", because neither Temporal Workflow variables nor MAF
graph shared state should become the primary storage for physical state.
However, both must explicitly model the reconcile loop.
MAF does not gain an intrinsic advantage merely
because an external data warehouse exists.
Temporal remains more direct on the process-management plane,
including Workflow/Child Workflow identity, Signal/Update/Query,
Activity Task Queue routing, Event History auditability,
Continue-As-New/Reset/Worker Versioning, and similar mechanisms.
MAF's advantages remain primarily in Agent Framework graph, AIAgent,
RequestPort, and HITL authoring/runtime integration.
It is a candidate for primary process manager only
when the graph/hybrid itself owns the reconcile loop, resource identity mapping,
event interpretation, compensation, and coordination audit.

## Semantic boundaries of the dual source-of-truth streams

| Source-of-truth stream | Subject | What it records | What it cannot prove | Design consequence |
| --- | --- | --- | --- | --- |
| Coordination-command source-of-truth stream | Temporal Event History / Durable Task history / MAF durable graph checkpoint | What the Workflow/orchestrator decided, which Activity/executor it scheduled, which returns it received, which timer/event it waited on, and which coordination phase it entered. | It cannot by itself prove that a machine is truly in the target state at this moment. | Use it as the basis for process recovery, command audit, idempotent operation correlation, and the desired/command side of the controller loop. |
| Observation source-of-truth stream | External operational data warehouse | The machine state, time, source, version, confidence, and staleness boundaries observed by monitoring, probes, log aggregation, acceptance tasks, and operations systems. | It cannot by itself explain whether the workflow has already issued a command, whether an Activity completed, or whether a compensation was accepted by the orchestrator. | Use it as the observed-state source of truth for the physical world. Re-observe before and after every hazardous decision. |
| Command-return stream | Activity/executor return value | The result, receipt, operation ID, and error type for this command submission, API call, script execution, or tool invocation. | `success` does not mean the final state has been reached. `failure` also does not necessarily mean physical state was unchanged. | A command Activity should return a receipt and correlatable evidence, rather than hard-coding the target state as fact. |
| Alignment stream | Reconcile loop | The difference between desired and observed, the next delta, wait conditions, compensation, and human intervention. | A single read cannot eliminate monitoring staleness, external intervention, or hardware uncertainty. | Requires polling, event-triggered wakeup, staleness guard, idempotency key, and versioned decisions. |

The key difference from traditional saga/orchestration is
that a traditional saga often uses each step's success/failure return
as the primary signal for advancing or compensating.
An observation-driven buildout treats command returns
as **command-execution evidence** and external observations
as **state-progression evidence**.
Activity success only moves the controller into the next observation round.
It does not unconditionally advance the state machine.

Activity return values cannot be used as the basis for state decisions,
for reasons including:

- Bare-metal operations are often asynchronous.
  After a BMC or provisioning API accepts a command,
  the hardware may still be booting, running self-test, or reinstalling.
- Physical state can only be observed indirectly through monitoring, probes,
  logs, or operations systems, with sampling delay, aggregation delay,
  and missing data.
- External intervention may occur after an Activity returns,
  such as on-site cable changes, manual reboot, vendor repair,
  or configuration changes by another system.
- Partial failure is common: the command was successfully submitted, but PXE,
  RAID, NIC, firmware, switch, or power state only completed partially.
- Retries and timeouts cannot be mapped directly to physical state.
  After an Activity times out, the device may have succeeded;
  after an Activity succeeds, the device may later fail.

## Temporal modeling in an observation-driven architecture

### Workflow variables

Temporal Workflow variables should store **replayable coordination state**
and may cache versioned observation snapshots,
but must not treat cached snapshots as the true source
for current physical state.

Suitable for storage:

- desired state: target phase, target node state, plan version, gates,
  acceptance policy, compensation policy.
- coordination state: `clusterId`, `nodeId`, `operationId`, `idempotencyKey`,
  `currentGate`, `pendingCommand`, `lastCommandReceipt`, `childWorkflowIds`,
  `processedSignalIds`.
- observed snapshot: the latest `state`, `warehouseVersion`, `observedAt`,
  `source`, `confidence`, and `staleness` from `ObserveNodeState`,
  used to explain the current decision.
  Before the next hazardous decision, observe again.

Not suitable for storage:

- Writing the `PowerOn` Activity result `success: true`
  as `node.poweredOn = true` and skipping observation based on it.
- Treating an old observation snapshot as the latest fact after replay.
- Reading a database, monitoring system, BMC,
  or file system directly in Workflow deterministic code.
  Such I/O belongs in an Activity.

### Activity design pattern

Command Activities and observation Activities should be separated.

```typescript
type CommandReceipt = {
  operationId: string;
  idempotencyKey: string;
  accepted: boolean;
  submittedAt: string;
  commandedState: "POWERED_ON";
  rawEvidenceRef?: string;
};

// Command Activity: proves only command submission/call result, not that the target state has been reached.
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

// Observation Activity: reads the external operational data warehouse and returns an auditable observation snapshot.
async function ObserveNodeState(input: {
  nodeId: string;
  minFreshnessSeconds?: number;
}): Promise<NodeObservation>;
```

The ideal return from a command Activity is a receipt, operation ID,
idempotency key, submission time, error classification,
and external evidence reference.
The ideal return from an observation Activity is observed state,
observation time, data warehouse version, sources, confidence,
and staleness boundary.
The two can be correlated by the same `operationId`,
but their semantics must not be merged.

### Reconcile loop pattern

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

Key points:

1. After `PowerOnNode` returns success,
   the loop still returns to `ObserveNodeState`.
2. `wf.sleep` represents periodic reconcile.
   `reconcileSignal` represents non-periodic reconcile triggered by an external
   event.
3. Each command round uses an idempotency key, operation ID,
   and observation version to prevent repeated hazardous side effects.
4. If the loop is long-running,
   use Child Workflow partitioning and Continue-As-New to truncate history,
   and hand off desired state, pending operation,
   last observed snapshot metadata,
   and processed external event IDs across the Run boundary.

### Event History semantics and recovery

Event History records two kinds of history:

- Command history: the Workflow scheduled `PowerOnNode`,
  and the Activity returned a receipt.
- Observation history: the Workflow scheduled `ObserveNodeState`,
  and the Activity returned the observed snapshot at that time.

However, both are **historical facts**, not "current physical state".
During recovery, Temporal replay reconstructs variables using the Activity
results in history.
Completed observation Activities do not automatically re-query the external
operational data warehouse during replay.
Therefore, the recovery path should be:

```text
replay Event History
-> restore desired/coordination state, pending timer/activity/signal/child
-> arrive at the next decision fence
-> schedule a new ObserveNodeState Activity
-> reconcile the latest observation with desired state
```

## MAF Durable Extension modeling in an observation-driven architecture

### Graph workflow state

MAF Durable Extension's graph shared state should store graph-level coordination
state and lightweight observation snapshots, not the true source for observed
state.

Suitable for storage:

- desired state / plan version / target milestone.
- `clusterId`, `nodeId`, `resourceGeneration`, `operationId`, `idempotencyKey`.
- current graph/superstep, pending messages, pending RequestPort,
  agent/HITL correlation ID.
- `warehouseVersion`, `observedAt`, `state`,
  and stale marker for the latest observation snapshot.

Not suitable for storage:

- Treating graph shared state as the current-state database
  for nodes/racks/fabric.
- Using executor `success` to advance directly to "physical state achieved".
- Letting custom status become the true source of resource state
  for business dashboards.

### Executor design pattern

MAF should also split command executors from observation executors:

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

An ordinary executor is ultimately mapped by the Durable Extension to the
underlying Durable Task activity.
Therefore, it can perform DB/monitoring/BMC I/O,
but the return values from that I/O should still be classified
as either a "command receipt" or an "observation snapshot".
If direct Durable primitives, complex timers, sub-orchestration,
DurableTaskClient, or custom retry policy are required,
integrate them through MAF-exposed subworkflow/RequestPort/agent surface,
a service-layer client, a custom Durable orchestrator, or hybrid composition.

### Waiting until the target state is observed

RequestPort is suitable for expressing "wait for external input,
human confirmation, or external system callback".
It should not be understood by itself as "wait
until physical state has been achieved".
Waiting for the target state should be expressed as a graph loop:

```text
ObserveNodeState
-> CompareDesiredObserved
-> if Done: finish
-> if NeedCommand: PowerOnNode -> DelayOrWakeup -> ObserveNodeState
-> if NeedHuman: RequestPort(operator/repair/vendor input) -> ObserveNodeState
-> if Wait: durable timer / external wakeup -> ObserveNodeState
```

If the external operational data warehouse or monitoring system can emit events,
use Durable external event / RequestPort respond / service-layer RaiseEvent to
wake the graph and enter the next `ObserveNodeState` round earlier.
The event itself only means "it is worth observing again".
The final state still comes from the data warehouse snapshot read by the
observation executor.

Equivalent MAF graph pseudocode can be written as:

```text
sharedState.desired = { nodeId, state: POWERED_ON, planVersion }

ObserveNodeStateExecutor
  -> returns NodeObservation

CompareDesiredObservedExecutor
  -> if observation matches desired: route Done
  -> if observation is stale/unknown: route DelayOrWakeup
  -> if command is needed: route PowerOnNodeExecutor
  -> if human repair is needed: route RequestPort

PowerOnNodeExecutor
  -> returns CommandReceipt only
  -> route DelayOrWakeup

DelayOrWakeup / RequestPort
  -> on timer or external response
  -> route ObserveNodeStateExecutor
```

### Custom status projection

MAF custom status should be a **live coordination projection**,
not the only true source of desired state or observed state.
It can project:

- Current graph phase, pending RequestPort, latest command receipt,
  and next poll time.
- Summary of the latest observed snapshot, `warehouseVersion`, `observedAt`,
  and `stale` marker.
- Whether the current loop is waiting, commanding, observing, human-blocked,
  or done.

For resource state, a business dashboard should query the external operational
data warehouse directly.
Custom status can only serve as an auxiliary observation surface
for a running workflow/graph.

## Comparison with the Kubernetes controller pattern

The core of a Kubernetes controller is the separation between `spec`
and `status`: the controller observes the actual cluster state,
aligns it with the desired spec, and then updates the external world or status.
An observation-driven process manager
for bare-metal buildout can reuse the same pattern, but the differences matter:

| Dimension | Kubernetes controller | Temporal / MAF observation-driven process manager |
| --- | --- | --- |
| Desired state | The spec in the API server. | The Workflow/graph desired state, plan version, and phase gates. It can also reference an external blueprint, but the accepted version must be recorded in the coordination-command source-of-truth stream. |
| Observed state | The controller observes the cluster and writes status. | The external operational data warehouse aggregates monitoring, probes, and logs. The Workflow/graph reads it through an observation Activity/executor. |
| Loop owner | The controller in controller manager. | Temporal Workflow / Child Workflow or MAF durable graph / subworkflow. |
| Timer | Workqueue rate limit and resync period. | Temporal timer / Durable timer / graph delay. Long loops require history governance. |
| External event trigger | Watch/informer enqueue. | Temporal Signal/Update, Durable external event, MAF RequestPort/respond, service-layer RaiseEvent. |
| History governance | Controllers usually do not have per-object event-sourced command history. | Event History / Durable history records orchestrator commands, timers, activity/executor returns, and observation snapshots. |

Temporal and MAF can both express continuous reconcile loops,
but neither should be implemented as a busy-waiting infinite loop.
Long-running buildouts should be partitioned by resource, use durable timers,
handle external wakeups,
and periodically compact history or change the Run/instance boundary.

## Impact on existing analyses

Items corrected by this update:

1. `process-manager-external-data-warehouse-architecture.md` should no longer
   say that "the external data warehouse is the only source of truth" or that
   "resource state, resource history, and business audit are all primarily owned
   by the external fact warehouse".
   The accurate statement is:
   Event History/Durable history is the source-of-truth stream
   for coordination commands and command returns;
   the external operational data warehouse is the observed-state source-of-truth
   stream; the two source-of-truth streams must be aligned through a reconcile
   loop.
2. The statement in the bare-metal selection page
   that "if the external fact warehouse is the resource primary source-of-truth
   stream, MAF does not need to store complete resource facts" should be
   tightened to: if the external operational data warehouse is the
   **observed-state baseline**, neither MAF nor Temporal should treat Activity
   success as physical state; for graph/hybrid to become the primary process
   manager, it must itself own the desired/coordination-side process control
   path and explicitly implement the observe/compare/command/wait loop.
3. The POC gate should add: before and after hazardous side effects,
   the external data warehouse must be queried through an observation
   Activity/executor; Activity/executor success may only be recorded in command
   audit and must not directly advance physical state.
4. MAF positioning only needs to be corrected from the old "must itself own the
   resource source-of-truth stream" to "must itself own the coordination
   source-of-truth stream and reconcile loop".
   The observation-driven architecture makes MAF closer to Temporal in terms of
   state placement, but both must explicitly model reconcile, so there is no
   intrinsic advantage reversal in favor of MAF.

## Evidence and limitations

### Evidence units

| Type | Reference | Description |
| --- | --- | --- |
| user | User's clarification on 2026-06-17: “Event History 确实是执行的主线，但是具体 cluster buildout 的状态要以外部数据仓库为观察基准（没法直接观察机器情况，只能依赖运维数仓）”. | Establishes the dual source-of-truth streams: the coordination-command source-of-truth stream and the observed-state source-of-truth stream. |
| wiki | [Process Manager Platform Selection for Bare-Metal Cluster Buildout](bare-metal-cluster-buildout-process-manager-selection.en-US.md) | Provides the corrected MAF baseline condition and bare-metal buildout scope. |
| wiki | [Capability Boundaries Between Temporal and the MAF Durable Extension](../../../wiki/analyses/temporal-vs-maf-durable-extension.md) | Provides a mechanism comparison between the two across Event History, Task Queue, Signal/Update/Query, RequestPort, custom status, graph runner, and agent surface. |
| wiki | [Temporal Workflows Documentation](../../../wiki/sources/temporal/workflows-docs.md), [Temporal Workflow Determinism Constraints Documentation](../../../wiki/sources/temporal/workflow-deterministic-constraints-docs.md), [Temporal Activities Documentation](../../../wiki/sources/temporal/activities-docs.md) | Supports Temporal workflow replay, deterministic workflow code, and Activity external I/O boundaries. |
| wiki | [Temporal Message Passing Documentation](../../../wiki/sources/temporal/message-passing-docs.md), [Temporal Child Workflows Documentation](../../../wiki/sources/temporal/child-workflows-docs.md), [Temporal Task Queues Documentation](../../../wiki/sources/temporal/task-queues-docs.md), [Temporal Continue-As-New Documentation](../../../wiki/sources/temporal/continue-as-new-docs.md), [Temporal Reset Documentation](../../../wiki/sources/temporal/reset-docs.md) | Supports Temporal runtime interaction, resource partitioning, worker routing, and history governance semantics. |
| wiki | [Durable Task Orchestrations Documentation](../../../wiki/sources/azure-durable-functions/orchestrations-docs.md), [Durable Task Code Constraints Documentation](../../../wiki/sources/azure-durable-functions/code-constraints-docs.md), [Durable Task External Events Documentation](../../../wiki/sources/azure-durable-functions/external-events-docs.md), [Durable Task Instance Management Documentation](../../../wiki/sources/azure-durable-functions/instance-management-docs.md) | Supports Durable Task event sourcing/replay, determinism, external events, and instance ID boundaries. |
| wiki | [Microsoft Agent Framework Durable Extension Documentation](../../../wiki/sources/microsoft-agent-framework/durable-extension-docs.md), [Durable Workflow Registration Source Code](../../../wiki/sources/microsoft-agent-framework/durable-workflow-registration-source.md), [Durable Executor Dispatcher Source Code](../../../wiki/sources/microsoft-agent-framework/durable-executor-dispatcher-source.md), [Workflow Checkpoints Documentation](../../../wiki/sources/microsoft-agent-framework/checkpoints-docs.md), [Workflow State Documentation](../../../wiki/sources/microsoft-agent-framework/state-docs.md) | Supports the recovery boundaries of MAF Durable Extension graph workflow, executor dispatch, checkpoint/state, and Durable Task-backed execution. |
| raw | `raw/git/github.com/temporalio/temporal/service/history/workflow/mutable_state_impl.go:127-162,4200-4265,5390-5443`, `raw/git/github.com/temporalio/temporal/service/history/api/respondworkflowtaskcompleted/workflow_task_completed_handler.go:168-223,1029-1088`, `raw/git/github.com/temporalio/temporal/service/matching/matching_engine.go:580-660` | Source evidence for Temporal mutable state, Activity/Timer event application, command handling, Continue-As-New validation, and Task Queue task dispatch. |
| raw | `raw/git/github.com/microsoft/agent-framework/dotnet/src/Microsoft.Agents.AI.Workflows/IWorkflowContext.cs:13-197`, `raw/git/github.com/microsoft/agent-framework/dotnet/src/Microsoft.Agents.AI.DurableTask/Workflows/DurableWorkflowContext.cs:10-120`, `raw/git/github.com/microsoft/agent-framework/dotnet/src/Microsoft.Agents.AI.DurableTask/Workflows/DurableExecutorDispatcher.cs:41-129,172-186`, `raw/git/github.com/microsoft/agent-framework/dotnet/src/Microsoft.Agents.AI.DurableTask/Workflows/DurableWorkflowRunner.cs:67-210,254-284`, `raw/git/github.com/microsoft/agent-framework/dotnet/src/Microsoft.Agents.AI.DurableTask/Workflows/DurableWorkflowResult.cs:5-23`, `raw/git/github.com/microsoft/agent-framework/dotnet/src/Microsoft.Agents.AI.DurableTask/Workflows/DurableStreamingWorkflowRun.cs:100-150`, `raw/git/github.com/microsoft/agent-framework/dotnet/src/Microsoft.Agents.AI.DurableTask/DurableAgentContext.cs:80-122` | Source evidence for MAF ordinary executor context, graph state, executor-to-Durable Task dispatch, RequestPort external event, subworkflow orchestration, custom status/result, streaming status reads, and durable agent context. |

### Supported claims

| Claim | Evidence | Limitation |
| --- | --- | --- |
| The correct architecture has both a coordination-command source-of-truth stream and an observation source-of-truth stream, rather than the external data warehouse replacing Event History as the only source-of-truth stream. | The user's clarification; Temporal/Durable Task/MAF source pages; bare-metal selection page. | This article does not design the specific schema, latency, fidelity, or permission model of the external operational data warehouse. |
| Activity/executor success cannot be used as the decision basis for physical state arrival. It only proves the result of a command call or tool execution. | The user's clarification; evidence on Temporal Activities and Durable Task/MAF executor boundaries. | Some lower-level systems can provide strongly consistent operation status, but it should still be read and versioned as observation evidence rather than assumed to be Activity success. |
| Temporal Workflow variables should store desired/coordination state and versioned observation snapshots. The latest observed state must be read from the external data warehouse through a new observation Activity. | Temporal Workflows, determinism, and Activities source pages; raw evidence for Temporal mutable state and command handling. | SDK details differ by language. The pseudocode only expresses the pattern. |
| Temporal Event History records both command history and historical snapshots returned by observation Activities, but these are historical facts, not the true source for current physical state. | Temporal Workflows, Reset, and Continue-As-New source pages; mutable state raw evidence; user clarification. | Event History can correlate external audit and observation versions. It still is not a substitute for resource state in a business dashboard. |
| MAF Durable Extension graph/shared state should store desired/coordination state, resource identity mapping, and lightweight observation snapshots. Waiting for target state should use an observation executor plus graph loop, rather than only RequestPort or custom status. | MAF Durable Extension, checkpoint/state, and dispatcher source pages; `DurableWorkflowRunner.SuperstepState` raw evidence. | Long-running history, superstep, timer, and versioning boundaries for the MAF graph loop still require a target-version POC. |
| Custom status is a runtime coordination projection and should not be the true source for external observed state. Resource state in business dashboards should align with the external operational data warehouse. | `DurableWorkflowRunner.cs`, `DurableWorkflowResult.cs`, and `DurableStreamingWorkflowRun.cs` raw evidence; MAF capability-boundaries page. | It may display the last observed snapshot, but must annotate version, observation time, and stale boundary. |
| The observation-driven architecture makes MAF closer to Temporal on the point that "resource state is not stored in graph state", but it does not change the fact that both must explicitly implement a reconcile loop. MAF therefore does not gain an intrinsic advantage. | The mechanism comparison on this page; Temporal-vs-MAF capability boundaries; Temporal Task Queues, Message Passing, Continue-As-New/Reset source pages; MAF Durable Extension source pages. | Final ranking still depends on resource-pool routing, the share of HITL/agent work, Durable Task hosting/backend, data warehouse latency, and POC results. |
