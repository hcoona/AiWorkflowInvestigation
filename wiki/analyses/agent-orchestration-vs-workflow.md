---
schema_version: 2
page_type: analysis
title: "Agent Orchestration 与传统 Workflow 的边界"
status: active
created: 2026-06-13
updated: 2026-06-13
summary: "区分 agent orchestration 与传统 workflow 的控制权、状态、恢复和治理边界。"
maintenance:
  edit_policy: update
validation:
  body_contract: analysis-answer-memo
tags:
  - workflow
  - agent-orchestration
  - ai-agents
---

## 问题

arXiv:2508.01186 的 agent workflow survey 把许多 agent
framework、产品和论文方法放在 workflow 维度上比较。
这容易造成一个误解：只要一个 agent framework 有 graph、chain、planner、
multi-agent role 或 tool call，就等同于传统 workflow engine。

本页回答一个更窄的问题：Agent Orchestration 与传统 Workflow 的边界在哪里？
这里的传统 Workflow 包括 Temporal、Apache Airflow、BPMN/case management
等以显式过程规范、调度、状态推进和恢复语义为核心的系统。
这里的 Agent Orchestration 指组织一个或多个 agent 的目标、上下文、工具、状态、
权限、预算、停止条件、评价和协作方式的运行时。

## 答案

明确结论：在抽象能力层面，Agent Orchestration 和传统 Workflow
没有不可跨越的本质区别。
如果一个传统 workflow 产品允许 agent 在受治理的边界内生成、选择或修改
workflow/plan，并把结果交给 engine 的历史、调度、版本、恢复和审计契约执行，
它就在能力上覆盖了 agent orchestration 的核心区域。
区别会退化为实现 substrate、first-class
API、治理模型、可观测性、恢复语义和产品成熟度，而不是“agent orchestration vs
workflow engine”的本体论差异。

以当前已调研产品看，Temporal、Airflow、Microsoft Agent Framework 和 LangGraph
基本都已经提供了构建这种形态所需的关键 primitives：
消息/更新、运行期工作集展开、定义版本演进、Run/thread 边界状态交接、
checkpoint/time-travel fork、reset/replay、graph migration/recompile、agent
executor 或 agent workload hosting。
但它们不一定都把“agent 动态改 workflow”包装成同一个 first-class 产品功能；
差异主要在这些 primitives 如何组合、是否官方推荐、是否有治理和迁移保护、
以及修改发生在 current run、新 run/thread、未来版本还是重新编译后的定义上。

因此，核心分界不是“有没有 LLM”“有没有 DAG”“是不是动态修改 workflow”“是不是多
agent”，而是：

> 运行期是否把实质性过程控制权委托给受约束的 agent policy。

“动态修改 workflow”本身不是分界线。
传统 workflow 也可以具备很强的动态演进能力：
消息驱动状态和路径变化、运行期工作集展开、定义版本升级、Run/thread
边界状态交接、checkpoint fork、reset/replay、backfill/clear 到新版本等。
这些能力不能因为产品术语不是“agent plan mutation”或“topology edit”
就被判定为能力不同。

更可靠的判断是 capability mapping：把各产品的术语先映射到同一抽象层级，
再比较改变过程的是谁、改变什么对象、何时生效、是否保留历史、
如何约束副作用、如何审计和恢复。
传统 Workflow 的控制中心是 workflow engine 可解释的过程规范和运行状态；
这些规范可以在设计期写好，也可以通过版本、消息、数据或外部输入演进，
但一旦进入执行语义，就由 engine 按它的历史、调度、状态和恢复契约接管。

Agent Orchestration 的控制中心是受约束的 agent policy。
orchestrator 提供目标、上下文、工具、权限、状态、记忆、预算、停止条件、
评价器和审计边界；agent
根据语义观察、工具反馈和任务目标在运行期生成、选择或修改子目标、步骤、
工具、协作者和恢复策略，并可把 workflow/plan
本身当成需要被生成、修订或替换的对象。
这是一种更高层的过程控制/过程生成能力，但它可以运行在传统 workflow engine 之上。

