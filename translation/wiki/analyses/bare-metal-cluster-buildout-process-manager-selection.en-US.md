---
schema_version: 2
page_type: analysis
title: "Process Manager Platform Selection for Bare-Metal Cluster Buildout"
status: active
created: 2026-06-16
updated: 2026-06-17
summary: "Compares Temporal, Azure Durable Functions, Microsoft Agent Framework Durable Workflow Extension, Apache Airflow, and LangGraph for carrying the primary process manager responsibility in bare-metal cluster buildout."
maintenance:
  edit_policy: update
validation:
  body_contract: analysis-decision-memo
tags:
  - bare-metal
  - cluster-buildout
  - platform-selection
  - temporal
  - azure-durable-functions
  - microsoft-agent-framework
  - durable-extension
  - airflow
  - langgraph
---

## Decision

Based on the business modeling analysis,
if the goal is to build the primary process manager
for a new bare-metal cluster buildout,
**Temporal has the highest modeling fit with the scenario at the core
resource-process modeling dimension and should be treated as the primary
baseline.**

**Azure Durable Functions (direct)** is close to Temporal on the durable
orchestration basics of orchestration instance, sub-orchestration, activity,
external event, entity, history/replay, and versioning.
However, it lacks the activity-level active resource-pool routing capability
that Temporal has with `taskQueue`.
For a bare-metal buildout where network, credentials,
and dependencies diverge dynamically by node/rack/fabric,
Azure Durable Functions should be demoted from "same-tier strong candidate
as Temporal" to a **secondary but still strong conditional POC candidate**.
It should only enter primary-baseline comparison
if the resource-pool topology can be planned statically,
or if the team accepts extra deployment design using multiple Function Apps,
WorkItemFilters, or standalone workers.

**Microsoft Agent Framework Durable Workflow Extension** should not be demoted
automatically just because it adds "another graph mapping layer".
The source shows that it is a composition layer that maps Agent Framework graph,
executor, agent, and RequestPort onto Durable Task primitives in an integrated
way.
If controllable agent/graph/HITL is a first-class requirement,
**within the Azure/Durable Task route the preferred POC is MAF Durable Extension
or a direct Durable + MAF hybrid**.
But the MAF graph surface is not a strict superset of direct primitives;
a normal executor has `IWorkflowContext`,
not the full `TaskOrchestrationContext`.
**If the business treats the external operational data warehouse as the
observed-state source of truth while Event History / Durable Task history
remains the coordination command truth line, MAF does not need to persist the
full observed state itself; however, a Durable Extension-backed graph/hybrid
still must stably reference external resource identity, own the
desired/coordination-side process-control path, and explicitly implement an
observe/compare/command/wait reconcile loop before it can qualify for the
primary process manager baseline.**
**Otherwise it is more accurately an agent/HITL adapter layered on top of
durable orchestration.**

**Apache Airflow** and **LangGraph** have first-class modeling objects
(DAG/DagRun/TaskInstance and graph/thread/checkpoint)
that fit the long-running resource-process control path poorly.
Airflow can serve as perimeter DAG scheduling, approval, reporting,
or a neighboring POC; LangGraph can serve as an agent/HITL adapter
or neighboring POC.
**If long-term domain state, event interpretation, localized catch-up, and
compensation decisions are owned by a system outside these frameworks, that
external system is the real process manager.**

**Decision basis:** a buildout must handle long-running execution,
interactive events, entity-oriented local state, real-world side effects,
localized failure recovery, human/vendor/AI involvement,
and localized catch-up across node/rack/fabric.
The detailed modeling comparison matrix below supports this conclusion.

| Candidate | Modeling Positioning |
| --- | --- |
| Temporal | Primary baseline for core resource-process modeling; Workflow Execution, Child Workflow, Signal/Update, Event History, and Continue-As-New have the highest modeling fit. |
| Azure Durable Functions (direct) | Secondary but still strong conditional durable orchestration POC candidate; orchestration instance, sub-orchestration, activity, external event, and entity are close to the scenario, but activity-level active resource-pool routing is weaker than Temporal. |
| Microsoft Agent Framework Durable Extension | Strong agent/graph/HITL POC or hybrid candidate within the Azure/Durable Task route; if the external operational data warehouse is the observed-state baseline, the graph/hybrid can avoid persisting the full observed state, but it must stably reference external resource identity and personally carry the desired/coordination-side process-control path, explicit reconcile loop, event interpretation, localized catch-up, compensation decisions, side-effect boundary, and coordination audit before it can enter the primary process manager baseline. |
| Apache Airflow | Perimeter DAG scheduling, approval, or neighboring POC; DAG/DagRun/TaskInstance modeling has low fit with long-running resource processes. |
| LangGraph | Agent/HITL adapter or neighboring POC; graph/thread/checkpoint modeling has low fit with the long-running resource-process control path. |

## Scope

This page discusses buildout for physical-machine / bare-metal clusters: nodes,
racks and network connections, BMC, firmware/BIOS/RAID/NIC, PXE/iPXE,
OS provisioning, drivers/kernel, bare-metal resource management,
HPC/cluster schedulers, foundational services, burn-in, acceptance,
and integration validation.

It does not recast the problem as Kubernetes cluster provisioning,
GitOps application deployment, a plain ETL DAG, or a one-off CI/CD pipeline.
Metal3, Ironic, MAAS, Tinkerbell, Foreman, Cobbler, xCAT, Slurm,
and Redfish can be lower-level or adjacent control planes in the buildout,
but this page only evaluates whether Temporal,
Azure Durable Functions / Durable Task,
Microsoft Agent Framework Durable Workflow Extension, Airflow,
and LangGraph are suitable
for the upper-layer long-running process management role.

## Rationale

### Cognitive baseline: bare-metal control planes are not just shell commands

The lower-level tools and protocols in bare-metal buildout already own domain
objects, lifecycle, or resource state.
The primary process manager should coordinate, observe, and compensate them,
not rewrite them into stateless command sequences.

| Object | Responsibility boundary used in this page |
| --- | --- |
| Redfish | Standard layer for BMC/hardware management; suitable as the hardware-management protocol behind Activity calls, not as a workflow engine. |
| MAAS | Physical-server resource pool and machine-lifecycle control plane; suitable for boot, check, deploy, tear down, and redeploy operations. |
| Ironic | Bare-metal provisioning control plane; manages physical machines through APIs, plug-ins, PXE, IPMI/Redfish, and related mechanisms. |
| Tinkerbell | Bare-metal provisioning engine; includes boot, BMC interaction, metadata service, and a provisioning workflow engine. |
| Foreman | Control plane for server lifecycle, provisioning, configuration, orchestration, monitoring, and API/UI. |
| Cobbler | Linux network installation, DNS/DHCP, power management, and configuration orchestration subsystem. |
| xCAT | Cluster/HPC/datacenter deployment and management tool covering hardware discovery, OS provisioning, and parallel system administration. |
| Metal3 | Kubernetes/CRD-style control plane for BareMetalHost and related hardware/firmware/resource management. |
| Slurm | Cluster resource management and job scheduling system; suitable as the execution plane for buildout acceptance and resource validation at later stages. |

This yields a shared boundary:
external inventory/resource graph/audit store is a mandatory factual layer
and architecture component driven by bare-metal domain facts.
It is not a proprietary limitation of Airflow, LangGraph, Temporal,
Azure Durable Functions, or Microsoft Agent Framework.
The workflow runtime manages process and execution;
the bare-metal toolchain manages hardware, installation, resource pools, jobs,
and lifecycle facts.
The real selection question is
which runtime can carry the process-level control path, runtime event ingress,
localized failure catch-up, and side-effect boundary with the least distortion.

### State layering in bare-metal buildout

At this cognitive baseline, one real buildout has at least four layers of state,
and they cannot all be stuffed into workflow-engine runtime state:

| Layer | Example | Selection implication |
| --- | --- | --- |
| Resource fact layer | node, rack, switch port, BMC address, PXE network, firmware, RAID, OS image, Slurm partition. | Should be held by an external inventory/resource graph/audit store. |
| Physical side-effect layer | flashing firmware, changing BIOS, creating RAID, installing OS, rebooting, racking, recabling, vendor on-site action. | Must be protected with idempotency, read-back verification, locks, compensation, and human confirmation. |
| Process-state layer | blueprint, stage, gates, failure branches, remediation branches, catch-up conditions, acceptance level. | The primary process manager should own process-level state and the control path. |
| Collaboration/audit layer | human approvals, vendor replies, AI diagnostics, test reports, acceptance facts. | Needs queryable, auditable records that can be projected into the business UI. |

Therefore, the key platform-selection question is not whether DAG, Workflow,
Task, Sensor, or Signal terminology is the same.
It is what state the runtime persists, which object receives external events,
what is recovered after failure, how side effects are isolated,
and how the plan evolves within an auditable boundary.

### Shared POC gates and first-class modeling anchors

This page does not turn every engineering prerequisite into a defect of one
candidate.
The comparison should be split into two layers first:

1. **Shared POC gates**: all candidates must prove the external
   inventory/resource graph, business event schema, auth, dedup,
   ordering/concurrency, audit, long waits, HITL, idempotency keys, read-back
   verification, compensation, real-device reconcile, version/migration
   discipline, and dashboard projection.
   Runtime state, metadata DB, checkpoints, stores,
   or memory cannot replace the physical observed-state baseline;
   Event History / Durable Task history remains the coordination command truth
   line and cannot replace external observed state.
2. **Runtime first-class modeling anchors**:
   after the shared gates are satisfied,
   compare which first-class objects carry the process-level control path with
   the least distortion: where the long-running process identity lives, which
   running object receives external events, how local failures are isolated and
   caught up, how replay/reset/fork/rerun/backfill protect real side effects,
   and whether version migration restores the process object or just the
   scheduling/graph execution context.

This distinction cannot be reversed to wash away real mismatches.
If an Airflow, LangGraph, Azure Durable Functions, MAF Durable Extension,
or Temporal solution depends on a separate domain process service to hold
long-running process state, event interpretation, localized catch-up,
compensation decisions, and business audit, then that service is the primary
process manager as defined here.
The runtime it calls is only a scheduler, executor, durable execution runtime,
workflow adapter, or agent/HITL adapter.
So the real product difference is not "who lacks external inventory,
idempotency, or dashboard concerns",
but "how much of the primary process-management logic must live outside the
runtime, and whether the runtime's first-class objects flatten the long-running
resource process into a neighboring model".

### Evidence matrix for the first strong candidates

Temporal, Azure Durable Functions / Durable Task,
and MAF Durable Workflow Extension differ in subtle ways,
so they cannot be ranked by "whose docs are larger".
The matrix below separates projected first-party evidence,
the judgments that can currently be supported, and the remaining POC gaps:

