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

核心分界不是“有没有 LLM”“有没有 DAG”“是不是动态”“是不是多 agent”，而是：

> 运行期是否把实质性过程控制权委托给受约束的 agent policy。

传统 Workflow 的控制中心是显式过程模型。
步骤、依赖、条件、重试、补偿、人工审批、队列、调度和副作用边界主要在设计期定义。
运行时可以有动态分支、人工任务、LLM 调用和工具调用，但解释器或 workflow engine
仍按既定规则推进状态。

Agent Orchestration 的控制中心是受约束的 agent policy。
orchestrator 提供目标、上下文、工具、权限、状态、记忆、预算、停止条件、
评价器和审计边界；agent
根据观察结果在运行期选择或修改子目标、步骤、工具、协作者和恢复策略，
并可根据反馈重规划。

“过程控制权”不必一定改写整张全局流程图。
只要 agent 的选择会实质改变执行路径、副作用、工具顺序、子任务分解、协作者选择、
失败恢复或终止判断，就已经进入 agent orchestration 的核心区域。
相反，如果 LLM 只是分类、摘要、填参数或在预设 if/else 中给出数据，
后续状态推进仍由 workflow spec 决定，那仍是 workflow 中的 LLM workload。

### 分层区分

| 层级 | 传统 Workflow | Agent Orchestration |
| --- | --- | --- |
| 控制规范 | 设计期显式定义步骤、依赖、条件和失败策略。 | 设计目标、约束、工具、权限、评价标准；路径可运行期生成或修正。 |
| 执行解释器 | workflow engine 解释 DAG、状态机、workflow code 或 case plan。 | orchestrator 管理 agent 的观察、行动、反馈和重规划循环。 |
| 状态真源 | workflow history、metadata DB、case state、业务记录。 | conversation state、agent memory、tool results、task board、checkpoint 和外部观察共同影响行为。 |
| 恢复语义 | retry、timeout、resume、replay、compensation。 | 除工程恢复外，还可能诊断失败、换工具、改计划、请求澄清或降级目标。 |
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
| LLM-routed workflow | LLM 在有限枚举路径中做分类或路由。 | 固定图里 LLM 选择预设 conditional edge；属于弱 agentic workflow。 |
| single-agent tool orchestration | 单 agent 在约束内选择工具、顺序、恢复动作。 | 编码 agent 在 CI task 内自主修复；内层是 agent orchestration。 |
| governed agent orchestration | agent 选择子目标、工具、协作者和恢复策略，并受权限、预算、停止条件和审计约束。 | 生产级 research/coding/support agent runtime。 |
| multi-agent orchestration | 多 agent 角色之间有 handoff、协作、冲突处理和评价机制。 | AutoGen/CrewAI/Swarm 风格系统，前提是角色不是固定脚本顺序。 |
| durable agent orchestration | agent loop 由 durable workflow/runtime 承载，具备恢复、队列、审计和持久状态。 | Temporal 或 Durable Task 承载 agent loop；LangGraph/MAF 在特定 durable backend 下的混合形态。 |

### 双向收敛，但不是概念合并

传统 workflow 确实在增加接近“动态修改 workflow”的能力。
但更准确的说法是：传统 workflow engine 正在把 agentic planning、runtime
expansion 和 LLM/tool payload 纳入受控执行边界；agent orchestration framework
则在补 durability、checkpoint、queue、audit 和 policy 等 workflow-engine 能力。

这是一种双向收敛，而不是二者已经等同。
Temporal 的动态 agent 示例说明，agent loop 可以被 durable workflow 承载；
但非确定性的模型和工具调用仍要放在 Activity 或等价副作用边界中。
Airflow 的 Dynamic Task Mapping 和 agentic workload 示例说明，scheduler
可以按上游数据在运行期展开 task copies，并把 LLM/agent workload
放进可观察、可重试的 task graph；但这仍是 DAG/task 语义里的受控展开，不是 agent
任意改写 DAG 定义。

因此，“动态修改 workflow”可以作为边界的直觉入口，但需要再问修改发生在哪一层：
如果是 workflow engine 按预定义规则展开任务、路由 case 或重试失败步骤，这是动态
workflow；如果是 agent policy 根据观察重新生成或修订计划、插入步骤、换工具链、
改变恢复策略并影响副作用边界，这才是 agent orchestration 的核心能力。

四个产品的第二轮 GPT-5.5 复查与对抗审查把结论再次收紧：如果把“动态修改
workflow”宽泛理解为运行期状态、路径、任务实例、计划数据、部署定义或新 run/thread
会变化，四者都有动态能力；
如果严格理解为“直接改写已经记录的历史或同一个正在执行对象的拓扑”，
当前一手证据都不支持。

这里需要避免另一个过度收紧：修改 workflow 本来就不应改变历史。
以 Temporal 为例，Continue-As-New 正是把最新相关状态传给同一 execution chain
中的新 Workflow Execution；新 execution 使用相同 Workflow Id、不同 Run
Id，并拥有新的 Event History。
这不是“原地改写当前 history”，但确实可以作为 Run 边界状态交接/升级点：旧 run
保持可审计，新 run 承接状态并可在新代码或新计划语义下继续。
因此更精确的限制不是“Temporal 不能更改 workflow”，而是“Temporal 不支持绕过 Event
History/replay 约束去原地任意改写当前 execution 的定义或拓扑”。