“过程控制权”不必一定改写整张全局流程图。
只要 agent 的选择会实质改变执行路径、副作用、工具顺序、子任务分解、协作者选择、
失败恢复或终止判断，就已经进入 agent orchestration 的核心区域。
相反，如果 LLM 只是分类、摘要、填参数或在预设 if/else 中给出数据，
后续状态推进仍由 workflow spec 决定，那仍是 workflow 中的 LLM workload。

### 分层区分

| 层级 | 传统 Workflow | Agent Orchestration |
| --- | --- | --- |
| 控制规范 | engine 可解释的过程规范：DAG、workflow code、状态机、case plan、版本化定义或运行期生成后被纳入 engine 契约的工作集。 | 目标、约束、工具、权限、评价标准与过程生成策略；路径、工作集或恢复动作可由 agent policy 运行期生成或修正。 |
| 执行解释器 | workflow engine 解释 DAG、状态机、workflow code、case plan、serialized definition 或 checkpoint/thread state。 | orchestrator 管理 agent 的观察、行动、反馈和重规划循环，并可把 workflow engine 当作 durable substrate。 |
| 状态真源 | workflow history、metadata DB、case state、业务记录。 | conversation state、agent memory、tool results、task board、checkpoint 和外部观察共同影响行为。 |
| 动态演进 | 消息更新、task/workset expansion、definition versioning、run/thread boundary handoff、reset/replay/fork、backfill/clear 等受限操作。 | agent 根据任务语义决定是否生成新计划、调整步骤、替换工具、引入协作者或把状态交给新的 workflow/plan。 |
| 恢复语义 | retry、timeout、resume、replay、compensation、reset、checkpoint fork 或新 run/thread 恢复。 | 除工程恢复外，还可能诊断失败、换工具、改计划、请求澄清或降级目标。 |
| 副作用边界 | activity、operator、task 或 human task 通常是预定义副作用边界。 | tool call、API、文件、浏览器、代码执行等行动空间可由 agent 运行期选择，因此更依赖权限、预算、审批和沙箱。 |
| 治理与审计 | 审计步骤、审批人、时间、输入输出、重试和状态转移。 | 还需审计 prompt、model/version、tool schema、tool choice、观察、handoff、memory 和评价结果。 |
| 优化目标 | 稳定性、吞吐、SLA、成本、资源利用、可预测性。 | 任务成功率、适应性、推理质量、少人工干预、工具/记忆/协作结构质量。 |

### Agent policy 与规则、优化器、规划器不同

agent policy 不是所有“运行期决策”的同义词。
规则引擎在设计期枚举条件和动作；优化器在明确变量、目标函数和约束内求解；
传统规划器在形式化 action/operator、前置条件和效果模型中生成计划。
这些都可以让 workflow 很动态，但分支空间和决策模型通常仍由工程师显式建模。

Agent Orchestration 的强信号是 agent policy
根据语义上下文、开放输入、记忆、观察和工具反馈，
在运行期解释目标并生成或修改行动序列。
planner 可以是 agent 的一部分，但 planner 本身不是充分条件。
如果 planner 只在显式建模空间内生成可执行计划，它更接近 adaptive workflow 或
planning workflow；如果 policy 能根据观察修改子目标、工具和恢复策略，才更接近
agent orchestration。

### 不是充分条件的信号

- 有 LLM：Airflow task 调用 LLM 做分类仍是 workflow。
- 有 DAG 或 graph：DAG/graph 是控制表示面，不自动决定运行语义。
- 有动态分支：workflow 可以有条件分支、dynamic mapping、case routing。
- 有 planner：planner 可以只是 workflow 的一个节点。
- 有多 agent role：固定串行的 researcher/writer/reviewer 可能只是角色化
  pipeline。
