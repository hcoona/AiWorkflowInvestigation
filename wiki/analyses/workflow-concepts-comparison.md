---
schema_version: 2
page_type: analysis
title: "工作流概念比较：Temporal、Apache Airflow、Microsoft Agent Framework 与 LangGraph"
status: active
created: 2026-06-12
updated: 2026-06-12
summary: "以模式层比较四个多步编排系统的控制、恢复、动态性和时间语义。"
maintenance:
  edit_policy: update
validation:
  body_contract: analysis-answer-memo
tags:
  - workflow
  - orchestration
  - durability
  - ai-agents
---

## 问题

本页边界不是比较品牌生态、语言支持或各平台自造术语，而是把这些术语放进一张诊断矩阵：
先看用户如何表达 workflow，再看运行时如何解释、持久化、恢复和隔离副作用。
目标是回答：哪些差异只是命名差异，哪些差异会改变系统设计、恢复语义和选型边界。

## 答案

结论是：DAG、general graph/state machine、functional 或 imperative workflow code
都是 authoring/control representation
surface，用来描述长期工作中有哪些步骤、依赖、等待、分支和副作用边界。
它们解释“怎么写
workflow”，但不直接解释“系统怎么跑、怎么恢复、坏了以后相信什么状态”。
真正的分化点不应停在“DAG、graph 还是 code”这种表示形态上，而应继续看执行语义：
谁解释这份控制规范，什么状态被持久化，崩溃后如何恢复，以及副作用如何被隔离和重试。

关键分层是：
**控制流决定哪些路径合法、谁能决定下一步、如何恢复和审计；LLM、工具、API
调用通常只是节点或动作内部的工作负载**。
因此，不能因为四者都能承载 LLM/tool/agent workload，就把它们当成同类 agent
runtime；也不能因为它们都有 workflow、graph、task 或 step
等术语，就假定这些词语有相同语义。

因此，本页不使用单轴 taxonomy，而使用多轴诊断矩阵。
每个类比都必须说明“只在哪一轴成立”： Airflow DAG、Microsoft Agent Framework
graph workflow 和 LangGraph graph 只在 graph-shaped authoring surface 上相似；
Temporal workflow code 和 Microsoft Agent Framework functional workflow 只在
code-authored surface 上相似。
这些类比不能推出运行时等价。

### 概念分层

| 层 | 要问的问题 | 典型差异 |
| --- | --- | --- |
| 表达形态 | 用户用什么 authoring/control representation surface 描述 workflow？ | DAG、general graph/state machine、code-authored workflow、generated/learned graph。 |
| 执行解释器 | 谁读取控制规范并决定下一步？ | scheduler、event-history replay runtime、graph runner、agent orchestration runtime。 |
| 状态真源 | 哪些状态成为平台持久化真源？ | DagRun/TaskInstance metadata、Event History、checkpoint/thread state、Durable Task backend state。 |
| 恢复模型 | 崩溃后恢复的是哪类“当前位置”？ | 可运行任务集合、程序控制点与 replay-safe 局部状态、graph thread state、durable orchestration state。 |
| 副作用纪律 | 外部 I/O、LLM/tool call 如何脱离控制流并被重试或幂等化？ | task/operator、Activity、node/tool、executor/step/agent。 |
| 时间/调度模型 | 时间、触发、等待和人工暂停属于哪一层？ | DAG run timetable/asset trigger、Workflow Schedule/Timer、interrupt/resume、Durable Task timer/HITL。 |

DAG 是 graph 的受限子类，但在 workflow 语境里仍值得单列：
它强调有向无环的任务依赖、拓扑推进和 DagRun/TaskInstance 之类运行实例语义。
general graph/state machine 更宽，可以强调条件边、循环、状态迁移和
interrupt/resume。
functional/code-authored workflow 又是另一种表达形态； 只有当它与 deterministic
replay、Durable Task hosting 或其他运行时契约结合时，才形成具体的恢复语义。

### 产品映射矩阵