| Dimension | Temporal | Azure Durable Functions / Durable Task | MAF Durable Workflow Extension | Current judgment |
| --- | --- | --- | --- | --- |
| Long-running process identity / partition | Workflow Execution and Child Workflow; Child Workflow can use Workflow IDs by host/resource and isolate Event History. | Orchestration instance ID can map to external entities; sub-orchestration is an SDK feature; instance IDs can be specified, but random IDs distribute load better. | Graph workflows are registered as Durable Task orchestrations; subworkflow maps to sub-orchestration; resource identity must pass through graph/executor/Durable Task mappings or a hybrid boundary. | Temporal is the most direct evidence; Azure is not weak, but resource-derived ID hotspots and sub-orchestration catch-up still need validation; MAF does not lose Durable Task identity primitives, but resource-identity binding needs POC. |
| Command/event ingress | Signals are async messages; Updates can validate, track, and return results, but they are still not a full command gateway. | External events are one-way async; instance management APIs can start/query/terminate/suspend/resume/purge, but synchronous command results need outer-service design. | Request port maps to external events; HITL and agent workflows are more integrated, but auth, timeout, dead-letter handling, and audit still need the application layer. | If buildout commands need synchronous validation and results, Temporal has stronger current evidence; Azure/MAF are feasible, but the command-service boundary matters more. |
| Activity resource-pool routing | Each Activity / Child Workflow can be assigned or inherit a Task Queue; workflow code can route different activities to different worker fleets by activity type, resource, SLA, network, or credentials. | DTS can dispatch work items across Function Apps; WorkItemFilters let an app declare which function names it can handle; orchestration cannot proactively choose the target Function App or resource pool based on the current activity input. | The graph executor still lands on Durable Task work items and hosting topology; if using Azure Functions hosting, resource-pool routing inherits similar limits. | For a buildout with heterogeneous network/credential/dependency needs, Temporal provides a runtime-level dynamic routing surface; Azure/DTS is closer to static deployment topology + passive filtering, so it should be downgraded to a conditional POC rather than the same-tier primary baseline. |
| Long waits / timers | Timer is a durable wait inside Workflow Execution. | Durable timers support waiting; JS/Python/PowerShell Durable Functions have a six-day limit, while .NET/Java support arbitrarily long timers; Durable Task SDK language-state needs revalidation. | Inherits Durable Task-backed wait paths, but graph/request-port long waits, timeouts, and recovery still need POC. | The target language changes the ranking; it cannot be generalized to mean Azure cannot support multi-week waits. |
| Versioning, recovery, migration | Reset, Continue-As-New, and Worker Versioning boundaries are fairly complete, but they are not physical rollback or arbitrary migration. | Orchestration versioning is built in; the instance binds to a version at creation time, and worker/client can use version matching and conditional branches. | Checkpoint/recover supports graph workflows; checkpoint does not promise arbitrary topology migration; durable graph versioning still needs testing on the target version. | Azure's versioning gap has narrowed; MAF's graph/executor/checkpoint compatibility remains the key uncertainty. |
| Hosting/backend | Need to validate Temporal server/backend, worker placement, history growth, and ops cost. | Durable Functions and standalone SDKs share core capability; standalone workers can run on Kubernetes/VM/etc., but the SDK connects to a Durable Task Scheduler managed backend. **Note:** Azure Functions hosting affects resource-pool granularity and dependency isolation in multi-graph heterogeneous workload scenarios (see [MAF Durable Function Apps and Temporal Scale-out Boundaries](../../../wiki/analyses/maf-durable-functions-vs-temporal-scale-out.md)); standalone Durable Task workers can mitigate this. | Supports Azure Functions and BYOC/self-host workers; self-host workers still connect to the Durable Task Scheduler backend; docs use `--pre` / `--prerelease` for installation. | If fully self-hosted or air-gapped operation is mandatory, the Azure/MAF Scheduler dependency is a key risk; if an Azure-connected backend is acceptable, Azure/MAF becomes more competitive. **Hosting choice affects scale-out granularity**: Azure Functions hosting is more likely to run into resource-pool granularity issues in multi-graph heterogeneous scenarios; standalone Durable Task workers can be deployed independently per workload. |
| AI / HITL integration | Integrates through Activities, Signals/Updates, and external agent platforms. | Integrates through activities, external events, entities, or external services. | Agent, multi-agent, HITL, and graph workflow are first-class capabilities and map onto Durable Task-backed execution. | If Agent Framework control is a first-class requirement, MAF is the preferred POC within the Azure / Durable Task route; the boundary is that it is not a strict graph-level superset of direct primitives. |

See
[Process Manager Architecture: Coordination Truth Line and Observed Truth Line](process-manager-external-data-warehouse-architecture.en-US.md)
for the specific modeling split between "coordination command truth line +
external observed-state truth line" and Temporal vs. MAF.

So, when this page later says "baseline",
it only means a POC comparison point or reference architecture,
not the final winner.
Temporal's value is not merely that its evidence is more complete
or its variables are fewer;
it is that it has the highest fit with core resource-process modeling
and activity resource-pool routing.
Azure Durable Task still needs to be retained
as a durable orchestration candidate for comparison,
but in the target scenario
where runtime-level dynamic activity routing is required it should no longer be
written as the same-tier primary baseline as Temporal.
Whether MAF enters the primary baseline depends on
whether the graph / hybrid path itself carries the primary process duties,
not on whether using MAF somehow reduces Durable Task primitives.

### Relationship between direct Durable primitives and MAF

This page defines Direct Durable primitives
as the durable runtime / control primitives exposed directly by Durable
Functions / Durable Task to orchestrator, client, and entity authors: activity,
sub-orchestration, durable timer, external event wait / raise, entity call /
signal / lock, `ContinueAsNew`, custom status, replay-safe time / GUID, and the
instance management APIs for start, query, terminate, suspend, resume, purge,
and restart.
They are the low-level durable execution/control surface;
they do not mean "do not use MAF".

MAF Durable Extension does not remove those underlying capabilities.
The source shows ordinary executor mapping to `CallActivityAsync`,
RequestPort mapping to `SetCustomStatus` + `WaitForExternalEvent`,
the agent executor running through a Durable Entity-backed `DurableAIAgent`,
subworkflow mapping to `CallSubOrchestratorAsync`,
`ConfigureDurableOptions` providing additive configuration for agents
and workflows and exposing Durable Task worker/client builders,
and `DurableAgentContext` exposing schedule orchestration, get status,
and raise event to the durable agent/tool context.

But the MAF graph surface is not a strict superset either.
A normal executor receives `DurableWorkflowContext` / `IWorkflowContext`,
not an arbitrarily callable `TaskOrchestrationContext`.
So complex direct primitives must be accessed through graph mapping,
agent/tool context, service-layer `DurableTaskClient`,
a custom Durable orchestrator, or a hybrid composition.
For bare-metal buildout, this means:
if the first-class requirement is controllable agent / graph / HITL authoring,
MAF is a valuable composition surface;
if the first-class requirement is to directly manipulate all Durable primitives,
keep a direct Durable or hybrid boundary.

## Business modeling comparison

The primary process object in bare-metal buildout is a long-running,
addressable, locally catch-up-able cluster/rack/node/fabric resource process.
The comparison below evaluates the modeling fit of the five candidates against
that scenario.

### Core modeling dimension comparison

| Modeling dimension | Temporal | Azure Durable Functions | MAF Durable Extension | Apache Airflow | LangGraph | Modeling distortion judgment |
| --- | --- | --- | --- | --- | --- | --- |
| Long-running resource-process identity | Workflow Execution is the process identity; Child Workflow can express node/rack/fabric sub-processes. | Orchestration instance is the process identity; sub-orchestration can express sub-processes. | Graph workflow instance can carry the overall process; resource identity must pass through graph node, executor, Durable Task instance/entity, and multiple mapping layers. | DagRun is a scheduling-interval instance; TaskInstance is task execution; resource identity is not a first-class modeling object. | Thread is the conversation/graph execution; checkpoint is a state snapshot; resource identity is not a first-class modeling object. | Temporal and Azure Durable distort less; MAF needs an extra mapping layer; Airflow and LangGraph lack a first-class resource-process identity object. |
| Resource partitioning and localized failure catch-up | Child Workflow isolates history, waiting, and failure; after local repair it can catch up independently. | Sub-orchestration isolates history, waiting, and failure; after local repair it can catch up independently. | Subworkflow maps to sub-orchestration; graph/executor/checkpoint binding to resource identity needs additional conventions. | Mapped task instances can run concurrently; a single task failure does not isolate the others directly and relies on trigger rules; catch-up happens through task retry or DAG rerun. | Subgraphs can be modularized; checkpoint can recover, but it is a point-in-time snapshot rather than a localized history line for a resource partition. | Temporal and Azure Durable distort less; MAF needs conventions; Airflow is task-level retry; LangGraph is point-in-time recovery. |
| Runtime business-event ingress | Signal is an async message; Update is a validated command; Query is read-only; Cancellation is cooperative cancellation. | External event is an async message; RaiseEvent delivers it; `WaitForExternalEvent` receives it inside the orchestration; there is no Update equivalent. | RequestPort actively waits for external input; pending status is projected; respond turns into an external event; it is not the same as business-command completion. | Sensor waits for external conditions; external trigger starts a DagRun; XCom passes data between tasks; there is no command API for an in-progress orchestration. | Interrupt pauses execution and waits for human input; resume continues; Human-in-the-loop nodes exist, but interrupt is graph-execution suspension, not a process-level command entry point. | Temporal is more unified with four entry types; Azure Durable has external events; MAF is oriented toward form-style HITL; Airflow is trigger-level; LangGraph is execution suspension. |
| Physical side-effect boundary | Activity is the explicit external I/O boundary; Event History records scheduling, completion, and failure facts. | Activity is the explicit external I/O boundary; event sourcing records scheduling, completion, and failure facts. | Ordinary executor goes through Activity; agent executor goes through entity; RequestPort goes through external event; subworkflow goes through sub-orchestration. | Operator wraps the side effect; TaskInstance executes it; deferrable operator can wait asynchronously; side-effect discipline is the operator author's responsibility. | Tool is the side-effect boundary; agent executor calls the tool; checkpoint state before and after execution is graph execution state, not directly a side-effect fact stream. | Temporal and Azure Durable are more unified; MAF adds another executor-mapping layer; Airflow depends on operator discipline; LangGraph is a tool boundary. |
| History governance and version evolution | Continue-As-New explicitly truncates history; Reset replays; workflow versioning and Worker Versioning exist. | ContinueAsNew explicitly truncates history; orchestration versioning exists; Durable Task supports replay. | It inherits Durable Task long-running execution and replay; the current graph runner does not expose an equivalent graph-level history chain, reset, topology migration, or worker-code-version routing. | DAG versioning uses DAG bundles, serialized DAG, and `DagRun.verify_integrity` to reconcile task topology; there is no Continue-As-New equivalent. | Graph schema versioning exists; checkpoint migration is experimental; time travel can fork; there is no explicit history chain or Continue-As-New. | Temporal and Azure Durable have explicit history governance; MAF inherits the lower layer; Airflow is DAG versioning; LangGraph is experimental migration. |
| Process-audit source-of-truth stream | Event History is the recovery and audit fact log for the Workflow Execution. | Event-sourcing history is the recovery and audit fact log for the orchestration instance. | Custom status is a live projection; after completion, results must be retrieved from result events; the Durable Task dashboard is a runtime observation surface. | TaskInstance state, logs, and XCom are task-level facts; DagRun is a scheduling interval; the metadata DB is scheduler state, not the business audit stream. | Checkpoint is an execution-state snapshot; LangSmith trace is an observation surface; there is no first-class business-process audit fact model. | Temporal and Azure Durable have an audit fact stream; MAF requires composition; Airflow is task-level; LangGraph is an execution snapshot. |
| Agent/HITL as business substance | Agent session, memory, and LLM/tool schema must be modeled by the business layer or an external agent platform. | Agent session, memory, and LLM/tool schema must be modeled by the business layer or an external agent platform. | AIAgent, DurableAIAgent, AgentEntity, RequestPort, and graph executor are first-class authoring surfaces. | There is no first-class agent/HITL surface; it needs custom operators, XCom, or an external agent service. | Agent, LLM tool, and Human-in-the-loop nodes are first-class authoring surfaces; agent state and graph state are integrated. | If buildout is an agent/HITL collaboration process, MAF and LangGraph are locally more natural; otherwise Temporal and Azure Durable integrate agents externally. |
| Time/timer semantics | Timer is a durable wait inside the workflow; sleep/await timer can cross maintenance windows; timeout is expressed through timer + select. | Durable timer is a durable wait inside the orchestration; `CreateTimer` + `Task.WhenAny` expresses timeout. | It inherits Durable Task timers; the graph runner uses Activity timers or lower-layer orchestration timers. | TimeSensor and TimeDeltaSensor wait for time conditions; `task execution_timeout`; `schedule_interval` drives DagRun. | Sleep node and timeout configuration exist, but checkpoint point-in-time recovery is not equivalent to durable waiting across windows. | Temporal and Azure Durable have durable timers; MAF inherits the lower layer; Airflow is scheduling/sensor-level; LangGraph is configuration-level. |
| Concurrency/batching | Business code models concurrency; `Task.WhenAll` waits for multiple Activities/Child Workflows; there is no runtime-level fan-out primitive. | Business code models concurrency; `Task.WhenAll` waits for multiple activities/sub-orchestrations; there is no runtime-level fan-out primitive. | Graph fan-out/fan-in edges are a first-class authoring surface; the durable runner preserves fan-in, fan-out, and selector behavior. | Dynamic Task Mapping provides runtime fan-out; mapped task instances execute concurrently; fan-in uses trigger rules. | Graph parallel edges exist, but superstep/checkpoint is an execution model, not a first-class object for resource batch operations. | Temporal and Azure Durable use business code; MAF has graph fan-out/fan-in; Airflow has runtime task mapping; LangGraph is graph concurrent edges. |

### Modeling fit conclusion

**Under the bare-metal primary process manager model of "long-running resource
state machine + external events + localized catch-up":**

- **Temporal** has the highest modeling fit with the scenario:
  Workflow Execution, Child Workflow, Signal/Update, Event History,
  and Continue-As-New map directly to process identity, partitioning,
  event ingress, audit, and history management.

- **Azure Durable Functions (direct)** is close to Temporal in durable
  orchestration primitives: orchestration instance, sub-orchestration, activity,
  external event, and event sourcing cover the same modeling dimensions, but it
  differs from Temporal on activity-level resource-pool routing.
  Temporal can route different activities to different Task Queues inside the
  workflow; DTS / Azure Functions mainly rely on Function App deployment
  topology and WorkItemFilters to passively isolate function names.
  Azure should therefore be demoted to a secondary conditional POC in this
  scenario.