- 有 tool call：固定工具链是 workflow；运行期自主选择工具才是 agentic 信号。
- 有 stochastic output：非确定性输出不等于 agent orchestration。

### 更精细的谱系

| 类型 | 判别特征 | 示例判断 |
| --- | --- | --- |
| 静态 workflow | 步骤和转移主要由设计期定义。 | 固定 ETL、固定审批、固定 DAG。 |
| 动态或规则驱动 workflow | 运行期可分支、展开或路由，但分支规则被显式建模。 | Airflow Dynamic Task Mapping、BPMN gateway、规则引擎 case routing。 |
| 演进型 workflow | workflow 可通过定义版本、run/thread 边界状态交接、checkpoint fork、reset/replay、clear/backfill 等机制演进，但这些操作仍由 engine 契约解释。 | Temporal Continue-As-New/Worker Versioning、Airflow DagVersion/DAG Bundles、LangGraph graph migration/time travel、MAF checkpoint restore。 |
| LLM-routed workflow | LLM 在有限枚举路径中做分类或路由。 | 固定图里 LLM 选择预设 conditional edge；属于弱 agentic workflow。 |
| single-agent tool orchestration | 单 agent 在约束内选择工具、顺序、恢复动作。 | 编码 agent 在 CI task 内自主修复；内层是 agent orchestration。 |
| governed agent orchestration | agent 选择子目标、工具、协作者和恢复策略，并受权限、预算、停止条件和审计约束。 | 生产级 research/coding/support agent runtime。 |
| multi-agent orchestration | 多 agent 角色之间有 handoff、协作、冲突处理和评价机制。 | AutoGen/CrewAI/Swarm 风格系统，前提是角色不是固定脚本顺序。 |
| durable agent orchestration | agent loop 由 durable workflow/runtime 承载，具备恢复、队列、审计和持久状态。 | Temporal 或 Durable Task 承载 agent loop；LangGraph/MAF 在特定 durable backend 下的混合形态。 |

### 双向收敛，但不是概念合并

传统 workflow 不只是“接近”动态修改 workflow；
它们已经在各自抽象层级上拥有一组可验证的 workflow 演进能力。
重新判断后，问题不再是“传统 workflow 有没有动态修改能力”，答案是有；
问题是这些修改能力由什么控制源触发，以及修改对象是在 engine
契约内的状态、工作集、定义版本、run/thread 边界，还是由 agent policy
作为高层过程策略主动生成和改写。

这是一种双向收敛。
它不是说所有产品实现已经完全等同；而是说一旦传统 workflow 产品把 agent-driven
workflow generation/modification 纳入受治理能力面，“传统 workflow”和“agent
orchestration”就不再有本质能力边界，只剩具体运行时契约和产品成熟度差异。
Temporal 的动态 agent 示例说明，agent loop 可以被 durable workflow 承载；
但非确定性的模型和工具调用仍要放在 Activity 或等价副作用边界中。
Airflow 的 Dynamic Task Mapping 和 agentic workload 示例说明，scheduler
可以按上游数据在运行期展开 task copies，并把 LLM/agent workload
放进可观察、可重试的 task graph；但这仍是 DAG/task 语义里的受控展开，不是 agent
任意改写 DAG 定义。

因此，“动态修改 workflow”可以作为边界的直觉入口，
但不能把产品术语是否一一对应当成能力差异的依据。
`Workflow Execution`、`DagRun`、`thread`、`graph`、`checkpoint`、`DAG version`
只是证据定位对象；真正要比较的是同一抽象层级上的能力：
谁有权改变过程结构，改变的是控制规格、待执行工作集、状态中的计划、
部署版本还是新 run/thread 的输入，
改变何时生效，是否保留历史，是否仍受确定性、审计、权限和副作用边界约束。

