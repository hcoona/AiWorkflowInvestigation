# Bare-Metal Cluster Buildout Process Manager Selection Outline

## Presentation Constraints

- **Language**: American English.
- **Tone**: Professional workplace tone.
- **Speaker role**: Internal architect.
- **Audience**: Internal software engineers.
- **Target duration**: 30-40 minutes.
- **Core decision**: Select the main process manager for physical/bare-metal
  Cluster Buildout.
- **Primary conclusion**:
  Temporal is the recommended main process-manager PoC/reference baseline.
  Azure Durable Task SDK + Scheduler
  and Microsoft Agent Framework Durable Extension remain challengers.
  Airflow and LangGraph are eliminated from the main process-manager baseline.

## Section 1 -- Decision Frame

1. **Decision Question** -- Select the main process manager for
   physical/bare-metal Cluster Buildout; this is not about a generic workflow
   engine, UI, AI graph library, or adjacent adapter layer.

2. **Why Physical Buildout Is Different** -- Heterogeneous hardware and
   networks, constrained command locations, credentials, BMC/fabric/rack
   boundaries, long waits, human/vendor intervention, and integrated validation
   make this a long-running resource-process control problem.

3. **Deciding Failure Scenario** -- 10 nodes pass local OS/driver checks; later
   rack-level scheduler validation exposes a defect affecting 3 nodes; those 3
   branch, repair, and catch up while the other 7 continue.

4. **Two Fact Lines and System Boundary** -- Runtime execution history is
   authoritative for process coordination only: workflow/slice state, command
   intent IDs, event receipt IDs, idempotency keys, accepted plan-patch
   decisions, and coordination audit.
   The operations warehouse is authoritative
   for observed physical/test/business facts: machine state,
   provisioning observations, validation outputs, command gateway result facts,
   timestamps, sources, schema/tool versions, and confidence.
   Runtime decisions read warehouse facts by explicit version or watermark.
   New or corrected warehouse facts do not mutate runtime state directly;
   they enter running buildouts through idempotent events/updates carrying fact
   IDs and versions.
   When warehouse facts supersede runtime assumptions,
   the runtime invalidates
   or branches the affected slice rather than silently overwriting history.

## Section 2 -- Evidence Frame

5. **Candidate Families** -- Traditional workflow/process: Temporal and
   Airflow; Azure Native: standalone Durable Task SDK workers with Durable Task
   Scheduler backend; AI Native: Microsoft Agent Framework Durable
   Extension-backed graph workflow or hybrid, and LangGraph.

6. **Hard Test and Evaluation Criteria** -- Judge every candidate against the
   same rack-level delayed-defect test:

   1. Ten nodes pass local validation.
   2. Later rack validation finds a defect on three nodes.
   3. The running buildout receives the defect event with affected node IDs and
      fact version.
   4. The three affected nodes branch into repair.
   5. The other seven continue only work allowed by lock and pool policy.
   6. Duplicate or out-of-order events, restarts, and retries do not reissue
      unsafe commands.
   7. Final validation waits for repaired nodes to catch up.

   Evaluate resource-process identity, event entry, slice catch-up, task routing,
   lock/pool/credential enforcement, side-effect audit/retry safety,
   recovery/versioning, private control-plane fit, and operational fit.

7. **Criteria-by-Candidate Matrix** -- Use a compressed live-slide matrix
   and keep primitive-by-primitive evidence in speaker notes.

   Labels: `native fit`, `native composition, PoC-required`,
   `known primitive, PoC-required`, `external contract required`,
   `external scaffolding`, `not baseline-fit`.

   | Criterion group | Temporal | Azure Durable Task SDK + Scheduler | MAF Durable Extension | Airflow | LangGraph |
   | --- | --- | --- | --- | --- | --- |
   | Resource-process identity + event entry | native fit | known primitive, PoC-required | known primitive, PoC-required | external scaffolding | external scaffolding |
   | Slice repair / catch-up | native composition, PoC-required | known primitive, PoC-required | known primitive, PoC-required | external scaffolding | external scaffolding |
   | Task routing primitive | native fit | known primitive, PoC-required | known primitive, PoC-required | external contract required | external scaffolding |
   | Locks, pool policy, credential/location enforcement | external contract required | external contract required | external contract required | external scaffolding | external scaffolding |
   | Replay / audit / versioning | native fit | known primitive, PoC-required | known primitive, PoC-required | external scaffolding | external scaffolding |
   | Resource-process control semantics | native composition, PoC-required | known primitive, PoC-required | known primitive, PoC-required | not baseline-fit | not baseline-fit |
   | Private deployment and control-semantics fit | known primitive, PoC-required | known primitive, PoC-required | known primitive, PoC-required | not baseline-fit | not baseline-fit |