- **MAF Durable Extension** has more modeling distortion
  when the workflow history itself must hold the physical resource state:
  it must pass through graph node, executor,
  and Durable Task primitives across multiple layers.
  Its advantage is agent/HITL authoring.
  If the external operational data warehouse carries the observed-state
  baseline, MAF's state-placement distortion shrinks; however, the graph/hybrid
  path still has to stably reference resource identity, personally own the
  desired/coordination-side process-control path, and explicitly implement
  observe/compare/command/wait reconcile loop before it can enter the primary
  process manager baseline.

- **Airflow** has DAG/DagRun/TaskInstance as its modeling anchors
  and is a poor fit for long-running resource processes:
  DagRun is a scheduling interval and TaskInstance is task execution,
  so resource identity must live outside the framework.
  It is suitable for perimeter DAG scheduling, approval, or reporting,
  but not as the primary process manager.

- **LangGraph** has graph/thread/checkpoint as its modeling anchors
  and is a poor fit for the resource-process control path:
  thread is conversation/execution and checkpoint is a point-in-time snapshot,
  so resource identity must live outside the framework.
  It is suitable as an agent/HITL adapter,
  but not as the primary process manager.

These conclusions do not negate the common prerequisites:
every candidate still needs an external inventory/resource graph,
business event contracts, idempotency keys, read-back verification,
compensation strategy, and a business dashboard.
The difference is which candidate's first-class objects more naturally carry the
primary process-manager responsibilities: long-running process identity,
business event interpretation, localized catch-up, compensation decisions,
side-effect boundary, and audit truth line.

### Boundaries for Temporal with agents and plan revisions

Temporal can integrate agents, but the agent is application load,
not a non-deterministic interpreter inside the Workflow replay path.
LLM calls, tool calls, external diagnosis,
and vendor-system access should live in Activities, Child Workflows,
or an external agent service; the Workflow should store only the process state,
plan version, event, and side-effect boundary accepted from the agent output.

If an agent needs to "rewrite the graph", distinguish two graphs first:

| Meaning of the graph | Correct boundary |
| --- | --- |
| Workflow Definition / code graph | Cannot be rewritten in place by an agent at runtime; it needs code deployment, workflow patching/versioning, Worker Versioning, and replay-safe branching. |
| Business plan / resource graph | Can be produced by an agent as `PlanPatch`, but it should be treated as untrusted business input and enter the running Workflow through an external command API plus Workflow Update/Signal. |

The recommended shape is: the agent emits a `PlanPatch` with `basePlanVersion`,
resource scope, operation diff, risk level, idempotency key, and preconditions;
the external command API first performs auth, schema, RBAC, size limits,
and basic security checks;
use Temporal Update when synchronous validation
and a returned result are needed, Signal for async notifications,
and Query for read-only reads.
The Workflow then decides
whether the patch is acceptable based on the current deterministic state,
and when needed it uses Activities to read external inventory, policy engines,
or real-device state to complete the physical reconcile and policy validation.

Continue-As-New is not an "edit graph" API that an agent can call directly,
nor is it physical rollback or arbitrary plan-migration magic.
The agent or client may request entry into a controlled rollover boundary
through Update/Signal at most; once the Workflow main logic confirms the handler
is complete, dangerous side effects have no unresolved replay risk, and compact
state is ready, it uses Continue-As-New to hand the plan version, processed
update IDs, child workflow IDs, pending approvals, and required process state to
a new Run and new Event History under the same Workflow ID.

### Temporal's value as a reference architecture and its limits

Temporal's advantage is that Workflow Execution is a long-lived,
durable process object; Event History supports replay recovery of control state;
Signals/Updates can inject external messages into the running Workflow
Execution; Timer can express a durable wait inside execution; Activity is the
boundary for external I/O and real-world side effects; and Child Workflow can
split a long-running process into resource-entity-related subexecutions for
host, node, rack, fabric, or validation-domain partitions.

At the durable orchestration runtime layer,
this matches the bare-metal buildout primary process-management problem quite
directly, which makes Temporal a suitable minimal reference architecture:

- A cluster buildout can be one addressable long-running Workflow Execution.
- Per-node, per-rack, or per-fabric handling can use Child Workflow to isolate
  history, waiting, retries, and localized failure.
- BMC/Redfish, MAAS/Ironic/Tinkerbell, Foreman/Cobbler/xCAT, Slurm,
  notifications, and AI agent calls should sit at the Activity
  or external-event boundary.
- Human confirmation, vendor replies, on-site actions,
  and plan-change requests can enter the running process object through
  Signals/Updates.
- Outside the domain fact layer above, Temporal holds process-level state,
  the control path, event ingress, and the auditable execution history.

The downplayed points matter just as much:
Signals/Updates are not a full command gateway
and still require an external entry point for auth, schema, dedup, audit,
and synchronous return semantics; Temporal Reset is not physical rollback;
Continue-As-New is a Run-boundary state handoff
and Event History truncation point, not arbitrary plan-migration magic;
Worker Versioning is a worker/deployment routing
and replay-safe upgrade mechanism,
not automatic migration of already-executed physical side effects;
Activity retry is not exactly-once.
Every real device operation still needs idempotency keys, state read-back,
external locks, compensation flows, and human confirmation.
Temporal still needs, just like Azure and MAF,
a POC that proves worker placement, Event History growth, in-flight versioning,
dashboard projection, and target operating cost.

### Candidate positioning for Azure Durable Functions / Durable Task

Azure Durable Functions / Durable Task should be treated
as a strong durable-orchestration candidate near Temporal,
not as something to be excluded on the standard used for Airflow
or a normal agent graph.
Under the same external inventory/resource graph, business event schema,
idempotency key, read-back verification, lock, and compensation discipline,
its similarity to Temporal is substantial:
an orchestration instance can carry the long-running process identity;
sub-orchestration can be a resource-process-partition candidate;
activity is the boundary for real I/O and physical side effects;
durable timer can express waiting across maintenance windows;
external event can inject human approval, vendor callbacks,
or on-site action results into the running instance;
entity can carry fine-grained serialized coordination state;
execution history / checkpoint / replay support failure recovery of the process.

So the Azure Durable Functions / Durable Task question is not "it also needs an
external resource fact layer", "activity also needs idempotency", or "the
orchestrator also has deterministic replay constraints".
Those also apply to Temporal and belong in the shared POC checklist;
they are not Azure-specific weaknesses.
The real comparison is: once the shared prerequisites are satisfied,
how do Azure's native semantics reduce
or increase the primary process manager burden?

The first difference is product and hosting boundaries.
Durable Task can be used through Azure Durable Functions
or via standalone Durable Task SDKs that are self-hosted.
They share durable execution fundamentals, but the trigger, scaling,
storage provider, monitoring, management APIs,
and runtime surface are different.
If buildout workers must remain
for a long time on a private out-of-band management network to reach BMC, PXE,
MAAS/Ironic, or switch control planes,
you cannot rely on an Azure Functions HTTP starter, timer demo,
or a successful cloud-side plan to prove the target solution works.
You must first make clear
whether the final runtime surface is Azure Functions plan
or a standalone Durable Task worker on AKS, VMs, or on-premises.
Temporal also needs proof of worker placement, backend, capacity, and rollout;
but its candidate definition is directly centered on the Temporal server/backend

- worker pair, while the Azure solution must distinguish "Durable Functions
product surface" from "standalone Durable Task runtime surface" earlier.

The second difference is the interaction model.
Durable external events can send external async signals into an orchestration.
For example, after the vendor finishes recabling,
raise an event to `BuildoutCluster-2026w25`
so the waiting `ValidateFabric` stage can continue.
Temporal Signals/Updates are also designed for a running Workflow;
Updates are better when the change request needs validation
and a synchronous return value.
So when an operator submits "add 12 nodes to rack-7"
or "approve skipping a burn-in rerun for one machine",
the Azure solution must make clear which layer handles command auth,
schema validation, audit, synchronous return, and event delivery.
Azure can do it, but the command service, external event,
and orchestration-state boundaries must be clearly drawn.

The third difference is the boundary of observation and operational evidence.
Durable Task storage provider stores runtime state, history, entity state,
and internal messages; Temporal Event History is also not a business resource
graph.
Neither should replace the fact layer
for node/rack/BMC/firmware/OS/network/validation.
What really needs POC comparison is
whether the target runtime surface can stably expose the process observation
points required by buildout, such as a rack waiting for human approval, a batch
of nodes waiting for BMC reboot, an activity that needs retry after an on-site
fix, or an orchestration/entity that recovers after worker failure.
If these observations, alerts,
and dashboard projections are mostly filled in by an external system,
then that external system is taking over part of the process manager
responsibility.

The fourth difference is versioning, replay, and side-effect discipline.
Durable orchestrator replay, storage-provider recovery, worker failover,
and external-event waiting recover the durable runtime's process-execution
state, not the physical device state.
The Azure solution, like Temporal, must prove activity idempotency,
external-fact reconcile, code/version compatibility for in-flight instances,
and protection for dangerous side effects.
One point to downplay is
that the projected evidence now shows orchestration versioning in the Durable
Task ecosystem; an orchestration instance is permanently associated with a
version at creation time, and workers/clients can use version matching or
conditional branching so old and new instances can coexist.
Therefore, Azure version evolution should no longer be treated
as an unknown weakness.
The difference is that these proofs must land on the chosen Azure Functions
plan, standalone Durable Task worker, storage provider, and
deployment/monitoring boundary.

The fifth difference is backend and worker placement.
Durable Task SDKs can run workers on Azure Container Apps, Kubernetes, VMs,
and other compute.
Durable Task Scheduler is the managed backend for the SDKs
and can support private connectivity through private endpoints.
This makes Azure/Durable Task competitive in Azure-connected
or private-link-acceptable environments; however,
if the target is a fully offline, fully self-hosted bare-metal control plane,
the Scheduler dependency becomes a constraint that must be validated separately.

The conclusion is: Azure Durable Functions / Durable Task can compete
for the "durable orchestration process manager" position,
especially when the organization already accepts the Azure Functions
or Durable Task runtime surface and can clearly separate external events,
activities, entities, and the external resource fact layer.
But if the solution depends on another domain service to hold the process-level
control path, event interpretation, localized catch-up, and compensation
decisions, that service is the primary process manager as defined in this page,
and Azure Durable Functions / Durable Task is only the durable execution
runtime.

### Candidate positioning for Microsoft Agent Framework Durable Workflow Extension

Microsoft Agent Framework Durable Workflow Extension is closer to a durable
process manager than a normal agent graph because it does not depend only on
in-process graph checkpoints; instead, it wires graph-based Agent Framework
workflows into Durable Task-backed execution.
The current evidence shows
that `ConfigureDurableWorkflows` configures durable graph workflows
and registers orchestrations, activities, and agent entities;
the dispatcher maps ordinary executors to Durable Task activities,
maps subworkflows to sub-orchestrations,
maps the agent executor to a Durable Entity,
and maps request port to external-event waiting.
The Durable Extension docs also support both Azure Functions
and self-hosted worker hosting models,
and describe checkpoint/recover across multiple stateless worker
processes/hosts.
But self-hosted worker still connects to the Durable Task Scheduler backend;
it is not equivalent to shipping a production-grade durable backend by itself.

Therefore, MAF Durable Workflow Extension does not belong in the scheduler layer
or normal agent-graph candidate bucket
that has not been connected to durable orchestration.
It inherits Durable Task's long-running execution,
activity side-effect boundary, external event, entity, sub-orchestration,
and recovery capabilities.
Under the same external inventory/resource graph, business event schema,
idempotency, side-effect isolation, and replay discipline,
it can indeed enter the POC set adjacent to Temporal.
Its key difference from Temporal is not the Durable Task backend itself,
but the graph/executor/superstep/agent entity abstraction layer added by Agent
Framework on top of Durable Task.

The first risk is workflow-surface to resource-process-identity mapping.
Microsoft Agent Framework has multiple workflow surfaces.
The evidence projected by the Durable Extension docs and source is the path
where graph-based workflows are checkpointed/recovered by Durable Task
infrastructure; standard checkpoint storage, the functional workflow surface, or
the core workflow surface without Durable Extension cannot be treated as the
same capability.
For example, a Python functional workflow
that only uses ordinary checkpoint storage cannot be written
as a Durable Task-backed graph workflow just
because it shares some surface names.

For resource modeling, Temporal's modeling surface can be organized around a
cluster Workflow, node/rack/fabric Child Workflows, Activities, and
Signals/Updates.
MAF Durable Extension, in contrast,
must explain which graph workflow instance corresponds to a long-running
buildout process; how executors such as `DiscoverNodes`, `ProvisionNode`, and
`OperatorApproval` map to durable activities, sub-orchestrations, agent
entities, or request ports; and how the long-running identity of a
node/rack/fabric is associated with graph nodes, executor bindings, Durable Task
instances/entities, and the external resource graph.
For example, after `ProvisionNode(node-42)` fails as an executor activity,
the BMC credentials are repaired on site, and an event is resubmitted,
the architecture must explicitly model
which request port should receive the event,
which graph workflow should be awakened,
and how only `node-42` is caught up without accidentally touching other nodes.