在这个判准下，如果 workflow engine 展开任务、路由 case、重试失败步骤、
把状态交给新 run、让未来 run 使用新版本定义、或从 checkpoint fork 出新路径，
它已经具备对应抽象层级的 workflow 演进/修改能力。
只有当 agent policy 被授权把这些能力当作行动空间的一部分，
根据观察重新生成或修订计划、插入步骤、换工具链、
改变恢复策略并影响副作用边界时，才构成 agent orchestration
这一更高抽象层级的核心能力。

四个产品的第二轮 GPT-5.5 复查与对抗审查在这个新判准下应重新解释：
Temporal、Airflow、MAF 和 LangGraph 都有 workflow 演进能力，只是能力落点不同。
Temporal 主要落在 Event History、message/update、Continue-As-New、Reset 和
worker/code versioning；Airflow 落在 DAG/bundle/DagVersion、scheduler-managed
mapped tasks、DagRun reconciliation、clear/backfill；MAF 落在
builder/build、functional control flow、checkpoint restore/migration 语境和
durable hosting；LangGraph 落在 compiled graph
内动态路由、checkpoint/time-travel fork、graph migration/recompile 和 Functional
API 运行轨迹。
这些都不能被术语差异抹掉。
未被当前证据支持的是更强的命题：
任一系统都允许不受其历史、状态、版本和恢复契约约束地任意改写正在执行对象的未来结构。

这里需要避免另一个过度收紧：修改 workflow 本来就不应改变历史。
以 Temporal 为例，Continue-As-New 正是把最新相关状态传给同一 execution chain
中的新 Workflow Execution；新 execution 使用相同 Workflow Id、不同 Run
Id，并拥有新的 Event History。
这不是“原地改写当前 history”，但确实可以作为 Run 边界状态交接/升级点：旧 run
保持可审计，新 run 承接状态并可在新代码或新计划语义下继续。
因此更精确的限制不是“Temporal 不能更改 workflow”，而是“Temporal 的修改能力
必须映射到它的 Event History、run boundary、worker routing 和 replay
抽象上判断；不能因为 Temporal 没有 DAG/topology 术语就说它没有等价的 workflow
演进能力，也不能因为它有 Continue-As-New 就说它能无约束改写当前 execution”。

| 产品 | 重新映射后的 workflow 演进能力 | Agent Orchestration 判断 |
| --- | --- | --- |
| Temporal | 消息驱动当前 run 状态/路径改变；Run 边界状态交接/升级；历史前缀重放式修复；worker/code version routing。这些是受 Event History、deterministic replay 和 worker routing 约束的 workflow 演进能力。 | Temporal 不是因为没有 DAG/topology 术语而缺少 workflow 修改能力；只有当 agent policy 被授权决定何时 signal/update、continue-as-new、选择新计划或触发外部 replacement 时，才是 agent orchestration 层。 |
| Apache Airflow | 部署/解析期定义版本演进；未来 DagRun 使用新定义；当前 DagRun 内 scheduler-managed workset expansion；既有 DagRun 与当前 DAG 视图的受控 reconciliation。 | Airflow 的动态能力是 workflow-engine 能力，不应直接等同 agent plan mutation；只有当 agent 负责生成/选择 DAG、触发清理回填、决定后续工作集或改变恢复策略时，才上升到 agent orchestration。 |
| Microsoft Agent Framework | 应用层 build/create 新 workflow definition/instance；functional control flow；agent task replanning；checkpoint 恢复/迁移语境；Durable Extension hosting。 | MAF 同时有 workflow 和 agent surfaces；判断要看当前改变由 builder/code/runtime contract 解释，还是由 agent policy 生成下一步过程。不能用“没有任意 graph migration”否定动态 workflow 能力。 |
| LangGraph | compiled graph 内动态路由/动态并行；state/checkpoint fork 对未来路径的改变；受限 graph migration/recompile；Functional API 的运行轨迹生成。 | LangGraph 的 time travel 和 graph migration 是 workflow 演进能力；如果 agent 在状态中生成计划、决定工具和下一步，并通过这些机制改变未来路径，才是 agent orchestration 层。 |

