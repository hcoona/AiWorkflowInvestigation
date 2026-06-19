---
marp: true
theme: default
paginate: true
size: 16:9
html: true
title: Bare-Metal Cluster Buildout Process Manager Selection
description: Main process-manager platform selection for physical/bare-metal Cluster Buildout.
---

<!-- markdownlint-disable MD013 MD022 MD025 MD033 MD036 -->

<style>
section {
  --body-font-size: 26px;
  font-size: var(--body-font-size);
  padding: 46px 54px;
  display: flex;
  flex-direction: column;
  place-content: start stretch;
  align-content: start;
  justify-content: flex-start;
  align-items: stretch;
}
section.compact {
  --body-font-size: 23px;
}
section h1 {
  font-size: 40px;
  line-height: 1.08;
  margin: 0 0 0.55rem;
}
section h2 {
  font-size: 30px;
  line-height: 1.12;
  margin: 0 0 0.65rem;
}
section p {
  margin: 0.45rem 0;
}
section ul, section ol {
  margin: 0.45rem 0 0.6rem;
  padding-left: 1.35rem;
}
section li {
  margin: 0.18rem 0;
}
.grid-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.9rem;
  margin-top: 0.65rem;
}
.grid-3 {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
  margin-top: 0.65rem;
}
.card {
  border: 2px solid #d0d7de;
  border-radius: 12px;
  padding: 0.68rem;
}
.card ul {
  margin: 0.45rem 0 0;
  padding-left: 1.1rem;
}
.center {
  text-align: center;
}
.flow {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.45rem;
  margin-top: 1rem;
}
.step {
  border: 2px solid #0969da;
  border-radius: 12px;
  padding: 0.65rem;
  min-height: 4.8rem;
  flex: 1;
  background: #f6f8fa;
}
.arrow {
  font-size: 1.5rem;
  color: #57606a;
}
.matrix {
  font-size: 18px;
}
.matrix td, .matrix th {
  padding: 0.24rem 0.32rem;
}
.legend {
  font-size: 19px;
}
.ok { color: #1a7f37; font-weight: 700; }
.warn { color: #9a6700; font-weight: 700; }
.bad { color: #cf222e; font-weight: 700; }
</style>

# Bare-Metal Cluster Buildout
## Process Manager Selection

**Recommendation**:
Use **Temporal** as the first-wave main process-manager PoC/reference baseline.

**Challengers**:
Azure Durable Functions / Durable Task,
including standalone Durable Task SDK + Scheduler PoC,
and Microsoft Agent Framework Durable Extension.

<!--
Speaker note:
Frame this as an engineering selection decision, not a generic product tour.
The decision is specifically about the main process manager for physical/bare-metal Cluster Buildout.
-->

---

# Why Bare-Metal Buildout Is Different

This is a **long-running resource-process control** problem.

- Heterogeneous hardware, firmware, racks, fabrics, credentials, and BMC networks
- Constrained command locations and credential boundaries
- Long waits, vendor/human intervention, and partial physical uncertainty
- Not ordinary shell commands: many steps coordinate control planes, people, external systems, or physical inspection
- Earlier local checks can pass while later integrated validation reveals slice-scoped defects

<!--
Speaker note:
Keep this slide focused on why the runtime decision is hard.
Do not drift into a general bare-metal architecture overview.
-->

---

# Deciding Failure Scenario

<div class="flow">
  <div class="step"><strong>Local pass</strong><br>10 nodes pass OS / driver checks</div>
  <div class="arrow">→</div>
  <div class="step"><strong>Integrated defect</strong><br>Rack validation finds 3 affected nodes</div>
  <div class="arrow">→</div>
  <div class="step"><strong>Split path</strong><br>3 repair + catch up<br>7 continue if policy allows</div>
</div>

The runtime must handle **delayed discovery of slice-scoped defects**.

<!--
Speaker note:
This scenario is the recurring hard test.
Every candidate should be judged against whether it can carry this control path.
-->

---

# Two Independent Fact Lines

<div class="grid-2">
  <div class="card">
    <strong>Runtime execution history</strong>
    <ul>
      <li>Owns coordination state</li>
      <li>Workflow / slice state</li>
      <li>Command intent IDs</li>
      <li>Event receipt IDs and idempotency keys</li>
      <li>Accepted plan-patch decisions</li>
    </ul>
  </div>
  <div class="card">
    <strong>Operations warehouse</strong>
    <ul>
      <li>Owns observed facts</li>
      <li>Machine state</li>
      <li>Provisioning observations</li>
      <li>Validation outputs</li>
      <li>Command result facts, sources, versions, confidence</li>
    </ul>
  </div>
</div>

They are not row-by-row mappings.
Runtime decisions consume warehouse fact IDs, versions, or watermarks.

<!--
Speaker note:
Do not imply the runtime owns physical truth.
Corrected facts enter running buildouts through idempotent events or updates carrying fact IDs and versions.
-->

---

# Candidate Families

<div class="grid-3">
  <div class="card">
    <strong>Traditional workflow / process</strong>
    <ul>
      <li>Temporal</li>
      <li>Airflow</li>
    </ul>
  </div>
  <div class="card">
    <strong>Azure Native</strong>
    <ul>
      <li>Azure Durable Functions / Durable Task</li>
      <li>PoC topology: standalone SDK workers + Scheduler</li>
    </ul>
  </div>
  <div class="card">
    <strong>AI Native</strong>
    <ul>
      <li>Microsoft Agent Framework Durable Extension-backed graph workflow or hybrid</li>
      <li>LangGraph</li>
    </ul>
  </div>
</div>

<!--
Speaker note:
Do not describe this as an analysis-history expansion.
These are the candidate families for the business scenario.
-->

---

# Hard Test Criteria

Evaluate every candidate on the same control test:

- Resource-process identity
- Event entry into the already-running buildout
- Slice repair and catch-up
- Task routing plus externally enforced worker placement
- Lock, pool, credential, and location enforcement
- Side-effect audit and retry safety
- Recovery/versioning and private control-plane fit

<!--
Speaker note:
These are the decision criteria.
Adjacent systems are required integrations, but not comparison topics.
-->

---

# Criteria-by-Candidate Matrix

<table class="matrix">
  <tr>
    <th>Criterion group</th>
    <th>Temporal</th>
    <th>Azure DT SDK + Scheduler</th>
    <th>MAF Durable</th>
    <th>Airflow</th>
    <th>LangGraph</th>
  </tr>
  <tr><td>Identity + event entry</td><td class="ok">Direct primitive</td><td class="warn">Durable primitive + topology PoC</td><td class="warn">Graph mapping + contract PoC</td><td>External control service</td><td>External control service</td></tr>
  <tr><td>Slice repair / catch-up</td><td class="ok">Primitive composition + PoC</td><td class="warn">Durable primitive + topology PoC</td><td class="warn">Graph mapping + contract PoC</td><td>External control service</td><td>External control service</td></tr>
  <tr><td>Task routing</td><td class="ok">Direct primitive</td><td class="warn">Topology/filtering PoC</td><td class="warn">Graph dispatch PoC</td><td>External contract</td><td>External control service</td></tr>
  <tr><td>Locks / pools / credentials</td><td>External contract</td><td>External contract</td><td>External contract</td><td>External</td><td>External</td></tr>
  <tr><td>Replay / audit / versioning</td><td class="ok">Direct primitive</td><td class="warn">Durable primitive + topology PoC</td><td class="warn">Graph mapping + contract PoC</td><td>External control service</td><td>External control service</td></tr>
  <tr><td>Control semantics</td><td class="ok">Primitive composition + PoC</td><td class="warn">Durable primitive + topology PoC</td><td class="warn">Graph mapping + contract PoC</td><td class="bad">Not baseline-fit</td><td class="bad">Not baseline-fit</td></tr>
</table>

<div class="legend">
Direct primitive = first-class runtime primitive.
PoC terms mean the primitive exists, but target topology, graph mapping, or resource contract must prove fit.
For Azure task routing, the PoC specifically tests topology/filtering rather than an activity-level dynamic routing primitive.
<br>
<small>Criterion groups are compressed from the source analysis' core modeling dimensions and PoC gates.</small>
</div>

<!--
Speaker note:
Use the matrix to make the conclusion visible.
Temporal is the recommended first-wave baseline because more of the control path is expressible with first-class or direct primitive composition.
It still has PoC obligations.
Mapping to source analysis:
resource-process identity and event entry come from "长期资源过程身份" and "运行中业务事件入口";
slice repair/catch-up comes from "资源分区与局部失败追平";
task routing and lock/pool/credential contracts come from the POC gates and worker-placement discussion;
replay/audit/versioning comes from "历史治理与版本演进" and "过程审计事实线";
control semantics summarizes whether the runtime's first-class objects carry the main process-manager control path.
-->

---

# Evidence Behind the Matrix

**Temporal**:
Workflow ID, Signals/Updates, Child Workflows, Activities, Task Queues, Event History.

**Azure Durable Task SDK + Scheduler**:
orchestration identity, external events, sub-orchestrations, activities, replay; topology and private placement remain PoC.

**MAF Durable Extension**:
counts only if Durable Extension preserves Durable Task-like identity, event, replay, and audit semantics.

**Airflow / LangGraph**:
current evidence puts the main control path outside their first-class objects;
they re-enter only if PoC proves those objects own resource identity, event entry, slice catch-up, and side-effect audit without a separate domain process service.

<!--
Speaker note:
This slide exists to keep the matrix auditable without turning the live matrix into an unreadable wall of text.
-->

---

# Decision Thesis

**Temporal is the recommended PoC/reference baseline.**

It is the strongest reference architecture for testing the delayed-defect hard test:

- Durable resource-process identity and running event entry
- Slice-level branch/catch-up through workflow composition
- Task Queue routing to pre-deployed constrained worker pools

Azure Durable Task SDK + Scheduler and MAF Durable Extension remain challengers.

<!--
Speaker note:
Say explicitly that this is not a final procurement winner.
It is the first-wave baseline unless challengers prove equivalent control behavior with better operational fit.
-->

---

<!-- _class: compact -->

# AI-Native Has No Standalone Main-Decision Weight

AI-generated plans, tool calls, and accepted plan patches can enter through command APIs or events.
Human/vendor follow-up is usually a long-lived external work item, not a brief in-app approval.

For the main process-manager decision, MAF and LangGraph get no standalone AI-native credit.
Evaluate them only on durable control primitives:

- Resource-process identity
- Event entry and catch-up
- Side-effect safety and recovery
- Routing hooks compatible with externally enforced placement constraints

Treat HITL surfaces as a UI/implementation layer, not main-selection evidence by themselves.
Product UI should bind requests to durable message primitives:

- Temporal Updates for validated synchronous commands
- Temporal Signals for asynchronous notifications
- MAF RequestPort/external events where that stack is chosen

RequestPort can expose pending input, but it does not turn external human work into a short prompt.
The overall stack must still prove durable identity, routing, audit, recovery, and catch-up semantics.

<!--
Speaker note:
Do not grant MAF or LangGraph credit merely for AI-native UX.
MAF RequestPort has useful pending-input plumbing, but it still routes through Durable external events.
Most real human/vendor interactions in this scenario are long waits around external work.
Main-process-manager eligibility depends on durable control-plane primitives, not the HITL surface alone.
-->

---

# Temporal Scenario Trace

1. A defect Signal/Update reaches the running buildout Workflow.
2. Affected node/slice Child Workflows branch into repair.
3. Repair Activities schedule to zone-specific Task Queues; external contracts enforce worker placement, reservations, and credential policy.
4. Catch-up validation runs for repaired slices.
5. Unaffected Child Workflows continue when policy allows.
6. Replay/retry safety must be proven through Activity and idempotency boundaries.

<!--
Speaker note:
Do not overclaim that Temporal owns pool policy or physical truth.
Task Queues provide routing primitives; locks, pool policy, and credential enforcement remain explicit contracts.
-->

---

# Azure Durable Task Challenger Trace

<div class="grid-2">
  <div class="card">
    <strong>Known durable primitives</strong>
    <ul>
      <li>Orchestration and sub-orchestration identity</li>
      <li>External events</li>
      <li>Activity boundaries</li>
      <li>Replay</li>
    </ul>
  </div>
  <div class="card">
    <strong>PoC gates</strong>
    <ul>
      <li>Private/on-prem workers and Scheduler connectivity</li>
      <li>Backend residency, availability, SDK maturity</li>
      <li>Resource-pool routing by rack/BMC/fabric/credential zone</li>
      <li>Long-history/versioning strategy and no unsafe replay</li>
    </ul>
  </div>
</div>

<!--
Speaker note:
Keep Azure framed as a real challenger, not weak.
The question is whether the selected topology matches Temporal's placement/control model.
-->

---

# MAF Durable Extension Challenger Trace

Evaluate only **Durable Extension-backed graph workflow or hybrid MAF**.

Do **not** count standard checkpoints, functional workflows, or non-Durable Extension surfaces as equivalent.

<div class="grid-2">
  <div class="card">
    <strong>Must preserve</strong>
    <ul>
      <li>Durable process identity</li>
      <li>External-event / RequestPort delivery</li>
      <li>Replay safety and versioning</li>
      <li>Resource routing and side-effect audit</li>
    </ul>
  </div>
  <div class="card">
    <strong>PoC boundaries</strong>
    <ul>
      <li>Targeted resource-event routing still proven in PoC</li>
      <li>Self-hosted workers still need the Durable Task backend</li>
      <li>Direct Durable primitives may require hybrid/custom access</li>
    </ul>
  </div>
</div>

<!--
Speaker note:
This slide should avoid a MAF feature tour.
The only relevant question is whether the Durable Task-like control guarantees survive the graph layer.
-->

---

<!-- _class: compact -->

# Airflow and LangGraph: Not Main Process-Manager Baseline Fit

Against the main process-manager hard test:

<div class="grid-2">
  <div class="card">
    <strong>Airflow</strong>
    <ul>
      <li>Has durable DagRun / TaskInstance records.</li>
      <li>Natural model: scheduled task graph.</li>
      <li>Gap: active resource identity, event entry, and slice repair move to a domain control layer.</li>
    </ul>
  </div>
  <div class="card">
    <strong>LangGraph</strong>
    <ul>
      <li>Has thread / checkpoint and interrupt / resume primitives.</li>
      <li>Natural model: durable graph run.</li>
      <li>Gap: resource-process identity, slice catch-up, and side-effect audit move to surrounding services.</li>
    </ul>
  </div>
</div>

<!--
Speaker note:
Do not discuss residual use cases.
The only point is why these do not satisfy the main process-manager role.
-->

---

# PoC Control Boundary

Use Temporal as the first-wave baseline to test the decision thesis.

Fixed dependencies, not comparison topics:

- Command gateway
- Inventory / resource graph
- Operations warehouse
- Dashboard projection
- Idempotency, lock, pool, credential, and compensation contracts

The services/contracts are fixed dependencies.
Each candidate is compared on how cleanly and safely its runtime control path invokes and preserves those contracts.

<!--
Speaker note:
This keeps adjacent systems from becoming new selection topics.
They are required regardless of runtime.
-->

---

# PoC Pass / Fail: Control Flow

A valid candidate must pass this script:

1. Local checks write passing warehouse facts with source and version.
2. Rack validation emits a defect event with affected node IDs, validation ID, and fact version.
3. The event targets the already-running buildout and is delivered duplicate/out-of-order.
4. Affected slices branch and repair; unaffected nodes continue only work allowed by lock/pool policy.
5. Final validation waits for repaired-slice catch-up and reads required warehouse fact versions.

<!--
Speaker note:
This is the process-control half of the falsifiable test.
If a candidate passes only by moving the main control path into a custom domain service, it fails the main process-manager role.
-->

---

# PoC Pass / Fail: Safety Fences

The same PoC must also prove:

1. Repair commands carry idempotency key, target resource, lease/fencing token, credential scope, and worker zone.
2. Repair commands acquire/release reservations.
3. Work is scheduled only through contracts backed by authorized zone workers.
4. Unauthorized reservation, route, or credential use is rejected and audited.
5. Crash after command dispatch but before result persistence reconciles by command intent ID before any reissue.
6. Duplicate events, stale fact versions, expired leases, and credential-scope mismatches are rejected or deduplicated.

<!--
Speaker note:
This is the side-effect fencing half of the test.
-->

---

# Revisit Triggers

Azure Durable Task SDK + Scheduler or MAF Durable Extension can displace Temporal only if they prove:

- Equivalent control behavior
- Lower operational risk or better platform fit
- Clean integration across execution history and warehouse facts
- Safe recovery without unsafe command replay

Airflow or LangGraph can re-enter the main process-manager baseline race only if their first-class objects own the main control path without externalizing it to a domain service.

<!--
Speaker note:
End with the decision rule:
choose the runtime whose first-class objects carry the long-running resource process with the least semantic distortion.
-->