The second risk is migration and checkpoint compatibility.
MAF checkpoints can capture executor state, pending messages,
pending requests/responses, and shared states;
the workflow-state docs also state that a built workflow has no public API
for modification.
Temporal also has deterministic replay, Continue-As-New, Reset,
and Worker Versioning discipline and cannot be written as arbitrary migration
or physical rollback.
The difference is that Temporal's migration discussion is centered on Workflow
Execution, Event History, Run boundaries, and worker routing, while MAF must
also layer graph definitions, executor splitting, edge/superstep structure,
agent entity, and checkpoint-shape compatibility.
For example, after splitting the original `ProvisionNode` executor into
`FlashFirmware`, `InstallOS`, and `JoinScheduler`, how a buildout instance
already checkpointed in the old superstep resumes, continues, skips forward, or
requeues cannot be summarized as "it has checkpoint".

The third risk is observation and operations layering.
The Durable Task backend can dispatch orchestrator, activity,
and entity work items and manage durable state;
but an MAF solution still has to prove
that Agent Framework layer graph execution, executor dispatch, agent entity,
request port, and checkpoint/recover state can be observed
and diagnosed consistently.
For bare-metal buildout,
the POC cannot stop at "the multi-agent HITL demo runs";
it must prove that worker crash, activity retry, external-event wait,
agent approval, subworkflow failure,
and recovered graph position can all be located
and projected into the business dashboard.
Temporal also needs observability and operations POC;
the extra MAF question is
whether the middle abstraction layer introduces unacceptable mapping
and diagnosis cost.

The strong point of MAF Durable Workflow Extension is agent, multi-agent,
workflow graph, and HITL integration.
If the primary process naturally contains AI diagnosis, agent collaboration,
human approval, and recoverable graph execution,
placing these capabilities in the same framework may reduce integration burden
relative to Temporal + a separate agent platform; inside the Azure / Durable
Task route it may also fit Agent Framework control needs better than pure direct
Durable Functions.
But that only becomes primary-baseline value
if the MAF graph / hybrid path itself carries the process-level control path
and writes agent/HITL interaction back into long-running resource identity,
event interpretation, localized catch-up, compensation decisions,
and coordination audit.
If AI/HITL is only auxiliary capability called by the primary process manager,
the Durable Task-backed graph layer of MAF is better treated
as an upper-layer agent/control surface,
not as a replacement for a smaller durable process substrate.
If the external operational data warehouse is merely the observed-state
baseline, MAF / Temporal can still be the coordinator; if the
desired/coordination-side long-running process-control path, domain event
interpretation, localized failure catch-up, compensation decisions, and
coordination-audit interpretation are still owned by another domain service,
then that service is the primary process manager and MAF Durable Workflow
Extension is only a stronger agent/HITL/durable workflow adapter.

### Airflow's runtime modeling anchor and its adaptation distortion

Airflow cannot be dismissed simply as "it cannot wait for people,
cannot wait for events, or cannot expand dynamically".
It has a clear DAG/TaskInstance scheduling model, Dynamic Task Mapping,
deferrable operators, event-driven scheduling, HITL operators,
TaskInstance states, and an Airflow UI.
These capabilities must be considered to avoid misclassifying Airflow
as "completely unable to wait or respond to events"; however,
they still do not make Airflow the long-running process manager
for bare-metal buildout.

The key limitation of Airflow is not "it cannot run long-wait tasks"
but rather its main state objects and recovery semantics.
Airflow more naturally persists DagRun, TaskInstance, mapped task, retry,
deferred, and removed scheduler/task-execution state.
These states can express "where this finite task graph has run to" very well,
but they should not directly replace "which local failures, repairs, catch-ups,
and acceptance facts this physical cluster resource graph has experienced over
weeks".

So, if a solution claims "use Airflow as the process manager",
it cannot answer only with an external inventory/resource graph.
The external resource graph holding domain facts, locks,
and audit is common discipline for all candidates
and does not disprove Airflow by itself.
What really needs to be checked is where the process-level control path lives:
how long-running resource identity maps to DagRun/TaskInstance
or an external object, how external events enter the running process,
how localized failures propagate and catch up,
how physical side-effect compensation decisions are formed,
and who maintains the process audit source of truth.

If those control responsibilities are actually held by another domain process
service or event system, then that service is the process manager under this
page's scope, and Airflow is only a finite DagRun scheduler/executor.
If Airflow itself is to carry the primary process manager,
then its first-class mechanisms need to be explained honestly:
the scheduler creates DagRuns from the timetable,
advances schedulable TaskInstances, and hands them to the executor;
event-driven scheduling more naturally triggers DagRuns than injects events into
arbitrary running resource-process objects; a deferrable operator solves task
waiting and worker-slot occupation, but local state is not automatically
persisted after deferral; Dynamic Task Mapping is the scheduler creating mapped
task instances from upstream data; DAG file processing, serialization, DAG
bundle versioning, and `DagRun.verify_integrity` provide deployment/scheduling
views and controlled reconciliation of existing DagRuns, not arbitrary topology
evolution of a running resource state machine.
This distinction is the boundary the page must preserve to keep the scope
honest.

If Airflow is still claimed to be the primary process manager,
the difference is not whether it has any single capability.
It is whether the combination of those capabilities naturally carries the
long-running resource process.
The three points below are not Airflow-exclusive defects;
they explain how Airflow's first-class objects map these gates onto
DAG/DagRun/TaskInstance and schedule/data interval:

1. **Resource identity more easily lands on a finite mapped task rather than a
   long-running resource-process object.**
   For example, if `discover_nodes` returns 10 hosts,
   the Airflow scheduler can create 10 mapped TaskInstances
   for `provision(host)`.
   This expresses "the current batch of hosts is fanned out for execution".
   But if a rack is added two days later, a machine is replaced,
   or a switch-port repair requires catching up only the affected nodes,
   Dynamic Task Mapping itself does not maintain the identity
   and evolution of "host/rack/fabric as a long-running process object".
   Temporal also does not magically understand topology;
   but Child Workflow can use host/node/rack and similar resource identities
   as Workflow IDs or partition boundaries, and Signals/Updates can send repair,
   addition, and approval events into the running process object.
   So under the same modeling burden,
   Temporal's resource-process partition semantics fit this problem more
   closely.
   Azure Durable Task's orchestration instance/sub-orchestration/entity also
   belongs to the same POC tier; MAF Durable Extension must prove that graph
   workflow instance, executor, and Durable Task instance/entity mappings can
   reach the same stability.
2. **Events and waits more naturally enter TaskInstance or a new DagRun rather
   than a running resource-process mailbox.**
   Airflow HITL can pause a DAG for human input;
   a deferrable operator can release the worker slot while waiting
   for a trigger; event-driven scheduling can trigger a DagRun from an event
   matching `BaseEventTrigger`.
   These are valuable, but they more naturally land on task waiting,
   DAG branching, or a new DagRun entry point.
   Event schema, authorization, dedup, ordering/concurrency,
   and audit are common gates for all candidates;
   Airflow's specific proof point is how those events eventually bind to an
   addressable long-running resource process, rather than only triggering a new
   DagRun or resuming a task.
   Resource-dependency propagation, localized failure catch-up,
   and physical side-effect compensation still need to be explicitly implemented
   by the business control path.
   Temporal does not automatically solve those business issues either;
   but Signals/Updates/Timers enter the long-running Workflow Execution
   directly, Activities explicitly isolate real-world side effects, and the same
   business logic is easier to model as "what state is this cluster/node/rack
   process in now, what event did it receive, and how should it catch up next".
3. **DAG version, backfill/catchup, and removed task put the migration burden
   onto schedule-graph reprocessing semantics.**
   Airflow's DAG file processing, serialized DAGs, DAG bundle versioning,
   `DagRun.verify_integrity`, backfill,
   and catchup handle the DAG version the scheduler sees,
   TaskInstance reconciliation,
   and the creation/reprocessing of DagRuns for historical logical dates.
   As soon as replay, reset, fork, rerun, retry,
   or recovery crosses a real side-effect boundary,
   all candidates must first reconcile external inventory with the real device
   state.
   Airflow's relative issue is that backfill/catchup/rerun
   and removed-task reconciliation are natively centered on logical date,
   DagRun, and TaskInstance,
   which makes bare-metal buildout "process migration" more likely to look like
   "schedule-graph reprocessing".
   Temporal has strict migration discipline as well: deterministic replay,
   Continue-As-New, Reset, and Worker Versioning all have limits,
   and Reset is not physical rollback.
   The difference is that Temporal's discipline is centered on Workflow
   Execution/Event History/Run boundaries, which is closer to "how a
   long-running process object evolves and recovers"; Airflow's discipline is
   centered on DAG code, DagRun, TaskInstance, and schedule/data interval, which
   more easily compresses the real resource process into a schedule-graph
   reprocessing problem.

### LangGraph's position and the primary-process-manager proof point

LangGraph also should not be underestimated as "unable to run long,
unable to persist, unable to do HITL".
It is designed for long-running stateful agents/workflows;
it uses checkpointers to save thread-scoped graph state,
stores to provide cross-thread long-term memory,
`interrupt()` / resume to support human-in-the-loop,
fault tolerance with graph/node-level retries, timeouts and error handlers,
and an Agent Server with a persistence database, task queue, and queue worker.
Graph migrations and time travel support constrained checkpoint replay, fork,
and recovery of an existing thread under a new graph definition.

Fair comparison means not writing every business discipline
that all runtimes must follow as a LangGraph-specific defect.
Temporal also does not automatically understand bare-metal resource processes:
it does not know the domain meaning of `node-42`, rack, fabric, BMC,
or Slurm validation; Temporal Event History is not an external
inventory/resource graph, and it is not a resource-fact database.
All candidates still need the business layer to define resource identity,
event schema, locks, audit, idempotency keys, real-state reconcile,
and the side-effect boundary.

The real difference is the runtime's modeling center of gravity and
whether its first-class semantics are stable enough to carry the primary
process-control path defined in this page.
Temporal centers on durable Workflow Execution, Child Workflow, Activity, Timer,
the Signal/Update mailbox, and Event History.
It still needs business mapping,
but these objects can serve as architecture anchors:
a cluster Workflow represents the overall buildout process;
node/rack/fabric Child Workflows represent resource-process partitions
that are independently addressable, can fail locally,
and can catch up independently; Signals/Updates deliver approvals, repairs,
vendor acknowledgments, and lower-layer system events into the running process
object; Activities isolate real-world side effects.

LangGraph centers on agent graph, thread, run, checkpoint, store,
interrupt/resume, and graph node execution.
That is a very good fit for AI diagnosis, operator copilot,
stateful agent automation, and HITL decision support;
but if it is promoted to the primary process manager for bare-metal buildout,
the solution must additionally prove
that these graph/thread/run semantics can reliably, stably,
and in an auditable manner carry a resource-partitioned, externally addressable,
long-running process manager,
not just a recoverable agent-graph execution context.

Under the current evidence,
the LangGraph proof points that matter most
for primary process-manager status are the resource-process contract,
not whether all runtimes have checkpoints, forks, or worker-queue boundaries:

1. **Resource-process identity must be mapped out of thread/run/graph.**
   This does not mean LangGraph cannot map a resource process.
   The business layer can absolutely define `thread_id = buildout-123`,
   or create threads/subgraphs/external process objects
   and event routing per node/rack.
   But that mapping must be proven stable by the solution itself.
   For example, if `node-42` fails after firmware flashing
   and is repaired by hand two days later, the solution must explain:
   where the long-running process identity for `node-42` lives;
   how the repair event reaches the right running process;
   whether the other 39 machines are isolated;
   and whether the catch-up condition is decided by graph state,
   the external resource graph, or another domain process service.
   Temporal also needs business-defined semantics here, but Child Workflow ID,
   Workflow Execution, and Signals/Updates can serve directly
   as durable identity and message-ingress anchors.
   Azure Durable Task and MAF Durable Extension also need business mapping,
   but they at least can anchor around orchestration instance,
   sub-orchestration, entity, activity, and external event.