| 系统 | 表达形态 | 执行解释器 | 状态与恢复语义 | 副作用纪律 | 动态性与时间模型 | LLM/tool 所在层 |
| --- | --- | --- | --- | --- | --- | --- |
| Temporal | code-authored deterministic workflow program；代码是控制表示，不是普通脚本 | worker 通过 Event History replay 重新执行 deterministic workflow code，并由代码发出 Activity、Timer 等 commands | Event History 是真源；恢复时通过 replay 重建 replay-safe 局部状态与当前控制点，并校验或生成下一步命令，而不是持久化任意程序栈 | Activity 承担非确定性 I/O、LLM/API/DB 调用，并需要考虑 retry/幂等 | 代码可表达 replay-safe 的分支、循环和等待；Timer 是内部持久等待，Schedule 是外部启动 Workflow Execution 的规则 | agent loop 或 LLM/tool call 是 durable execution 之上的 workload pattern，不是专用 agent runtime |
| Airflow | explicit DAG/task graph；DAG 是无环任务依赖形态，不只是静态图图片 | scheduler 使用 serialized DAG/control spec 与 metadata DB 中的 DagRun、TaskInstance 和 mapped-task state，评估依赖、重试、pool 与并发约束，并将可调度 TaskInstance 入队给 Executor | metadata DB、DagRun、TaskInstance、XCom、retry 与 mapped task state 是真源；恢复的是任务图实例状态，不是任意程序栈 | task/operator 是副作用和重试边界 | schedule/asset/manual trigger 创建 DagRun；Dynamic Task Mapping 由 scheduler 管理运行时任务展开 | LLM/agent operator 作为 task/operator/decorator 层 payload 嵌入 DAG/task 语义，可形成显式 fan-out/fan-in pipeline |
| Microsoft Agent Framework | 同时提供 graph workflow surface 与 functional workflow surface；graph/function 是 authoring surface 维度，不是产品类型 | graph execution/superstep runner 解释 graph；functional runtime 解释 workflow/step 边界；human/agent 可参与流程 | checkpoint/resume/HITL 只有在 Durable Extension hosting 下才能按 Durable Task-backed execution 理解；不能外推为所有 surface 的默认能力 | executor、step 或 agent 承担节点工作；文档不足以证明其副作用隔离等价于 Temporal Activity | 条件路由、并行、streaming 与 HITL 更接近业务流程/agent 编排，不是 task scheduler 中心模型 | agent 是框架一等对象，workflow 用来显式组织 agent、step 与多 agent orchestration |
| LangGraph | explicit general graph/state machine；graph 是长期运行 agent/workflow 的控制表示，不等同于 Airflow DAG | graph runner 根据节点返回、条件边、human interrupt、tool/LLM 结果推进下一步 | checkpointer 物化 thread-scoped graph state；store 提供跨 thread memory，不是当前位置；interrupt/resume 依赖 thread/checkpointer；未配置 persistence 时不应假定可恢复 | node/tool 承担 I/O；per-node retry、timeout、error handler 是节点级故障处理，不自动等价于 Temporal Activity 的副作用隔离/幂等 | 条件边和节点返回驱动路径；interrupt/resume 是图/节点级暂停恢复，不是 Airflow scheduler，也不是 Temporal Timer/Schedule | LLM/tool 通常是 node 内 payload，但 runtime 原生支持 stateful agent graph、HITL 和长生命周期执行 |

### 不能混淆的等价关系

- DAG 与 workflow code 在“用户写的控制规范”这一层可以类比；
  但它们的执行解释器、状态真源和恢复算法不同，不能直接等价。
- DAG 是 graph 的受限子类；
  但 Airflow DAG 的无环任务依赖、DagRun 和 TaskInstance 语义不能外推为所有 graph
  workflow 的语义。
- graph workflow 与 functional workflow 是 authoring surface
  维度，不是互斥产品类型； Microsoft Agent Framework 同时有 graph 与 functional
  surfaces。
- Airflow DAG、Microsoft Agent Framework graph workflow 与 LangGraph graph
  只能在 graph-shaped surface 上类比，不能推出相同的运行时恢复能力。
- Temporal workflow code 与 Microsoft Agent Framework functional workflow 只能在
  code-authored surface 上类比，不能推出相同的 deterministic replay 语义。
- Temporal replay 不等于 LangGraph checkpoint
  resume：前者重放确定性控制流，后者恢复保存的图状态。
- Airflow retry/reschedule 不等于 durable in-process workflow
  recovery：它恢复的是 scheduler/task execution 状态，而不是任意 Workflow
  代码栈。
- MAF Durable Extension 不等于 MAF 全部 workflow surface 默认 durable：它是
  Durable Task-backed integration/hosting 层。
- Timer 不等于 Schedule：Temporal Timer 是 Workflow Execution
  内部的持久等待，Schedule 是独立于 Workflow Execution 的启动规则。
- Airflow 有 trigger/run，Temporal 也有 Schedule/Workflow Execution；
  差异不在“谁有调度”，而在运行内部由 scheduler 解释 task graph，还是由
  event-history replay 解释确定性程序。