### 边界案例

- **Temporal 中嵌 Agent**：
  外层仍是负责 durable execution、retry、timer、history 和 Activity 边界的
  workflow engine，内层 Activity 或 child workflow 可以运行 agent
  orchestration，因此分类必须说明观察边界。
- **Airflow DAG 调 LLM**：如果 LLM 只是 task/operator 的 payload，控制流仍由
  DAG、scheduler 和 metadata DB 推进；这不是 agent orchestration。
- **LangGraph 固定图 + LLM conditional edge**：
  如果 LLM 只在预设边中选路，是 LLM-routed workflow 或 agentic workflow；
  如果 agent 能拆任务、改计划、选择工具并根据反馈重规划，才进入 agent
  orchestration。
- **Dify/Flowise 可视化 flow**：
  prompt chain、固定节点和固定路由更像低代码 workflow；
  agent 模式中模型自主选工具或路径时，才向 agent orchestration 移动。
- **AutoGen/CrewAI/OpenAI Swarm**：
  框架层面以 agent、message、handoff 和 tool choice 为中心，通常偏 agent
  orchestration；
  但固定脚本式 group chat 可以退化为 agent-shaped workflow。
- **Microsoft Agent Framework Durable Extension**：
  durable backend 可以给 agent/workflow surface 增加 workflow 能力；
  这说明 agent orchestrator 可以具备 durable execution substrate，
  但不能把所有 core workflow surface 都等同于传统 workflow engine。
- **Case management / BPMN human task**：
  人可以运行期选择任务或审批结果，但流程控制通常由 case plan、event 和 gateway
  推进；
  只有 agent 被授权实质选择任务、工具、子目标和恢复策略时，
  才进入 agent orchestration。

### 判别问题集

1. 正在比较的是哪一层能力：控制规格、运行状态、待执行工作集、定义版本、
   run/thread 边界、checkpoint fork，还是 agent policy 生成的计划？
2. 改变过程的是谁：workflow engine 的规则、用户/API、部署系统、数据输入，
   还是 agent policy？
3. 改变何时生效：当前 step、当前 run 的后续路径、新 run/thread、未来 DagRun、
   新 workflow instance，还是重新编译/部署后的 graph？
4. 改变是否保留旧历史，还是会试图改写已经记录的 history/checkpoint/metadata？
5. 改变后的执行是否仍受 engine 的确定性、调度、版本、权限和恢复契约约束？
6. 去掉 agent policy 后，系统是否仍能按同样过程推进？
7. agent 是否能选择工具、顺序、子任务、协作者或终止条件？
8. agent 的选择是否会改变执行路径、副作用或恢复策略？
9. 失败后是 engine 按 retry policy 重试，还是 agent 观察失败并重规划？
10. LLM 输出是数据，还是过程控制决策？
11. graph/flow 是约束边界，还是主要控制源？
12. durable execution 是主要控制逻辑，还是 agent loop 的执行保障？
13. 审计对象只是 workflow transition，还是还包括 prompt、model、tool choice、
    memory、handoff 和评价结果？

## 影响

这个区分会改变后续 wiki 的分类口径。
arXiv:2508.01186 的 survey 可以作为 agent workflow / agent orchestration 研究
taxonomy 的来源，但不能把其中多数 agent framework 直接当成传统 workflow engine
比较。
对 Temporal、Airflow、LangGraph、Microsoft Agent Framework 等系统的比较，
应继续先做 capability mapping：分清 authoring/control representation
surface、execution interpreter、state source、recovery semantics、side-effect
boundary、governance/audit，以及该能力是 engine 契约内的 workflow 演进，还是
agent policy 驱动的过程生成。