| 产品 | 已确认的动态能力 | 不应误写成 |
| --- | --- | --- |
| Temporal | Signals/Updates/async handlers 通过已部署 handler 改变当前 run 状态和后续路径；Continue-As-New 是显式、应用定义的 Run 边界状态交接/升级点；Reset 复制历史前缀并创建新 run；Patching/GetVersion 与 Worker Versioning/Build ID routing 支持受限代码演化和任务路由；官方 agent 示例把 agent loop 放进 deterministic workflow harness，并把 LLM/tool 调用放到 Activities。 | 原地改写当前 Workflow Execution 的 Event History 或已回放定义；绕过 deterministic replay 的 plan mutation；把 Continue-As-New、Reset、dynamic handler 或 worker routing 当成无约束自修改 workflow。 |
| Apache Airflow | DAG file/bundle refresh、Serialized DAG、DagVersion 和 Dynamic DAG Generation 支持部署/解析期 workflow revision 和未来 DagRun topology change；Dynamic Task Mapping 在当前 DagRun 内受限展开 mapped TaskInstances；`DagRun.verify_integrity`、clear latest version 和 backfill 可形成受控 reconciliation；LLMBranchOperator/AgentOperator 是预定义路径内路由或 task 内 agent loop。 | 运行中 task/agent 任意原地改写当前 DagRun 的 DAG definition；把 versioned bundle、serialized DAG 刷新、mapped task expansion 或 `verify_integrity` 当成无约束 DAG 自修改。 |
| Microsoft Agent Framework | `WorkflowBuilder`、declarative YAML/dict 和 Python/Functional workflow code 可创建新的 workflow definition/instance；Functional workflow 用原生控制流表达动态路径；handoff、group chat、Magentic 和 agent executor 支持 agent task replanning；checkpoints 支持暂停/恢复/迁移场景；Durable Extension 提供 durable hosting。 | 已运行 graph workflow 由 agent 任意插入/删除节点或边；把应用层重新 build/create workflow 写成官方运行中 graph migration；把 checkpoint 恢复写成自动 topology migration。 |
| LangGraph | 编译图内支持 conditional edges、`Command.goto/update`、`Send`、subgraphs 和动态 fan-out；time travel/update_state/checkpoint fork 可修改 state 中的计划数据并改变后续路径；graph migrations/recompile 允许已有 thread 在新 graph definition 下受限恢复；Functional API 可由 Python 控制流生成运行轨迹/隐式执行图。 | 正在执行的同一个 compiled graph object 可由 agent 任意增删节点/边；把 state fork、Functional API trace graph、assistant config versioning 或 graph migration 写成原地 topology mutation。 |

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

1. 去掉 agent policy 后，系统是否仍能按同样过程推进？
2. 下一步由谁决定：流程模型、规则、人，还是 agent policy？
3. agent 是否能选择工具、顺序、子任务、协作者或终止条件？
4. agent 的选择是否会改变执行路径、副作用或恢复策略？
5. 所有分支是否已在设计期显式枚举？
6. 失败后是 engine 按 retry policy 重试，还是 agent 观察失败并重规划？
7. LLM 输出是数据，还是过程控制决策？
8. graph/flow 是约束边界，还是主要控制源？
9. durable execution 是主要控制逻辑，还是 agent loop 的执行保障？
10. 审计对象只是 workflow transition，还是还包括 prompt、model、tool choice、
    memory、handoff 和评价结果？

## 影响

这个区分会改变后续 wiki 的分类口径。
arXiv:2508.01186 的 survey 可以作为 agent workflow / agent orchestration 研究
taxonomy 的来源，但不能把其中多数 agent framework 直接当成传统 workflow engine
比较。
对 Temporal、Airflow、LangGraph、Microsoft Agent Framework 等系统的比较，
应继续先分清 authoring/control representation surface、execution interpreter、
state source、recovery semantics、side-effect boundary 和 governance/audit。

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
| Agent Orchestration 与传统 Workflow 的核心分界是运行期是否把实质性过程控制权委托给受约束 agent policy。 | session 证据单元；[工作流概念比较](workflow-concepts-comparison.md)。 | 这是综合概念判准，不是某个厂商或论文的标准定义。 |
| LLM、DAG、动态分支、planner、多 agent role、tool call 都不是充分条件。 | session 证据单元；[arXiv 2508.01186 Agent Workflow Survey](../sources/arxiv/agent-workflow-survey-2508-01186.md)。 | 这些信号在具体系统中可能是强提示，但仍需看控制权、状态和恢复语义。 |
| 传统 workflow 可以承载 agent，agent orchestrator 也可以具备 workflow 能力；二者应按观察边界拆开。 | Temporal、Airflow、LangGraph 和 Microsoft Agent Framework source pages；[工作流概念比较](workflow-concepts-comparison.md)。 | 混合系统会随部署方式变化，不能只按产品名分类。 |
| 传统 workflow 正在增加动态/agentic 能力，但通常通过消息、状态交接、新 run/thread、部署版本、受控 task expansion 或应用层新定义来实现，而不是改写既有历史。 | Temporal、Airflow 新增 source pages；历史 session 证据单元；本轮产品专项调研和审查。 | 这是当前证据下的概括；不同厂商后续可能提供更强的 governed authoring 或 migration 能力。 |
| 四个被审产品均支持某种 workflow 修改或演进能力，但当前一手证据不支持“直接改写已经记录的历史或同一个正在执行对象的拓扑”这个强结论。 | Temporal、Airflow、MAF、LangGraph 新增 source pages；两轮产品专项调研和审查；[Temporal Continue-As-New 文档](../sources/temporal/continue-as-new-docs.md)。 | 如果把“修改”限定为原地任意 topology mutation，结论是否定的；如果把“修改”扩展为 run-boundary state handoff、future-run DAG version、checkpoint fork、new workflow definition 或 graph migration，则结论是肯定的。 |
| 更精细的谱系比简单二分更安全：静态 workflow、动态/规则 workflow、LLM-routed workflow、single-agent tool orchestration、governed/multi-agent/durable agent orchestration。 | session 证据单元。 | 谱系是本 wiki 的工作性分类，后续可随更多证据调整。 |