2. **`interrupt()` / resume is a strong HITL mechanism, but it is not a complete
   business event model.**
   `interrupt()` / resume expresses "pause the graph, wait for operator input,
   then continue" very well.
   For example, after the operator approves "restart `node-42`",
   LangGraph can carry the approval result back into the graph.
   But the primary process manager also needs to handle more external messages:
   BMC power events, provisioning results, vendor recabling acknowledgments,
   rack validation results, scheduler drain completion,
   and manual override revocation.
   These events need schema, auth, dedup, ordering/concurrency handling,
   resource-identity binding, and audit.
   Temporal Signals/Updates do not magically solve business semantics either,
   but they are a first-class message ingress into durable Workflow Execution.
   If LangGraph injects events through resume, webhook, a custom event router,
   or store polling, it must prove
   that these ingress paths do not blur thread/resource identity,
   approval context, and failure-recovery paths.
3. **Fault-tolerance recovery of graph/node execution does not automatically
   make resource-level catch-up part of the process contract.**
   Retries, timeouts, and error handlers are valuable execution recovery
   capabilities; but the bare-metal control plane still needs to know what
   actually happened to the real device.
   For example, if a graph node calls Redfish to reboot `node-42` and times out
   before retrying, that does not tell us
   whether the machine has already rebooted, is stuck in BIOS, is in PXE,
   or needs an on-site power-cord reseat.
   Temporal Activity retry has the same risk;
   the difference is not that Temporal automatically understands physical state,
   but that the Activity boundary, Workflow/Child Workflow state,
   and Signal/Update ingress can be organized around "which long-running process
   object is waiting for which event, which side effect has already been
   emitted, and how should the next step reconcile".
   If a LangGraph solution is to own the primary process-control path,
   it must add equally strong side-effect recording, read-back verification,
   idempotency keys, compensation, and human-confirmation models.

Three other capabilities should be written as evidence boundaries
or common POC gates, not as LangGraph-specific defects:

- **checkpoint/store are graph-state/memory persistence capabilities.**
  They are valuable, but they do not by themselves prove
  that resource-process audit, external inventory,
  or localized catch-up is already in place.
  This is the same kind of common boundary as Temporal Event History,
  Durable Task backend state,
  or the Airflow metadata DB not being the resource-fact database.
- **time travel/fork are diagnosis and controlled-branching capabilities.**
  They are not unusable in the primary control path;
  but once fork/replay crosses a real side-effect boundary,
  they must reconcile external inventory with the real device state
  and protect downstream side-effect nodes from unconditional replay,
  just like Temporal Reset, Durable orchestration recovery,
  or Airflow rerun/backfill.
  This is a common side-effect guard, not a LangGraph weakness.
- **Agent Server queue worker proves the graph-run execution queue.**
  It shows that a LangGraph run can be queued, workerized,
  and executed persistently;
  but it does not by itself prove
  that node/rack/fabric resource-process scheduling,
  localized failure isolation,
  and long-running business audit are already in place.
  If the business layer maps each resource process to a thread/run
  and implements event routing, locks, catch-up, and audit,
  the queue worker can be part of the execution foundation; it is not,
  by itself, sufficient evidence of primary-process-manager fit.

Therefore, if a solution claims "LangGraph as the primary process manager",
it cannot stop at "LangGraph has persistence, HITL, fault tolerance,
and Agent Server queue".
It must answer directly: where the long-running resource identity lives;
how external events are delivered to the correct process object;
how localized failures are isolated and caught up;
how operator approval enters the audit chain;
and how real-world side effects are isolated, deduped, compensated,
and protected.

If the external inventory/resource graph only stores domain facts, locks,
and audit projections, while LangGraph graph/thread explicitly owns the
process-control path, event interpretation, recovery strategy, and side-effect
boundary, then LangGraph should not be disqualified merely because an external
resource graph exists.
But under the current evidence,
LangGraph is still more safely positioned as AI diagnosis, operator copilot,
HITL decision support, or an agent automation adapter invoked by the primary
process manager.
If a POC proves that "business layer + LangGraph" can stably carry the primary
process-control path and achieve equivalent requirements for resource
partitioning, event routing, localized catch-up, audit, and side-effect
protection, then the decision should be reevaluated using that new evidence.

## Consequences

No matter whether the team chooses Temporal,
Azure Durable Functions / Durable Task,
Microsoft Agent Framework Durable Workflow Extension, Airflow, or LangGraph,
it still needs an external inventory/resource graph, a business event model,
side-effect discipline, dashboard projection, and migration/version discipline.
These are common engineering prerequisites for bare-metal buildout,
not defects unique to any single candidate.

Even if Temporal is adopted as the reference architecture
or primary process manager,
that does not mean only the Temporal runtime is being deployed.
On top of the domain fact layer
and bare-metal control-plane baseline described above,
the solution should also commit to the following supporting capabilities:

1. **Resource-entity partitioning strategy**:
   make it explicit which objects are represented by Child Workflow and
   which are only referenced as external state.
2. **Side-effect discipline**: every Redfish/IPMI, provisioning, OS, Slurm,
   notification, and AI agent call must have idempotency keys,
   read-back verification, retry boundaries, and compensation strategy.
3. **In-flight change discipline**: Continue-As-New, Reset, Worker Versioning,
   and blueprint schema migration must be handled at Run boundaries,
   with external-fact reconcile and human approval.
4. **Business dashboard projection**:
   do not treat the Temporal UI as the operator product UI;
   project business state from Temporal, the inventory/resource graph,
   and lower-level control planes.

If the organization still requires Airflow in the solution and has not
yet proven that Airflow DagRun/TaskInstance together with the business layer can
carry the primary process-control path, the architecture document should label
it as a scheduler/executor/UI adapter invoked by the primary process manager,
not as the answer to this selection problem.
If a POC proves that the Airflow solution can carry those primary process
responsibilities, then the decision should be revisited using the new evidence.

If the organization requires LangGraph in the solution and has not yet proven
that LangGraph graph/thread together with the business layer can carry the
primary process-control path, it should first be labeled an agent/HITL adapter,
and the document should explicitly state which events and decisions are written
back to the primary process manager and the external inventory/resource graph.
If a POC proves that the LangGraph solution can carry those primary process
responsibilities, then the decision should be revisited using the new evidence.

If the organization requires Azure Durable Functions / Durable Task,
it should be treated as a same-tier strong candidate for durable orchestration,
not as a perimeter adapter.
But the solution must explicitly state
whether the final runtime surface is Azure Functions plan
or the standalone Durable Task SDK,
and it must explain the responsibility boundaries
for Durable Task Scheduler / storage provider, network/private endpoint,
language SDK, external event / management API interaction model,
orchestration versioning, business dashboard,
and external inventory/resource graph.

If the organization requires Microsoft Agent Framework Durable Workflow
Extension, first confirm whether it is carrying the primary process-control path
or only an agent/HITL support layer.
If it is carrying the path,
treat it as a Durable Task-backed graph workflow
or hybrid POC candidate in the Azure / Durable Task route,
and explicitly state whether the Durable Extension covers the target workflow
surface, chosen hosting/backend,
executor/activity/entity/sub-orchestration/external-event mapping,
direct-durable-primitives access path, checkpoint compatibility, agent/HITL
boundary, and whether the Agent Framework middle layer adds unacceptable mapping
and diagnosis cost.
If the external operational data warehouse is the observed-state baseline,
and the graph/hybrid path can stably reference resource identity
and personally own the desired/coordination-side process-control path,
explicit reconcile loop, event interpretation, localized catch-up,
compensation decisions, side-effect boundary, and coordination audit,
it can be a primary baseline; if AI diagnosis, multi-agent,
and HITL are only auxiliary capabilities,
it should be labeled an upper-layer agent/HITL/control adapter rather than the
primary process manager.

## Revisit triggers

Reevaluate this decision when any of the following occurs:

- The decision scope narrows from "primary process manager" to "finite-batch
  scheduling/execution/UI adapter".
- The organization explicitly accepts
  that another external domain process service is the real process manager,
  and Airflow only acts as the invoked scheduler/executor.
- The organization explicitly accepts
  that another external domain process service
  or durable orchestrator is the real process manager,
  and LangGraph only acts as the invoked agent/HITL adapter.
- The Azure/Durable Task evidence matrix or POC shows
  that orchestration instance/sub-orchestration, entities, external events,
  orchestration versioning, Durable Task Scheduler/backend,
  and private connectivity fit the target organization better than the Temporal
  reference architecture.
- The organization has standardized on Microsoft Agent Framework Durable
  Extension / Durable Task and the target workflow surface clearly runs on a
  Durable Extension-backed graph workflow, with graph/executor/checkpoint
  compatibility and agent/HITL integration constraints not weakening the
  process-manager goal.
  If the external operational data warehouse is the observed-state baseline,
  and the graph workflow can stably reference external resource identity
  and personally carry the desired/coordination-side process-control path,
  explicit reconcile loop, event interpretation, localized catch-up,
  compensation decisions, side-effect boundary, and coordination audit,
  then this condition should trigger a reevaluation of MAF
  as the primary baseline rather than just an adapter.
- The team has no Temporal operations experience
  and cannot afford the cost of workflow versioning, Activity idempotency,
  and dashboard projection.
- The target buildout scenario is redefined as short-lived, batch validation,
  or reporting processing rather than a long-lived interactive resource state
  machine.
- The POC shows that Temporal modeling, observability,
  or operational cost is higher than the combination of Airflow plus an external
  state machine.
- The POC shows that the Airflow solution can stably carry the long-running
  process-control path under the same external inventory/resource graph and
  side-effect discipline using DagRun/TaskInstance, event scheduling, deferral,
  HITL, backfill/catchup, and DAG version/reconciliation discipline.
- The POC shows that, after the Azure Durable Functions / Durable Task
  hosting/runtime/backend boundaries are made explicit, the durable
  orchestration, external event, entity, versioning, and runtime constraints are
  a better fit for the target organization than Temporal.
- The POC shows that Microsoft Agent Framework Durable Workflow Extension's
  graph workflow, executor dispatch, Durable Task-backed orchestration, external
  event, and checkpoint/recover can stably carry the primary process-control
  path, and that the middle-layer mapping and diagnosis cost is acceptable; if
  the external operational data warehouse provides the observed-state baseline,
  and the graph workflow can stably reference resource identity and personally
  hold the desired/coordination-side process-control path, explicit reconcile
  loop, event interpretation, localized catch-up, compensation decisions,
  side-effect boundary, and coordination audit, it can be compared with
  Temporal/Azure as the same-tier primary baseline.
- The POC shows that LangGraph graph/thread explicitly owns the long-running
  control path, event interpretation, localized catch-up, migration strategy,
  and side-effect boundary, rather than those responsibilities being held by an
  external domain process service.

## POC validation boundary

Before turning this page's judgment into a procurement or engineering baseline,
validate at least the common gates below:

- The external operational data warehouse provides physical observed state,
  observation time, source, version, confidence, and acceptance observations;
  if a command ledger, lock, inbox/outbox,
  or business audit projection is needed,
  they should be explicitly designed
  as adjacent operational control-plane components.
- resource identity / process partition can reliably express long-running
  process objects such as cluster, node, rack, and fabric.
- event schema, auth, dedup, ordering/concurrency, and audit cover human,
  vendor, BMC, provisioning, scheduler, and validation events.
- Every real-world side effect has an idempotency key, read-back verification,
  retry boundary, compensation, and human-confirmation model.
- Whenever replay, reset, fork, rerun, retry,
  or recovery crosses a real side-effect boundary,
  it must first query the external operational data warehouse through an
  observation activity/executor, reconcile against desired state, and protect
  downstream side-effect nodes.
- Local failure isolation, catch-up after repair, migration/version discipline,
  and dashboard projection do not depend on a temporary runtime UI
  interpretation.

The common gates are not a product defect list.
The additional candidate validation must prove how the first-class runtime
object satisfies these gates, and whether satisfying them requires moving the
primary process-control logic outside the runtime:

- Temporal single-node workflow covering BMC read, firmware/BIOS check,
  OS provisioning, driver install, and Slurm validation job.
- Temporal handling of 10-node Child Workflows
  where partially failed nodes do not block the unaffected nodes,
  and repaired nodes can catch up to the integration gate.
- Temporal Reset before/after must first use an observation Activity to read the
  external operational data warehouse and reconcile desired/observed state;
  dangerous Activities cannot be replayed unconditionally.
- The Temporal solution must also validate worker placement,
  Event History growth, in-flight versioning, business dashboard projection,
  and target operating cost;
  do not treat the reference architecture as a proven winner baseline.
- If someone claims Airflow can be the primary process manager,
  the POC must prove that the Airflow solution can explain long-running resource
  identity, external events, local failure propagation, catch-up conditions, and
  physical side-effect compensation; proving only that Dynamic Task Mapping,
  HITL, deferrable operators, or event scheduling run successfully only proves
  that it is suitable as an execution/scheduling layer.
- The Airflow solution must prove that DAG code changes, existing DagRuns,
  removed tasks, and backfill/reprocessing/catchup do not break buildout process
  audit; otherwise it is still not a qualified primary process manager.