8. **Decision Thesis From the Matrix** -- Temporal is the recommended main
   process-manager PoC/reference baseline because it best satisfies the hard
   test with the least semantic distortion.
   Azure Durable Task SDK + Scheduler
   and MAF Durable Extension remain challengers.
   Airflow and LangGraph are eliminated from the main process-manager baseline.

9. **AI-Native Receives No Main-Decision Weight** -- AI can generate plans,
   propose plan patches, drive humans, or invoke tools through command APIs,
   events, or plan patches.
   For the main process-manager decision,
   MAF and LangGraph are evaluated only on durable control-plane primitives:
   resource-process identity, event entry, catch-up, side-effect safety,
   recovery, and worker/resource placement.

## Section 3 -- Candidate Evidence Traces

10. **Temporal Scenario Trace** -- Defect signal/update arrives at the running
    buildout workflow; affected node/slice child workflows branch; repair
    activities route to BMC/rack/fabric/credential worker pools through Task
    Queues; catch-up validation runs; unaffected child workflows continue.
    Event History records coordination audit;
    command/result audit is captured through Activity payloads,
    idempotency keys, command gateway outcomes, and warehouse observations.
    Replay/retry safety must prove no unsafe command reissue.

11. **Azure Durable Task Challenger Trace** -- Azure Durable Task has known
    durable primitives for orchestration identity, sub-orchestrations, external
    events, activity boundaries, and replay.
    The standalone SDK + Scheduler topology must prove long-history management
    and running-code versioning strategy,
    external events target active resource instances cleanly,
    workers can be partitioned by rack/BMC/fabric and credential zone,
    sub-orchestrations model node slices without unsafe replay,
    and private Scheduler/backend operations fit the buildout environment.

12. **MAF Durable Extension Challenger Trace** -- Test only Durable
    Extension-backed graph workflow or hybrid MAF.
    MAF is relevant only if its graph/executor/checkpoint/hosting layer
    preserves Durable Task-like process identity, event targeting, replay
    safety, versioning, resource routing, and side-effect audit instead of
    hiding those guarantees behind AI/HITL authoring.

13. **Airflow and LangGraph Elimination Trace** -- Against the same hard test,
    Airflow's DagRun/TaskInstance model requires an external domain process
    service for active resource-process identity, event entry into already
    running resource flows, and slice repair/catch-up; its queues/pools help
    task placement but do not make DagRun a durable resource-process object.
    LangGraph's graph/thread/checkpoint model likewise externalizes durable
    resource-process identity, side-effect audit, slice catch-up, and
    worker/resource placement into surrounding services.

## Section 4 -- PoC Decision Plan

14. **PoC Control Boundary** -- Use Temporal
    as the first-wave baseline only to test the decision thesis.
    Adjacent systems are fixed dependencies, not comparison topics:
    command gateway, inventory/resource graph, operations warehouse,
    and dashboard remain outside runtime selection.

15. **PoC Pass/Fail Checklist** -- A valid candidate must pass this script:
    local node checks write passing warehouse facts with source and version;
    later rack-level validation emits a defect event with affected node IDs,
    validation ID, and fact version; the event targets the already-running
    cluster buildout and is delivered duplicate/out-of-order; affected slice
    processes branch and repair while unaffected nodes continue only work
    allowed by lock/pool policy; repair commands acquire/release required
    resource reservations and route only to authorized
    rack/BMC/fabric/credential-zone workers; unauthorized routes are rejected
    and audited; orchestrator and worker restart mid-repair; stable idempotency
    keys prevent unsafe command reissue; final cluster validation waits for
    repaired-slice catch-up and reads required warehouse fact versions.

16. **Revisit Triggers** -- Azure Durable Task SDK + Scheduler
    or MAF can displace Temporal only
    if they prove equivalent control behavior with lower operational risk
    or better fit.
    Airflow or LangGraph can re-enter only
    if their first-class objects demonstrably own the main control path instead
    of externalizing it to a domain service.