- “能调用 LLM/tool”不等于“agent runtime”：LLM/tool 可能只是
  Activity、task、executor、node 内的 payload。

### 学术文献如何约束抽象层级

DeepXiv 检索到的 arXiv 文献支持把 agent workflow
当成一个内部复杂的子家族，而不是单一产品类型。
这些文献最有用的地方不是证明某个产品更强，而是提供更高层的模式语言。

| 研究线 | 可复用模式 | 对本页结论的约束 |
| --- | --- | --- |
| Agent Workflow Survey | planning、tool use、memory、multi-agent、flow、representation、protocol 等维度 | “workflow”在 agent 领域不是单一抽象，产品比较必须先说明比较轴。 |
| StateFlow | process control 与 state action 分层 | 控制流和 LLM/tool 执行应分层比较，不能把节点 payload 当成控制抽象。 |
| GraphBit | engine-orchestrated typed DAG、deterministic routing | agent workflow 研究也追求显式、可复现、可审计的图执行，但它不等同于 Temporal replay 或 Airflow DAG。 |
| GraphFlow | shared operation graph、task-adaptive workflow generation、KV/state reuse | workflow 可能是 serving optimization structure，但这种优化目标不能外推到通用 workflow engine。 |
| FlowSteer | policy 生成和编辑 workflow graph | workflow 也可以是可学习/可优化对象；这属于研究线或上层策略，不是四个产品的默认保证。 |

因此，比较 Temporal/Airflow/MAF/LangGraph 时，应先问这个类比发生在哪一轴：
是表达形态、执行解释器、状态真源、恢复模型、副作用纪律，还是时间/调度模型。
只在表达形态上相似的系统，不应被直接推导为运行语义相同。

## 影响

- 需要强确定性重放、恢复程序逻辑与局部状态、长时间运行、持久
  Timer，并把外部副作用关进受控边界：优先 Temporal。
- 需要显式 DAG/task graph、资产/时间触发、任务级可观测性和 scheduler-managed
  task-instance fan-out/fan-in：优先 Airflow。
- 需要在 agent 框架内显式组织 agent、step、多 agent orchestration，并接受
  graph/functional/durable surfaces 成熟度不完全齐整：评估 Microsoft Agent
  Framework。
- 需要低层 stateful agent graph、checkpointed thread state、HITL
  interrupt/resume，并愿意自己配置 persistence：评估 LangGraph。
- 如果讨论的是 agent workflow
  研究或未来平台能力，应单独标注“显式图”“状态机”“服务端 operation graph”“学习式
  workflow generation”等模式，避免把论文模式误写成产品保证。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| wiki | [Temporal Workflows 文档](../sources/temporal/workflows-docs.md) | Temporal Workflow 定义、执行与 Event History/replay。 |