- The Azure Durable Functions solution must prove
  that orchestrator deterministic replay, durable timers, external events,
  entities, storage provider, hosting plan,
  and network connectivity can carry the target buildout cycle.
- The Azure Durable Functions solution must clearly state
  whether it uses Durable Functions or standalone Durable Task SDKs
  as its hosting model; if the deployment target is AKS, VMs, or on-premises,
  it must not smuggle standalone SDK capabilities through Azure Functions
  triggers and built-in HTTP management APIs.
- The Azure Durable Functions solution must prove in-flight orchestration
  instance code/version compatibility, storage-provider recovery, and downstream
  Activity side-effect protection, rather than treating deterministic replay as
  a restoration of physical facts.
- The Azure Durable Task solution must validate
  whether fixed/resource-derived instance IDs
  and sub-orchestration will cause hotspots or latency,
  how the one-way async semantics of external events are complemented by
  synchronous command results, whether Durable Task Scheduler/backend/private
  endpoint satisfy the target networking and availability boundary, and whether
  entities are only carrying fine-grained coordination state rather than
  replacing the resource graph.
- The Microsoft Agent Framework Durable Workflow Extension solution must prove
  that the target flow actually runs on a Durable Extension-backed graph
  workflow rather than only using standard checkpoints or a workflow surface
  without Durable Extension enabled.
- The Microsoft Agent Framework Durable Workflow Extension solution must prove
  that the graph workflow can stably reference long-running resource identity,
  carry runtime event ingress, localized failure catch-up,
  physical side-effect boundary, and coordination audit;
  proving only that executor/agent graph, checkpoint,
  or HITL runs successfully only proves that it is suitable
  as an agent/HITL/workflow adapter.
- The Microsoft Agent Framework Durable Workflow Extension solution must test
  the chosen hosting/backend, stateless worker failover, Durable Task
  activity/entity/sub-orchestration dispatch, external-event waiting, checkpoint
  recovery, graph definition/checkpoint compatibility, the combination boundary
  of direct durable primitives / `DurableTaskClient`, and the observability and
  diagnosis cost of the Agent Framework middle layer.
- If MAF is used as the primary baseline,
  the POC must prove that a Durable Extension-backed graph workflow or hybrid,
  while referencing the external observed-state warehouse,
  personally holds the desired/coordination-side process-control path,
  explicit reconcile loop, event interpretation, localized failure catch-up,
  compensation decisions, side-effect boundary, and coordination audit;
  agent entity, request port, tool approval,
  and LLM/tool side-effect isolation
  and audit cannot be just peripheral adapter capabilities.
- If someone claims LangGraph can be the primary process manager,
  the POC must prove that the LangGraph solution can explain long-running
  resource identity, domain events, local failure propagation, catch-up
  conditions, physical side-effect compensation, process audit, and graph/thread
  migration; proving only that persistence/checkpoint, interrupt/resume, time
  travel/fork, fault tolerance, or Agent Server queue worker works only proves
  that these are available mechanisms, not that the solution already carries the
  primary process-control path.

## Evidence and limitations

### Evidence units