后续写作中，应避免把“agent framework 的 flow”直接写成 workflow engine。
更安全的写法是：agent framework 可能提供 workflow-like authoring surface；
只有当它具备或委托给 durable execution、scheduling、retry、policy、audit
等运行时契约时，才进入 workflow engine 的工程范畴。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| wiki | [工作流概念比较](workflow-concepts-comparison.md) | 已有四系统比较，区分控制表示面、执行解释器、状态真源、恢复模型、副作用纪律和时间/调度模型。 |
| wiki | [arXiv 2508.01186 Agent Workflow Survey](../sources/arxiv/agent-workflow-survey-2508-01186.md) | agent workflow 综述、三层框架、能力/架构双轴和 workflow modes。 |
| wiki | [Temporal 动态 AI Agent 博客](../sources/temporal/dynamic-ai-agents-blog.md)、[Temporal Message Passing 文档](../sources/temporal/message-passing-docs.md)、[Temporal Continue-As-New 文档](../sources/temporal/continue-as-new-docs.md)、[Temporal Reset 文档](../sources/temporal/reset-docs.md)、[Temporal Workflow Versioning 文档](../sources/temporal/workflow-versioning-docs.md)、[Temporal Worker Versioning 文档](../sources/temporal/worker-versioning-docs.md) | 支撑 Temporal 的 durable agent loop、message-driven state change、Run 边界状态交接/升级点、Reset、受控 versioning 与 worker routing 边界。 |
| wiki | [Airflow DAG File Processing 文档](../sources/apache-airflow/dagfile-processing-docs.md)、[Airflow DAG Bundles 文档](../sources/apache-airflow/dag-bundles-docs.md)、[Airflow DAG Serialization 文档](../sources/apache-airflow/dag-serialization-docs.md)、[Airflow Dynamic DAG Generation 文档](../sources/apache-airflow/dynamic-dag-generation-docs.md)、[Airflow Dynamic Task Mapping 文档](../sources/apache-airflow/dynamic-task-mapping-docs.md)、[Airflow DagRun verify_integrity 源码](../sources/apache-airflow/dagrun-verify-integrity-source.md)、[Airflow Common AI LLMBranchOperator 文档](../sources/apache-airflow/common-ai-llm-branch-docs.md)、[Airflow Agentic Workloads 博客](../sources/apache-airflow/agentic-workloads-blog.md) | 支撑 Airflow 的解析/部署期 revision、serialized DAG/DagVersion、scheduler-managed runtime task expansion、既有 DagRun 受控 reconciliation、LLM-routed branching 与 agentic workload hosting 边界。 |
| wiki | [Microsoft Agent Framework WorkflowBuilder 文档](../sources/microsoft-agent-framework/workflow-builder-docs.md)、[Microsoft Agent Framework Workflow State 文档](../sources/microsoft-agent-framework/state-docs.md)、[Microsoft Agent Framework Workflow Checkpoints 文档](../sources/microsoft-agent-framework/checkpoints-docs.md)、[Microsoft Agent Framework Functional Workflows 文档](../sources/microsoft-agent-framework/functional-workflows-docs.md)、[Microsoft Agent Framework Durable Extension 文档](../sources/microsoft-agent-framework/durable-extension-docs.md) | 支撑 MAF builder/build 边界、workflow immutability、checkpoints、functional control flow 与 Durable Task-backed hosting 边界。 |
| wiki | [LangGraph Graph API 文档](../sources/langgraph/graph-api-docs.md)、[LangGraph Graph Migrations 文档](../sources/langgraph/graph-migrations-docs.md)、[LangGraph StateGraph Compile 源码](../sources/langgraph/stategraph-compile-source.md)、[LangGraph Time Travel 文档](../sources/langgraph/time-travel-docs.md)、[LangGraph Functional API 文档](../sources/langgraph/functional-api-docs.md)、[LangGraph Persistence 文档](../sources/langgraph/persistence-docs.md)、[LangGraph Agent Server 文档](../sources/langgraph/agent-server-docs.md) | 支撑 LangGraph compiled graph、graph migration/recompile、dynamic routing/fan-out、checkpoint/time travel、Functional API runtime-generated execution graph 与部署边界。 |
| wiki | [Temporal Workflows 文档](../sources/temporal/workflows-docs.md)、[Airflow Scheduler 文档](../sources/apache-airflow/scheduler-docs.md)、[LangGraph Graph API 文档](../sources/langgraph/graph-api-docs.md)、[Microsoft Agent Framework Durable Extension 文档](../sources/microsoft-agent-framework/durable-extension-docs.md) | 支撑传统 workflow engine、graph runtime 与 durable extension 的工程边界示例。 |
| session | 过去 Copilot CLI session `1a589d1a-96de-4db1-9e0c-e715ed58a7a4` 中，用户请求深入区分 Temporal、Airflow、Microsoft Agent Framework 与 LangGraph 的 workflow 功能，并继续 arXiv research。 | 该历史调研把 Temporal/Airflow 与 MAF/LangGraph 的 workflow 语义拆成控制表示面、执行解释器、状态真源、恢复模型和副作用纪律，并把 agent workflow 文献进一步细分为状态机控制、确定性图引擎、服务端图管理和学习式 workflow 生成。 |
| user | [`raw/00-human-original-input/2026-06-11-ai-workflow-initial-ideas.md`](../../raw/00-human-original-input/2026-06-11-ai-workflow-initial-ideas.md) | 用户原始问题已经包含 AI 生成 Workflow 计划、执行 Workflow 计划、动态判断执行情况并调整 Workflow 计划的方向。 |
| session | 当前 Copilot CLI session `7dd4dcd2-136d-4756-af15-2a4dd9cb2765` 中，用户于 2026-06-12T20:25:52-07:00 请求 GPT-5.5 多 subagent 讨论；`g55-concept-modeler`、`g55-concept-critic`、`g55-engineering-taxonomy`、`g55-consensus`、`g55-devil-advocate` 输出。 | 多路 GPT-5.5 讨论收敛出“运行期实质过程控制权是否委托给受约束 agent policy”这一判准，并由反方代理细化出谱系而非二分法。 |
| session | 当前 Copilot CLI session `7dd4dcd2-136d-4756-af15-2a4dd9cb2765` 中，用户于 2026-06-12T20:51:00-07:00 要求每产品 GPT-5.5 深挖和对抗审查；`g55-temporal-dynamic-research/review`、`g55-airflow-dynamic-research/review`、`g55-maf-dynamic-research/review`、`g55-langgraph-dynamic-research/review` 输出。 | 第一轮产品专项调研确认四者都有受控动态能力，但需避免把“不能原地改写历史/拓扑”误写成“不能修改 workflow”。 |
| session | 当前 Copilot CLI session `7dd4dcd2-136d-4756-af15-2a4dd9cb2765` 中，用户于 2026-06-12T21:08:59-07:00 指出 Continue-As-New 反例，并要求每产品 GPT-5.5 复查与对抗审查；`g55-temporal-revisit/review`、`g55-airflow-revisit/review`、`g55-maf-revisit/review`、`g55-langgraph-revisit/review` 输出。 | 第二轮审查全部要求 REVISE：Temporal 应写成 Run 边界状态交接/升级点；Airflow 应写成 DAG/Bundle/DagVersion 与受控 DagRun reconciliation；MAF 应写成应用层重新 build/create workflow 与 checkpoint 兼容性边界；LangGraph 应写成 graph migration/recompile、state fork 和 Functional API trace graph，而非原地 topology mutation。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| 在抽象能力层面，Agent Orchestration 与传统 Workflow 没有不可跨越的本质区别；如果传统 workflow 产品支持 agent 在受治理边界内动态生成或修改 workflow/plan，并由 engine 契约执行，它就在能力上覆盖 agent orchestration 的核心区域。 | Temporal、Airflow、MAF、LangGraph 新增 source pages；两轮产品专项调研和审查；[工作流概念比较](workflow-concepts-comparison.md)。 | 这里说的是抽象能力等价，不是产品 API、运行时实现、推荐架构或成熟度完全相同。 |
| 当前调研的 Temporal、Airflow、MAF 和 LangGraph 基本都已提供构建 agent 动态改 workflow 所需的关键 primitives，但 first-class 程度和治理保护不同。 | Temporal、Airflow、MAF、LangGraph 新增 source pages；两轮产品专项调研和审查。 | “基本支持”不应理解为都支持同一个无约束 live topology edit API；更准确地说，是可以通过各自的受限 workflow 演进机制组合出该能力。 |
| 动态修改 workflow 不是 Agent Orchestration 与传统 Workflow 的分界线；传统 workflow 也可以具备消息更新、运行期 workset expansion、定义版本演进、run/thread 边界状态交接、reset/replay/fork 等 workflow 演进能力。 | Temporal、Airflow、MAF、LangGraph 新增 source pages；两轮产品专项调研和审查；[工作流概念比较](workflow-concepts-comparison.md)。 | 这些能力必须按同一抽象层级比较，不能由术语是否对应推出能力是否存在。 |
| Agent Orchestration 与传统 Workflow 的核心分界是运行期是否把高层过程控制/过程生成权委托给受约束 agent policy。 | session 证据单元；[工作流概念比较](workflow-concepts-comparison.md)。 | 这是综合概念判准，不是某个厂商或论文的标准定义；agent policy 可以运行在传统 workflow engine 之上。 |
| LLM、DAG、动态分支、planner、多 agent role、tool call 都不是充分条件。 | session 证据单元；[arXiv 2508.01186 Agent Workflow Survey](../sources/arxiv/agent-workflow-survey-2508-01186.md)。 | 这些信号在具体系统中可能是强提示，但仍需看控制权、状态和恢复语义。 |
| 传统 workflow 可以承载 agent，agent orchestrator 也可以具备 workflow 能力；二者应按观察边界拆开。 | Temporal、Airflow、LangGraph 和 Microsoft Agent Framework source pages；[工作流概念比较](workflow-concepts-comparison.md)。 | 混合系统会随部署方式变化，不能只按产品名分类。 |
| 传统 workflow 的动态/演进能力是真实能力，不应被降级为“只是术语不同”；它们通常通过消息、状态交接、新 run/thread、部署版本、受控 task expansion、checkpoint fork 或应用层新定义实现，而不是改写既有历史。 | Temporal、Airflow、MAF、LangGraph source pages；历史 session 证据单元；本轮产品专项调研和审查。 | 这是当前证据下的概括；不同厂商后续可能提供更强的 governed authoring 或 migration 能力。 |
| 判断 Agent Orchestration 与传统 Workflow 的差异必须做 capability mapping：产品术语只是证据入口，不能因为对象名不同就推出能力不同。 | 用户于 2026-06-12T21:41:44-07:00 的纠正；本页产品矩阵和 source pages。 | 能力映射必须保持抽象层级一致，分别比较控制权、改变对象、生效时点、历史约束、审计/权限和副作用边界。 |
| 四个被审产品均支持某种 workflow 修改或演进能力，但当前一手证据不支持“直接改写已经记录的历史或同一个正在执行对象的未来工作结构”这个强结论。 | Temporal、Airflow、MAF、LangGraph 新增 source pages；两轮产品专项调研和审查；[Temporal Continue-As-New 文档](../sources/temporal/continue-as-new-docs.md)。 | 如果把“修改”限定为原地任意 topology mutation，结论是否定的；如果把“修改”扩展为 run-boundary state handoff、future-run DAG version、checkpoint fork、new workflow definition 或 graph migration，则结论是肯定的。 |
| 更精细的谱系比简单二分更安全：静态 workflow、动态/规则 workflow、演进型 workflow、LLM-routed workflow、single-agent tool orchestration、governed/multi-agent/durable agent orchestration。 | session 证据单元；本页谱系表。 | 谱系是本 wiki 的工作性分类，后续可随更多证据调整。 |