| wiki | [Temporal Workflow 确定性约束文档](../sources/temporal/workflow-deterministic-constraints-docs.md) | Workflow 确定性约束与 replay-safe 行为。 |
| wiki | [Temporal Activities 文档](../sources/temporal/activities-docs.md) | Activities 与外部副作用边界。 |
| wiki | [Temporal Timers and Start Delays 文档](../sources/temporal/timers-delays-docs.md) | Timer 的持久等待语义与 Start Delay 的一次性延迟启动语义。 |
| wiki | [Temporal Schedule 文档](../sources/temporal/schedule-docs.md) | Schedule 作为独立外部启动规则及其 spec/policy 语义。 |
| wiki | [Temporal 动态 AI Agent 博客](../sources/temporal/dynamic-ai-agents-blog.md) | Temporal 承载动态 AI agent 的官方示例。 |
| wiki | [Temporal Deep Research Agent 博客](../sources/temporal/deep-research-agents-blog.md) | Temporal 承载 deep research agent 的官方示例。 |
| wiki | [Airflow DAG 文档](../sources/apache-airflow/dags-docs.md) | Airflow DAG、schedule、tasks 与 dependencies 的核心语义。 |
| wiki | [Airflow Scheduler 文档](../sources/apache-airflow/scheduler-docs.md) | Airflow scheduler loop、DagRun 与 TaskInstance 推进语义。 |
| wiki | [Airflow Dynamic Task Mapping 文档](../sources/apache-airflow/dynamic-task-mapping-docs.md) | 运行时动态展开 task 的语义。 |
| wiki | [Airflow Asset Scheduling 文档](../sources/apache-airflow/asset-scheduling-docs.md) | 资产更新触发 DAG 的调度语义。 |
| wiki | [Airflow Common AI Provider 博客](../sources/apache-airflow/common-ai-provider-blog.md) | Airflow common.ai provider、LLM/agent operators 与工具集。 |
| wiki | [Airflow Agentic Workloads 博客](../sources/apache-airflow/agentic-workloads-blog.md) | Dynamic Task Mapping + common.ai 的显式 fan-out/fan-in pipeline。 |
| wiki | [Microsoft Agent Framework Overview 文档](../sources/microsoft-agent-framework/overview-docs.md) | Microsoft Agent Framework 的 agents/workflows 总览。 |
| wiki | [Microsoft Agent Framework Workflows 概览](../sources/microsoft-agent-framework/workflows-overview-docs.md) | Workflows 概览与编排定位。 |
| wiki | [Microsoft Agent Framework Functional Workflows 文档](../sources/microsoft-agent-framework/functional-workflows-docs.md) | functional workflow API 与 `@workflow` / `@step`。 |
| wiki | [Microsoft Agent Framework WorkflowBuilder 文档](../sources/microsoft-agent-framework/workflow-builder-docs.md) | `WorkflowBuilder` graph API、executors、edges 与 execution。 |
| wiki | [Microsoft Agent Framework Durable Extension 文档](../sources/microsoft-agent-framework/durable-extension-docs.md) | Durable Extension 与 Durable Task-backed execution。 |
| wiki | [LangGraph Overview 文档](../sources/langgraph/overview-docs.md) | LangGraph 的 low-level orchestration framework/runtime 定位。 |
| wiki | [LangGraph Persistence 文档](../sources/langgraph/persistence-docs.md) | checkpointers 与 stores 的持久化分层。 |
| wiki | [LangGraph Interrupts 文档](../sources/langgraph/interrupts-docs.md) | interrupt/resume/HITL 的暂停与恢复语义。 |
| wiki | [LangGraph Fault Tolerance 文档](../sources/langgraph/fault-tolerance-docs.md) | retries、timeouts、error handlers 的 fault tolerance 语义。 |
| wiki | [Agent Workflow Survey 论文](../sources/arxiv/agent-workflow-survey-2508-01186.md) | agent workflow 综述、能力/架构分类和 workflow management 维度。 |
| wiki | [StateFlow 论文](../sources/arxiv/stateflow-2403-11322.md) | state-driven workflow、状态转移与 action 分层。 |
| wiki | [GraphBit 论文](../sources/arxiv/graphbit-2605-13848.md) | engine-orchestrated typed DAG 和 deterministic routing。 |
| wiki | [GraphFlow 论文](../sources/arxiv/graphflow-2605-22566.md) | operation graph、task-adaptive workflow generation 与 KV state management。 |
| wiki | [FlowSteer 论文](../sources/arxiv/flowsteer-2602-01664.md) | workflow graph policy、executable canvas 和 RL-based orchestration。 |
| session | 当前会话 `eb8a80bb-159f-406e-af3e-c4037c085c4d` 的 `abstraction-critic`、`durable-patterns`、`scheduler-patterns`、`agent-graph-patterns`、`taxonomy-synthesis`、`dag-code-equivalence`、`dag-code-distinction`、`workflow-abstraction`、`taxonomy-judge-2`、`taxonomy-red-team-2`、`review-temporal-control`、`review-airflow-control`、`review-maf-control`、`review-langgraph-control`、`representation-taxonomy`、`execution-semantics`、`product-mapping-critic`、`taxonomy-judge-r1`、`taxonomy-redteam-r2`、`consensus-synthesis-r2`、`doc-readiness-r2`、`review-temporal-surface`、`review-airflow-surface`、`review-maf-surface` 与 `review-langgraph-surface` subagent 输出 | 独立评审认为原页抽象层级“部分成立”；后续讨论进一步确认 DAG、workflow code、graph 都应先归入 authoring/control representation surface，真正差异在执行解释器、状态真源、恢复模型和副作用纪律；逐产品审查要求收紧 Temporal、Airflow、MAF 和 LangGraph 行，并在本轮最终审查中均无概念意见。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| 四者都属于多步状态化编排问题空间；DAG、workflow code、graph 和 workflow surface 都可视为 authoring/control representation surface，但比较不能停在表示形态，应继续比较执行解释器、状态真源、恢复模型和副作用纪律。 | 上方全部 source page；本次 session subagent 评审与调研。 | 这是综合判断，不是任何单一厂商文档的原话；过度抽象会掩盖产品运行语义差异。 |
| Temporal 的核心模式是 event-sourced deterministic replay；Activities 是副作用边界，Timer 是内部持久等待，Schedule 是独立外部启动规则。 | [Temporal Workflows 文档](../sources/temporal/workflows-docs.md)、[Temporal Workflow 确定性约束文档](../sources/temporal/workflow-deterministic-constraints-docs.md)、[Temporal Activities 文档](../sources/temporal/activities-docs.md)、[Temporal Timers and Start Delays 文档](../sources/temporal/timers-delays-docs.md)、[Temporal Schedule 文档](../sources/temporal/schedule-docs.md) | AI agent 只是可承载 workload pattern；Temporal Schedule 也不等同于 Airflow 的 DAG scheduler。 |
| Airflow 的核心模式是显式 DAG/task graph 控制规范，加上 scheduler 和 metadata DB 对 DagRun/TaskInstance 状态的解释与推进；dynamic mapping、asset scheduling 与 common.ai 扩展了同一 task graph 语义。 | [Airflow DAG 文档](../sources/apache-airflow/dags-docs.md)、[Airflow Scheduler 文档](../sources/apache-airflow/scheduler-docs.md)、[Airflow Dynamic Task Mapping 文档](../sources/apache-airflow/dynamic-task-mapping-docs.md)、[Airflow Asset Scheduling 文档](../sources/apache-airflow/asset-scheduling-docs.md)、[Airflow Common AI Provider 博客](../sources/apache-airflow/common-ai-provider-blog.md)、[Airflow Agentic Workloads 博客](../sources/apache-airflow/agentic-workloads-blog.md) | common.ai provider 是快速演进的增强层，不应当成 Airflow 核心语义已整体转向 agent runtime；Airflow 与 Temporal 的差异也不是“是否有 schedule/trigger/run”。 |
| Microsoft Agent Framework 更接近 agent framework 内的 explicit graph/functional workflow surfaces，Durable Extension 是可选 durable backend/integration hosting。 | [Microsoft Agent Framework Overview 文档](../sources/microsoft-agent-framework/overview-docs.md)、[Microsoft Agent Framework Workflows 概览](../sources/microsoft-agent-framework/workflows-overview-docs.md)、[Microsoft Agent Framework Functional Workflows 文档](../sources/microsoft-agent-framework/functional-workflows-docs.md)、[Microsoft Agent Framework WorkflowBuilder 文档](../sources/microsoft-agent-framework/workflow-builder-docs.md)、[Microsoft Agent Framework Durable Extension 文档](../sources/microsoft-agent-framework/durable-extension-docs.md) | functional API 明确 experimental，不能按统一 GA 处理；Durable Extension 不能外推为所有 surface 的默认语义。 |
| LangGraph 的核心模式是 checkpointed stateful graph runtime；checkpointer/store 与 interrupt/resume 共同支撑 thread-scoped graph state、cross-thread memory 和图/节点级暂停恢复。 | [LangGraph Overview 文档](../sources/langgraph/overview-docs.md)、[LangGraph Persistence 文档](../sources/langgraph/persistence-docs.md)、[LangGraph Interrupts 文档](../sources/langgraph/interrupts-docs.md)、[LangGraph Fault Tolerance 文档](../sources/langgraph/fault-tolerance-docs.md) | durability 是配置后的能力，不是无条件默认；store 不等于当前位置，fault tolerance 也不自动等价于 Temporal Activity 的副作用隔离。 |
| 控制流与 LLM/tool 执行应分层比较；LLM/tool 调用通常是 Activity/task/executor/node 内 payload，而不是自动成为控制抽象。 | [StateFlow 论文](../sources/arxiv/stateflow-2403-11322.md)、[GraphBit 论文](../sources/arxiv/graphbit-2605-13848.md)、Temporal/Airflow/MAF/LangGraph source pages。 | MAF 和 LangGraph 对 agent/workflow runtime 的原生建模程度更高，但也不能消除控制流与节点工作负载的分层。 |
| agent workflow 文献提供模式语言，但不能直接外推为四个产品的默认能力或成熟度保证。 | [Agent Workflow Survey 论文](../sources/arxiv/agent-workflow-survey-2508-01186.md)、[GraphFlow 论文](../sources/arxiv/graphflow-2605-22566.md)、[FlowSteer 论文](../sources/arxiv/flowsteer-2602-01664.md) | arXiv 论文包含预印本和系统论文，结论应作为研究趋势和概念补充，而不是产品成熟度证明。 |