| Type | Citation | Notes |
| --- | --- | --- |
| user | On 2026-06-16, the user endorsed the core judgment in `raw/10-ai-generated-drafts/2026-06-13-cluster-buildout-platform-selection-bare-metal-research-report.md` about long-running, interactive, event-driven, resource-entity-oriented buildout process managers, and requested analysis-page extraction. | Establishes the scenario boundary and the direction of the user-endorsed judgment. |
| user | On 2026-06-16, the user corrected the ranking method: “也许顺序其实应该调整，我也不确定，你不能假定就是这样了，我们应该先找证据再决定，不是开枪再画靶”. | Supports the decision not to write Temporal as a confirmed procurement winner and to reintroduce Azure Durable Task and MAF into the same evidence-first candidate comparison. |
| user | On 2026-06-17, the user first narrowed the question: “仅考虑对业务场景建模的扭曲程度……运维成本方面可以摊薄，AI方面属于收益不明确，对接起来也不复杂”; then continued challenging the MAF Graph counterargument and asked what extra value “集成度更高” actually brings. | Establishes the narrower modeling-distortion subquestion for Temporal / MAF and moves AI ergonomic benefit from "not counted for now" to "included only as agent/HITL authoring and adapter-layer benefit". |
| user | On 2026-06-17, the user further noted that bare-metal control planes are not simple shell commands and many nodes may require asynchronous human action; they also asked whether a pure Agent Graph as the primary control plane is actually invalid, and whether Temporal can carry plan revisions through agents, plan patches, and Continue-As-New. | Establishes the further narrowing of the MAF agent-graph exception conditions and the architectural boundary for Temporal with agents. |
| user | On 2026-06-17, the user clarified that Azure Durable Functions orchestrators are handwritten anyway and using MAF does not mean Durable primitives cannot be controlled at the orchestrator layer; the reason to choose MAF is precisely to obtain controllable Agent Framework capability, and they asked for source-based clarification of Direct Durable primitives and MAF. | Triggered the rollback of the over-strong claim that MAF is inherently weaker than direct Azure Durable Functions, and added the boundary between Direct Durable primitives and MAF composition. |
| user | On 2026-06-17, the user first stated that “业务上已经假定事实状态是外部数据仓库”, and then clarified: “Event History 确实是执行的主线，但是具体 cluster buildout 的状态要以外部数据仓库为观察基准”. | Triggers the split between the coordination-command source-of-truth stream and the observed-state source-of-truth stream in this page and refines the MAF baseline condition. |
| session | In this session `caa042f4-ce50-4fa6-93b5-e07f577d64a8`, four GPT-5.5 review agents: `decision-semantics`, `decision-maf-fairness`, `decision-temporal-strength`, and `decision-page-structure`. | Supports the reorganization of the decision section entrance, Temporal strength, MAF conditions, and reader entry path; the review opinions are used only as structure and consistency checks, not as third-party technical facts. |
| session | In this session `caa042f4-ce50-4fa6-93b5-e07f577d64a8`, four GPT-5.5 review agents: `azure-direct-primitives`, `maf-composition`, `maf-superset-skeptic`, and `durable-maf-final`. | Supports the adversarial review of Direct Durable primitives, MAF composition, the strict-superset boundary, and MAF positioning within the Azure / Durable Task route; the technical facts still come from the raw source. |
| raw | [`2026-06-13-cluster-buildout-platform-selection-bare-metal-research-report.md`](../../../raw/10-ai-generated-drafts/2026-06-13-cluster-buildout-platform-selection-bare-metal-research-report.md) | Non-authoritative AI research draft; used only as a clue and the source of this page's question, not as the main technical evidence. |
| wiki | [Workflow Concepts Comparison](../../../wiki/analyses/workflow-concepts-comparison.md) | Provides the common comparison axes for control surface, execution interpreter, state source of truth, recovery model, side-effect boundary, and time/trigger semantics. |
| wiki | [Capability Boundaries Between Temporal and MAF Durable Extension](../../../wiki/analyses/temporal-vs-maf-durable-extension.md) | Direct comparison of Temporal and MAF Durable Extension on Event History, Task Queue, Signal/Update/Query, Continue-As-New/Reset, graph durable adapter, RequestPort, agent entity, and graph semantic fidelity boundaries. |
| wiki | [Process Manager Architecture: Coordination Truth Line and Observed Truth Line](process-manager-external-data-warehouse-architecture.en-US.md) | Dedicated analysis of Temporal and MAF when Event History / Durable history is the coordination command truth line and the external operational data warehouse is the observed-state baseline. |
| wiki | [Temporal Workflows docs](../../../wiki/sources/temporal/workflows-docs.md) | Basic semantics of Temporal Workflow Execution, Event History, and replay. |
| wiki | [Temporal Activities docs](../../../wiki/sources/temporal/activities-docs.md) | Activity as the boundary for external I/O and side effects. |
| wiki | [Temporal Message Passing docs](../../../wiki/sources/temporal/message-passing-docs.md) | Signals, Updates, and Queries interacting with running Workflows. |
| wiki | [Temporal Timers and Start Delays docs](../../../wiki/sources/temporal/timers-delays-docs.md) | Timer semantics as durable waiting inside Workflow Execution. |
| wiki | [Temporal Child Workflows docs](../../../wiki/sources/temporal/child-workflows-docs.md) | Child Workflow partitioning by large workload or single resource. |
| wiki | [Temporal Continue-As-New docs](../../../wiki/sources/temporal/continue-as-new-docs.md) | Run-boundary and Event History truncation semantics of Continue-As-New. |
| wiki | [Temporal Reset docs](../../../wiki/sources/temporal/reset-docs.md) | History-prefix and new-execution semantics of Reset. |
| wiki | [Temporal Worker Versioning docs](../../../wiki/sources/temporal/worker-versioning-docs.md) | Worker-version routing and in-flight execution boundaries. |
| wiki | [Temporal Dynamic AI Agents blog](../../../wiki/sources/temporal/dynamic-ai-agents-blog.md) | Temporal can carry dynamic agent patterns through durable workflows, with model/tool calls still living at the Workflow/Activity boundary. |
| wiki | [Azure Durable Functions Overview docs](../../../wiki/sources/azure-durable-functions/overview-docs.md) | Positioning of Durable Functions as Azure Functions' stateful workflow extension. |
| wiki | [Durable Task Orchestrations docs](../../../wiki/sources/azure-durable-functions/orchestrations-docs.md) | Durable orchestration, instance identity, event sourcing, execution history, and replay semantics. |
| wiki | [Durable Task Code Constraints docs](../../../wiki/sources/azure-durable-functions/code-constraints-docs.md) | Orchestrator deterministic replay and external I/O boundary. |
| wiki | [Durable Task Timers docs](../../../wiki/sources/azure-durable-functions/timers-docs.md) | Durable timers and timeout semantics. |
| wiki | [Durable Task External Events docs](../../../wiki/sources/azure-durable-functions/external-events-docs.md) | External-event semantics and the one-way async limitation. |
| wiki | [Durable Task Entities docs](../../../wiki/sources/azure-durable-functions/entities-docs.md) | Fine-grained serialized coordination state and entity operation semantics. |
| wiki | [Durable Task Storage Providers docs](../../../wiki/sources/azure-durable-functions/storage-providers-docs.md) | Durable Task runtime-state backend and storage-provider boundaries. |
| wiki | [Durable Task Instance Management docs](../../../wiki/sources/azure-durable-functions/instance-management-docs.md) | Orchestration instance-management APIs and instance-ID boundaries. |
| wiki | [Durable Task Orchestration Versioning docs](../../../wiki/sources/azure-durable-functions/orchestration-versioning-docs.md) | Orchestration versioning boundaries for Durable Functions and Durable Task SDKs. |
| wiki | [Durable Task Hosting Model docs](../../../wiki/sources/azure-durable-functions/hosting-model-docs.md) | Hosting-model differences between Durable Functions and standalone Durable Task SDKs. |
| wiki | [Durable Task SDKs Overview docs](../../../wiki/sources/microsoft-durable-task/sdk-overview-docs.md), [Durable Task Scheduler docs](../../../wiki/sources/microsoft-durable-task/scheduler-docs.md) | Compute placement, Scheduler backend, dashboard, private connectivity, and backend boundaries for standalone Durable Task SDKs. |
| wiki | [Azure Functions Scale and Hosting docs](../../../wiki/sources/azure-functions/scale-hosting-docs.md) | Azure Functions hosting plans, scale, resources, networking/container support, and cost boundaries. |
| raw | `raw/git/github.com/Azure/azure-functions-durable-extension/src/WebJobs.Extensions.DurableTask/ContextInterfaces/IDurableOrchestrationContext.cs:87-114,116-169,331-430,432-558`、`raw/git/github.com/Azure/azure-functions-durable-extension/src/WebJobs.Extensions.DurableTask/ContextInterfaces/IDurableOrchestrationClient.cs:117-338` | Direct orchestrator/client primitives in Azure Durable Functions: Continue-As-New, custom status, Durable HTTP, entity call/signal, sub-orchestration, timer, external event, entity lock, activity/retry, start/raise/manage/query/purge/restart. |
| wiki | [Microsoft Agent Framework Durable Extension docs](../../../wiki/sources/microsoft-agent-framework/durable-extension-docs.md) | Durable Task-backed execution, checkpoint/recover, HITL, Azure Functions and self-hosted worker, and Durable Task Scheduler backend boundaries. |
| wiki | [Microsoft Agent Framework Durable Workflow Registration source](../../../wiki/sources/microsoft-agent-framework/durable-workflow-registration-source.md), [Microsoft Agent Framework Durable Executor Dispatcher source](../../../wiki/sources/microsoft-agent-framework/durable-executor-dispatcher-source.md) | Registration and dispatch mapping from durable graph workflows to orchestrations/activities/entities/sub-orchestrations/external events. |
| raw | `raw/git/github.com/microsoft/agent-framework/dotnet/src/Microsoft.Agents.AI.DurableTask/Workflows/DurableWorkflowRunner.cs:72,162-190,294-323,365-399,494-515`、`raw/git/github.com/microsoft/agent-framework/dotnet/src/Microsoft.Agents.AI.DurableTask/Workflows/EdgeRouters/DurableEdgeMap.cs:75-190`、`raw/git/github.com/microsoft/agent-framework/dotnet/src/Microsoft.Agents.AI.DurableTask/Workflows/EdgeRouters/DurableFanOutEdgeRouter.cs:35-67`、`raw/git/github.com/microsoft/agent-framework/dotnet/src/Microsoft.Agents.AI.DurableTask/Workflows/EdgeRouters/DurableDirectEdgeRouter.cs:55-107`、`raw/git/github.com/microsoft/agent-framework/dotnet/src/Microsoft.Agents.AI.DurableTask/Workflows/DurableMessageEnvelope.cs:15-51`、`raw/git/github.com/microsoft/agent-framework/dotnet/src/Microsoft.Agents.AI.DurableTask/Workflows/DurableExecutorDispatcher.cs:51-66,104-125,172-185` | Superstep limit, message-queue / fan-in aggregation, fan-out routing, selector-condition evaluation, activity/entity/sub-orchestration/external-event dispatch, RequestPort custom status / external-event behavior, and the absence of a `TargetId` field in `DurableMessageEnvelope`. |
| raw | `raw/git/github.com/microsoft/agent-framework/dotnet/src/Microsoft.Agents.AI.Workflows/Execution/MessageEnvelope.cs:10-20`、`raw/git/github.com/microsoft/agent-framework/dotnet/src/Microsoft.Agents.AI.Workflows/Execution/DirectEdgeRunner.cs:13-54`、`raw/git/github.com/microsoft/agent-framework/dotnet/src/Microsoft.Agents.AI.Workflows/Execution/FanInEdgeRunner.cs:13-96`、`raw/git/github.com/microsoft/agent-framework/dotnet/src/Microsoft.Agents.AI.Workflows/Execution/FanInEdgeState.cs:10-63`、`raw/git/github.com/microsoft/agent-framework/dotnet/src/Microsoft.Agents.AI.Workflows/Execution/FanOutEdgeRunner.cs` | In-process graph runner `MessageEnvelope.TargetId`, targeted-message filtering in `DirectEdgeRunner` (lines 21-25), `FanInEdgeState.ProcessMessage` waiting for all sources, and `FanOutEdgeRunner` fan-out routing and condition evaluation. |
| raw | `raw/git/github.com/microsoft/agent-framework/dotnet/src/Microsoft.Agents.AI.Workflows/AIAgentBinding.cs:14-38`、`raw/git/github.com/microsoft/agent-framework/dotnet/src/Microsoft.Agents.AI.DurableTask/DurableAIAgent.cs:36-39,89-140,147-168`、`raw/git/github.com/microsoft/agent-framework/dotnet/src/Microsoft.Agents.AI.DurableTask/AgentEntity.cs:32-151,197-214`、`raw/git/github.com/microsoft/agent-framework/dotnet/src/Microsoft.Agents.AI.DurableTask/AgentSessionId.cs:23-58`、`raw/git/github.com/microsoft/agent-framework/dotnet/src/Microsoft.Agents.AI.Hosting.AzureFunctions/BuiltInFunctions.cs:98-112,116-190` | MAF AIAgent binding, durable-agent session/entity conversation history/TTL, RequestPort pending-input projection, and respond/RaiseEvent behavior. |
| raw | `raw/git/github.com/microsoft/agent-framework/dotnet/src/Microsoft.Agents.AI.DurableTask/ServiceCollectionExtensions.cs:32-90,92-145,230-273`、`raw/git/github.com/microsoft/agent-framework/dotnet/src/Microsoft.Agents.AI.DurableTask/Workflows/DurableExecutorDispatcher.cs:51-88,104-125,139-157,172-185`、`raw/git/github.com/microsoft/agent-framework/dotnet/src/Microsoft.Agents.AI.DurableTask/DurableAgentContext.cs:21-49,80-122`、`raw/git/github.com/microsoft/agent-framework/dotnet/src/Microsoft.Agents.AI.DurableTask/Workflows/DurableActivityExecutor.cs:28-56`、`raw/git/github.com/microsoft/agent-framework/dotnet/src/Microsoft.Agents.AI.DurableTask/Workflows/DurableWorkflowContext.cs:19-99` | Additive configuration for MAF Durable Extension, mapping from graph executors to Durable Task primitives, exposure of schedule/status/raise-event operations through the durable agent context, and the `IWorkflowContext` boundary used by ordinary executors. |
| wiki | [Microsoft Agent Framework Workflows overview](../../../wiki/sources/microsoft-agent-framework/workflows-overview-docs.md), [Microsoft Agent Framework WorkflowBuilder docs](../../../wiki/sources/microsoft-agent-framework/workflow-builder-docs.md), [Microsoft Agent Framework Functional Workflows docs](../../../wiki/sources/microsoft-agent-framework/functional-workflows-docs.md) | Agent Framework workflows, graph workflows, executors, edges, superstep execution, and the functional workflow surface. |
| wiki | [Microsoft Agent Framework Workflow Checkpoints docs](../../../wiki/sources/microsoft-agent-framework/checkpoints-docs.md), [Microsoft Agent Framework Workflow State docs](../../../wiki/sources/microsoft-agent-framework/state-docs.md) | Checkpoint capture scope, recovery/migration context, workflow state, and built-workflow immutability. |
| wiki | [Claude Code Dynamic Workflows docs](../../../wiki/sources/claude-code/dynamic-workflows-docs.md), [Claude Agent SDK Todo Tracking docs](../../../wiki/sources/claude-code/todo-tracking-docs.md) | Script-held orchestration plans in Claude Code dynamic workflows and controlled task-state update semantics in Agent SDK task/todo tracking. |
| wiki | [Airflow DAG docs](../../../wiki/sources/apache-airflow/dags-docs.md) | DAG, task dependencies, DagRun, and control-flow basics. |
| wiki | [Airflow Dag Run docs](../../../wiki/sources/apache-airflow/dag-run-docs.md), [Airflow Backfill docs](../../../wiki/sources/apache-airflow/backfill-docs.md) | DagRun, catchup, backfill, reprocessing behavior, and historical-interval run creation semantics. |
| wiki | [Airflow Scheduler docs](../../../wiki/sources/apache-airflow/scheduler-docs.md) | Scheduler, metadata DB, DagRun, and TaskInstance advancement semantics. |
| wiki | [Airflow Dynamic Task Mapping docs](../../../wiki/sources/apache-airflow/dynamic-task-mapping-docs.md) | Runtime task fan-out and mapped task instances. |
| wiki | [Airflow Deferrable Operators docs](../../../wiki/sources/apache-airflow/deferrable-operators-docs.md) | Task/operator deferral, triggerer waiting, and state-transfer limitations. |
| wiki | [Airflow Event-Driven Scheduling docs](../../../wiki/sources/apache-airflow/event-scheduling-docs.md) | `BaseEventTrigger` and event-driven DAG scheduling constraints. |
| wiki | [Airflow HITL docs](../../../wiki/sources/apache-airflow/hitl-docs.md) | Human input, approval, branch selection, and notification capabilities. |
| wiki | [Airflow Task States docs](../../../wiki/sources/apache-airflow/task-states-docs.md) | TaskInstance states, deferred, removed, and heartbeat-timeout semantics. |
| wiki | [Airflow DAG File Processing docs](../../../wiki/sources/apache-airflow/dagfile-processing-docs.md), [Airflow DAG Serialization docs](../../../wiki/sources/apache-airflow/dag-serialization-docs.md), [Airflow DAG Bundles docs](../../../wiki/sources/apache-airflow/dag-bundles-docs.md), [Airflow DagRun verify_integrity source](../../../wiki/sources/apache-airflow/dagrun-verify-integrity-source.md) | DAG file processing, serialized DAG scheduling views, bundle versioning, and reconciliation boundaries for existing DagRuns and task instances. |
| wiki | [LangGraph Overview docs](../../../wiki/sources/langgraph/overview-docs.md) | LangGraph long-running stateful agents/workflows and runtime positioning. |
| wiki | [LangGraph Persistence docs](../../../wiki/sources/langgraph/persistence-docs.md) | checkpointers, stores, threads/thread_id, and persistence semantics. |
| wiki | [LangGraph Interrupts docs](../../../wiki/sources/langgraph/interrupts-docs.md) | `interrupt()`, resume, and HITL semantics. |
| wiki | [LangGraph Fault Tolerance docs](../../../wiki/sources/langgraph/fault-tolerance-docs.md) | graph/node execution semantics for retries, timeouts, and error handlers. |
| wiki | [LangGraph Agent Server docs](../../../wiki/sources/langgraph/agent-server-docs.md) | Agent Server persistence database, task queue, and queue-worker boundaries. |
| wiki | [LangGraph Graph Migrations docs](../../../wiki/sources/langgraph/graph-migrations-docs.md) | Restricted boundaries for recovering an existing thread under a new graph definition. |
| wiki | [LangGraph Time Travel docs](../../../wiki/sources/langgraph/time-travel-docs.md) | Checkpoint replay, fork, and the effect of `update_state` on future execution paths. |
| wiki | [DMTF Redfish standards page](../../../wiki/sources/dmtf/redfish-standards-page.md), [Canonical MAAS README](../../../wiki/sources/canonical/maas-readme.md), [OpenStack Ironic README](../../../wiki/sources/openstack/ironic-readme.md), [Tinkerbell README](../../../wiki/sources/tinkerbell/readme.md) | Evidence for bare-metal hardware management, machine lifecycle, and provisioning control planes. |
| wiki | [Foreman README](../../../wiki/sources/the-foreman/readme.md), [Cobbler README](../../../wiki/sources/cobbler/readme.md), [xCAT Documentation Index](../../../wiki/sources/xcat/docs-index.md), [Metal3 BareMetalHost API docs](../../../wiki/sources/metal3/baremetal-operator-api.md), [Slurm Overview docs](../../../wiki/sources/slurm/overview-docs.md) | Evidence for lifecycle management, installation, cluster management, CRD bare-metal resources, and job-scheduling control planes. |

### Claims supported

| Claim | Evidence | Limitation |
| --- | --- | --- |
| Bare-metal Cluster Buildout is a decision boundary distinct from the existing generic workflow comparison page. | User input; raw draft; workflow concepts comparison. | The raw draft is not authoritative technical evidence; this page still needs to be supported by first-party source projections. |
| Platform selection should compare long-running process objects, state source of truth, external event ingress, waiting model, side-effect boundary, localized failure, and process evolution rather than only task-execution capability. | Workflow concepts comparison; Temporal, Azure Durable Functions / Durable Task, Microsoft Agent Framework Durable Extension, Airflow, and LangGraph source pages. | This is the wiki's synthesized analysis framework, not an official vendor taxonomy. |
| Temporal should be used as the primary baseline / reference-architecture anchor for core resource-process modeling, but it must not be written as a confirmed procurement or engineering winner; Azure Durable Functions / Durable Task should remain a same-tier strong durable-orchestration candidate for comparison. | Temporal, Azure Durable Functions / Durable Task, Microsoft Agent Framework Durable Extension, Durable Task SDKs, and Durable Task Scheduler source pages; user correction that evidence should come before the decision; multi-agent GPT-5.5 review of the decision section. | This is a modeling-semantic and candidate-positioning judgment under current evidence constraints, not a procurement decision; POC is still required for the target scenario; the Temporal-vs-MAF subclaim does not cover Azure Durable Task. |
| Temporal's durable Workflow Execution, message passing, Timer, Activity, and Child Workflow are a strong first anchor for core resource-process modeling. | Temporal Workflows, Activities, Message Passing, Timers, and Child Workflows source pages. | Temporal does not store all domain facts; Signals/Updates do not replace a complete command gateway and do not automatically handle physical-side-effect idempotency, compensation, or business dashboarding; worker placement, history growth, versioning, and operational cost still need validation. |
| If the only goal is to compare how much Temporal and MAF Durable Extension distort the bare-metal primary process-manager business model, while leaving ops cost, organizational stack, and cloud-hosting convenience for later POC, and if AI ergonomic benefit is limited to agent/HITL authoring and adapter-layer benefit, then Temporal is significantly less distorted in the core resource-process dimensions of long-running resource identity, resource partitioning, runtime event ingress, localized failure catch-up, physical side-effect boundary, history management, version evolution, and process audit. | User narrowed the question on 2026-06-17 and then asked to recheck what extra value MAF "higher integration" really brings; Temporal and MAF Durable Extension capability boundaries; Temporal Workflows, Activities, Message Passing, Child Workflows, Continue-As-New, Reset, and Worker Versioning source pages; MAF Durable Extension, Durable Workflow Registration, and Durable Executor Dispatcher source pages; raw MAF durable runner / edge map / dispatcher source code; MAF AIAgentBinding, DurableAIAgent, AgentEntity, AgentSessionId, and Azure Functions BuiltInFunctions raw source code. | This is a narrow modeling-semantic judgment, not a procurement or engineering winner, and not an unconditional all-dimensions victory; it does not cover Azure Durable Task; both candidates still need external inventory/resource graph, idempotency, read-back verification, compensation, audit, and dashboarding. |
| Bare-metal control planes are not shell commands, and many nodes require asynchronous human action; these factors do not make a pure Agent Graph automatically become the primary process manager. In practice they usually require a durable/event-sourced process manager to own event ingress, resource binding, approval versions, coordination audit, and post-recovery catch-up. | User's follow-up on 2026-06-17; bare-metal toolchain source pages; Temporal Message Passing, Activities, and Child Workflows source pages; MAF Durable Extension, Durable Executor Dispatcher, and RequestPort-related source evidence. | If the external fact warehouse holds the resource facts, and a Durable Extension-backed graph/hybrid personally owns the process-control path, event interpretation, localized catch-up, compensation decisions, side-effect boundary, and coordination audit instead of merely serving as an auxiliary agent/HITL surface, it can still be a primary baseline. |
| The correct boundary for integrating agents with Temporal is for the agent to participate as an Activity, Child Workflow, or external agent service; agent-generated plan/resource-graph changes should be treated as untrusted `PlanPatch` input that enters the Workflow through a command API plus Update/Signal, and the Workflow should use Continue-As-New at a controlled boundary to hand off explicit state. | Temporal Dynamic AI Agents blog; Temporal Activities, Message Passing, Continue-As-New, and Worker Versioning source pages; user's 2026-06-17 architecture assumption. | The agent should not perform LLM/tool I/O directly inside the Workflow replay path; Continue-As-New is not an edit-graph API for the agent, not physical rollback, and not arbitrary plan migration; external auth, schema, policy, inventory reconcile, idempotency, and human approval still need to be designed. |
| Public practice evidence better supports "stable outer orchestration + controlled plan/task-state updates" than agent self-modifying topology arbitrarily inside a production workflow. | Claude Code Dynamic Workflows docs; Claude Agent SDK Todo Tracking docs; Microsoft Agent Framework Workflow State and Checkpoints docs; Temporal Dynamic Workflow and deterministic-constraints-related source pages. | Claude Code is a software-engineering agent orchestration product and does not directly equal bare-metal buildout; this claim is a cross-source mechanism synthesis, not a statistical conclusion about all agent-workflow frameworks. |
| Temporal Reset, Continue-As-New, and Worker Versioning cannot be written as physical rollback, arbitrary plan migration, or automatic upgrade. | Temporal Reset, Continue-As-New, and Worker Versioning source pages. | These mechanisms still serve as constrained recovery, history truncation, and version-routing tools. |
| Azure Durable Functions / Durable Task has durable orchestration, activity, timer, external event, entity, event sourcing, checkpoint/replay, sub-orchestration, instance identity, instance management, and orchestration versioning capabilities adjacent to the primary process manager, so it should be compared in the same candidate tier as Temporal. | Azure Durable Functions Overview, Durable Task Orchestrations, Timers, External Events, Entities, Instance Management, and Orchestration Versioning source pages. | Both Durable Functions and Temporal need an external fact layer, idempotency, and replay discipline; the real difference lies in command model, hosting/backend, versioning rollout, and observation/operations boundaries. |
| The core difference for Azure Durable Functions / Durable Task is that the Azure Functions product surface, standalone Durable Task SDKs, Durable Task Scheduler managed backend, language SDK state, and private connectivity must be separated first. | Durable Task Hosting Model, Durable Task SDKs Overview, Durable Task Scheduler, Azure Functions Scale and Hosting, and Durable Task Storage Providers source pages. | This page has not measured performance or operational cost in different hosting/backend, private-endpoint, air-gapped, or network environments. |
| Durable orchestrator replay, storage providers, entities, external events, orchestration versioning, and management APIs are durable runtime semantics and boundaries. In bare-metal buildout, they must be combined with external inventory/resource graph, business event contracts, and side-effect discipline; they cannot alone prove or disqualify candidate status. | Durable Task Orchestrations, Code Constraints, Storage Providers, External Events, Entities, Instance Management, and Orchestration Versioning source pages; bare-metal toolchain source pages. | These are not Azure-specific defects, and they also cannot be written as Azure automatically satisfying business command gateway, resource graph, or physical-side-effect safety. |
| Direct Durable primitives are the direct orchestrator/client/entity surface of Durable Functions / Durable Task, not synonymous with "no MAF"; MAF Durable Extension can compose these capabilities as a Durable Task-backed graph/agent/HITL layer, but the MAF graph surface is not a strict superset of direct primitives. | Azure Durable Extension direct context/client raw source code; MAF ServiceCollectionExtensions, DurableExecutorDispatcher, DurableAgentContext, DurableActivityExecutor, and DurableWorkflowContext raw source code; the Azure/MAF relationship page. | This is a source-code boundary judgment; a normal MAF executor does not automatically have the full `TaskOrchestrationContext`, and complex direct primitives must enter through graph mapping, agent/tool context, service layer, custom orchestrator, or hybrid composition. |
| Microsoft Agent Framework Durable Workflow Extension has evidence for Durable Task-backed graph workflow, checkpoint/recover, activity/entity/sub-orchestration/external-event dispatch, and multi-host/stateless-worker recovery; when Agent Framework control is a first-class requirement, it should be a priority POC or hybrid candidate within the Azure / Durable Task route. | Microsoft Agent Framework Durable Extension, Durable Workflow Registration, Durable Executor Dispatcher, Workflows Overview, WorkflowBuilder, Functional Workflows, and Durable Task Scheduler source pages; MAF composition raw source code; Direct Durable primitives raw source code; MAF in-process / durable graph edge-runner raw source code. | The evidence supports a Durable Extension-backed graph/hybrid solution; it cannot be automatically extrapolated to the standard checkpoints surface, the functional workflow surface, or any core workflow surface without Durable Extension enabled; self-host workers still connect to the Durable Task Scheduler backend; whether it is a primary baseline depends on whether the graph/hybrid path itself carries the primary process responsibilities. Durable runner preserves fan-in, fan-out, and selector semantics, but it does not support targeted messages (`DurableMessageEnvelope` has no `TargetId`; in-process `DirectEdgeRunner` checks `TargetId` matching in lines 21-25). |
| The real difference of Microsoft Agent Framework Durable Workflow Extension is the Agent Framework graph/executor/superstep/agent entity abstraction layer on top of Durable Task: it can reduce glue for graph runner, agent session persistence, pending-input discovery/respond loops, and AI/HITL authoring surfaces, but it does not automatically replace the primary process manager's PlanPatch schema, command API, auth, idempotency, resource binding, reconcile, compensation, audit, and dashboard projection. | Microsoft Agent Framework Workflows Overview, WorkflowBuilder, Functional Workflows, Workflow Checkpoints, Workflow State, Durable Executor Dispatcher, and Durable Extension source pages; MAF AIAgentBinding, DurableAIAgent, AgentEntity, AgentSessionId, DurableAgentContext, and Azure Functions BuiltInFunctions raw source code; Temporal Child Workflows, Message Passing, Continue-As-New, and Worker Versioning source pages. | Resource partitioning is the bare-metal buildout architecture mapping in this page, not an official Microsoft or Temporal reference architecture for this scenario; MAF's agent/HITL advantage is authoring/control/runtime ergonomics and state-placement advantage, and it turns into primary process-manager value only if the POC proves the graph/hybrid path holds the primary process-control duties. |
| If the business already assumes the external operational data warehouse is the observed baseline for physical state while Event History / Durable history remains the coordination command truth line, MAF does not need to persist the full observed state itself; but it still must stably reference external resource identity, personally carry the desired/coordination-side process-control path, and explicitly implement an observe/compare/command/wait reconcile loop before it can be a primary process-manager candidate. | User clarification on the external data-warehouse observed baseline on 2026-06-17; Process Manager dual truth-line architecture analysis page; Temporal-vs-MAF capability boundary; Temporal, Durable Task, and MAF source pages/raw evidence. | This correction only applies to the observation-driven dual-truth-line architecture; if another domain process service also owns event interpretation, catch-up, compensation, and coordination-audit interpretation, that service is the primary process manager and MAF remains an adapter. |
| Airflow's Dynamic Task Mapping, Deferrable Operators, Event-Driven Scheduling, HITL, TaskInstance states, DagRun/catchup/backfill, DAG processing/serialization, bundle versioning, and `DagRun.verify_integrity` prove that it can wait, trigger, accept human input, fan out, reprocess historical intervals, and manage deployment versions with controlled DagRun reconciliation; but its first-class objects center on DAG/DagRun/TaskInstance/schedule/data interval, so as the bare-metal primary process manager it more easily flattens the long-running resource process into schedule-graph reprocessing than Temporal Workflow/Child Workflow/Signals/Updates/Run boundaries do. | Airflow DAG, Dag Run, Backfill, Scheduler, Dynamic Task Mapping, Deferrable Operators, Event-Driven Scheduling, HITL, Task States, DAG File Processing, DAG Serialization, DAG Bundles, and DagRun verify_integrity source pages; Temporal Child Workflows, Message Passing, Reset, Continue-As-New, and Worker Versioning source pages. | Event schema, reconcile, migration, side effects, and the external fact layer are common gates; this page judges which runtime's first-class modeling anchors fit more naturally after those gates are satisfied. |
| Airflow's core state objects are DagRun/TaskInstance/mapped task/deferred task scheduler/task-execution states and should not directly replace bare-metal resource facts. | Airflow DAG, Scheduler, Task States, and Deferrable Operators source pages. | Airflow can read and write external domain state in tasks; this page rejects treating the Airflow metadata DB as the domain source of truth. |
| LangGraph's persistence, interrupt/resume, fault tolerance, Agent Server, graph migrations, and time travel prove that it can run long-lived stateful agent graph/thread executions; but the current evidence centers on graph/thread/run/checkpoint/store rather than a first-class durable resource-process identity, child execution, and workflow message ingress. | LangGraph Overview, Persistence, Interrupts, Fault Tolerance, Agent Server, Graph Migrations, and Time Travel source pages; Temporal Workflows, Message Passing, and Child Workflows source pages. | Temporal also needs the business layer to define resource meaning; the difference is not "who automatically understands resources" but rather what process-modeling anchors the current first-party evidence provides. |
| A LangGraph POC for primary-process-manager status must prove that graph/thread explicitly owns the long-running control path, event interpretation, localized catch-up, audit, migration strategy, and side-effect boundary; otherwise the safer position is AI diagnosis, operator copilot, HITL decision support, or agent automation adapter. | LangGraph Persistence, Interrupts, Fault Tolerance, Time Travel, and Agent Server source pages; Temporal Reset, Activities, Message Passing, and Child Workflows source pages. | checkpoint/store, time travel/fork, and Agent Server queue worker are usable mechanisms or evidence boundaries, not LangGraph-specific defects; they cannot be independently extrapolated into primary-process-manager fit. |
| external inventory/resource graph/audit store, the business event model, side-effect discipline, dashboard projection, and migration/version discipline are common POC gates for bare-metal buildout, not defects unique to any candidate; but common gates do not erase runtime-native model differences, and if another domain process service owns long-running process state, event interpretation, localized catch-up, and compensation decisions, that service is the primary process manager. | Temporal, Azure Durable Functions, Microsoft Agent Framework, Airflow, and LangGraph source pages; bare-metal toolchain source pages. | Specific data models, lock protocols, and audit schemas still need to be designed separately; the presence of these common prerequisites does not prove a candidate is unsuitable as a primary process manager, and it does not prove a runtime already carries the primary process-control path. |
| Redfish, MAAS, Ironic, Tinkerbell, Foreman, Cobbler, xCAT, Metal3, and Slurm are not stateless command collections; they are protocols, control planes, resource models, or schedulers and should be coordinated and observed by the upper-layer process manager. | DMTF Redfish, MAAS, Ironic, Tinkerbell, Foreman, Cobbler, xCAT, Metal3, and Slurm source pages. | These tools differ in coverage, maturity, project status, and applicability; this page only uses them to establish the lower-layer domain-control-plane boundary. |
| The judgment on this page still needs POC, operational, and organizational constraints to be validated before it becomes a procurement or engineering baseline. | User input; raw draft boundary; limitations in the source pages. | There is currently no measured data, scale parameter, team experience, cost model, or UI/operations maturity assessment. |
