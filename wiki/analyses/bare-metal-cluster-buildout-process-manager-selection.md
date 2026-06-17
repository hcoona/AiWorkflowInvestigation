---
schema_version: 2
page_type: analysis
title: "裸金属 Cluster Buildout 的 Process Manager 平台选型"
status: active
created: 2026-06-16
updated: 2026-06-17
summary: "比较 Temporal、Azure Durable Functions、Microsoft Agent Framework Durable Workflow Extension、Apache Airflow 与 LangGraph 承载裸金属 Cluster Buildout 主过程管理职责的边界。"
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

## 决策

如果目标是新建裸金属 Cluster Buildout 的主 process manager，
Temporal 应作为核心资源过程建模的主 baseline 和 reference architecture 强锚点。
这个判断不是最终采购排名，也不是说 Temporal 已经在运维成本、组织既有栈、
云托管便利性、UI 成熟度或供应商支持上胜出；它只判断 runtime 的一手对象
是否适合承载裸金属 buildout 的长期资源过程控制路径。

Azure Durable Functions / Durable Task 不应被 Temporal-vs-MAF 的子结论排除。
它在 orchestration instance、sub-orchestration、activity、external event、entity、
history / checkpoint / replay 和 orchestration versioning 等 durable orchestration
基本面上与 Temporal 接近，必须作为同批强候选对照。

Microsoft Agent Framework Durable Workflow Extension 也不应因为“多一层 graph
mapping”被默认降级为弱于直接 Azure Durable Functions。
Direct Durable primitives 指 Durable Functions / Durable Task 直接暴露的
orchestrator、client 和 entity 原语，不是“不用 MAF”的同义词。
源码显示 MAF Durable Extension 是把 Agent Framework graph、executor、agent
和 RequestPort 有机映射到 Durable Task activity、entity、sub-orchestration、
external event 和 custom status 的组合层；如果 Agent Framework 的可控 agent /
graph / HITL surface 是一等需求，Azure / Durable Task 路线内部应优先 POC
MAF Durable Extension 或 direct Durable + MAF hybrid，而不是默认“纯 direct
Durable Functions 优于 MAF”。

这个升级也有边界。MAF graph authoring surface 不是所有 direct durable
primitives 的 strict superset：普通 graph executor 面对的是 MAF `IWorkflowContext`，
不是任意 `TaskOrchestrationContext`；instance management、`ContinueAsNew`、
entity lock、复杂 timeout / retry 或底层 client 管理能力需要通过 MAF 映射节点、
durable agent context、服务层 `DurableTaskClient`、自写 orchestrator 或 hybrid
composition 进入。因此真正的判准不是“MAF 是否削弱 Durable primitives”，
而是主资源过程更适合由 MAF graph / hybrid 持有，还是由 direct durable
orchestrator / domain process service 持有。只有当 Durable Extension-backed
graph 或 hybrid 亲自持有长期资源过程身份、事件解释、局部失败追平、补偿决策、
副作用边界和审计事实线时，MAF 才进入主 process manager baseline；
否则它仍更准确地是 Temporal、Azure Durable Task 或外部 domain process service
之上的 agent/HITL adapter。

Apache Airflow 与 LangGraph 不应被写成同一 scope 下的主 process manager 等价方案。
Airflow 可作为外围 DAG 调度、审批、报表或相邻 POC；
LangGraph 可作为 agent/HITL adapter 或相邻 POC。
若长期领域状态、事件解释、局部失败追平和物理副作用补偿
由这些框架之外的系统负责，
真正的 process manager 是那个外部系统，而不是被它调用的执行、展示或 agent adapter。

这个决策的核心抽象不是“谁能跑更多 task”，而是一次 buildout 是否需要承载：
长期运行、交互式事件、资源实体导向的局部状态、真实世界副作用、局部失败恢复、
人工/供应商/AI Agent 介入，以及跨节点、机架、网络、固件、OS、集群资源管理和验收的追平。
在这个抽象下，Temporal 的 Workflow Execution、Child Workflow、Activity、
Signal/Update、Event History、Continue-As-New、Reset 和 Worker Versioning
与裸金属主过程模型的同构度最高。
Temporal + 外部 agent + 受控 `PlanPatch` 可以表达业务 plan / resource graph
的动态演进，但 `PlanPatch` 仍必须经过 command API、鉴权、policy、幂等、
reconcile、审批和审计。

| 候选 | 当前定位 |
| --- | --- |
| Temporal | 核心资源过程建模的主 baseline / reference architecture 强锚点；不是最终采购 winner。 |
| Azure Durable Functions / Durable Task | 与 Temporal 同批的 durable orchestration 强候选；需用相同 PoC gates 对照。 |
| Microsoft Agent Framework Durable Workflow Extension | Azure / Durable Task 路线内的 agent/graph/HITL 强 POC 或 hybrid 候选；当 graph/hybrid 亲自承担主过程职责时进入主 baseline。 |
| Apache Airflow | 可做外围 DAG 调度、审批、报表或相邻 POC；不是同 scope 主 process manager。 |
| LangGraph | 可做 agent/HITL adapter 或相邻 POC；不是同 scope 主 process manager。 |

这个决策仍然需要 PoC、压测、运维成本、团队熟练度、目标版本许可、
UI 成熟度、组织已有平台投资、框架版本成熟度和供应商支持来转成采购或工程基线。
组织已有任何候选技术都不能直接推出排序；需要先用同一证据矩阵和 PoC gates 比较。

## 范围

本页讨论物理机/裸金属机器集群的 buildout：
节点、机架和网络连接、BMC、固件/BIOS/RAID/NIC、PXE/iPXE、OS provisioning、
驱动/内核、裸金属资源管理、HPC/集群调度器、基础服务、烧机、验收和集成验证。

本页不把问题改写成 Kubernetes cluster provisioning、GitOps 应用部署、
普通 ETL DAG 或单次 CI/CD pipeline。
Metal3、Ironic、MAAS、Tinkerbell、Foreman、Cobbler、xCAT、Slurm 和 Redfish
可以成为 buildout 的下层或相邻控制面，但本页只讨论 Temporal、Azure Durable
Functions / Durable Task、Microsoft Agent Framework Durable Workflow Extension、
Airflow 和 LangGraph 是否适合承载上层长期过程管理职责。

## 理由

### 认知基线：裸金属控制面不是普通 shell 命令

裸金属 buildout 的下层工具和协议本身已经持有领域对象、生命周期或资源状态。
主 process manager 应协调、观察、补偿它们，而不是把它们重写成无状态命令序列。

| 对象 | 本页采用的职责边界 |
| --- | --- |
| Redfish | BMC/硬件管理标准层；适合作为 Activity 调用的硬件管理协议，不是 workflow engine。 |
| MAAS | 物理服务器资源池和机器生命周期控制面；适合管理 boot、check、deploy、tear down、redeploy 等机器操作。 |
| Ironic | 裸金属 provisioning 控制面；通过 API、plug-ins、PXE、IPMI/Redfish 等管理 physical machines。 |
| Tinkerbell | bare metal provisioning engine；包含 boot、BMC interaction、metadata service 和 provisioning workflow engine。 |
| Foreman | 服务器生命周期、provisioning、configuration、orchestration、monitoring 和 API/UI 控制面。 |
| Cobbler | Linux network installation、DNS/DHCP、power management 和 configuration orchestration 子系统。 |
| xCAT | 集群/HPC/datacenter 部署与管理工具，覆盖硬件发现、OS provisioning 和并行系统管理。 |
| Metal3 | Kubernetes/CRD 风格的 BareMetalHost 和相关硬件/firmware/resource 控制面。 |
| Slurm | 集群资源管理和作业调度系统；适合作为 buildout 后段验收和资源验证执行面。 |

这引出一个共同边界：external inventory/resource graph/audit store
是由裸金属领域事实驱动的必备事实层和架构组件，
不是 Airflow、LangGraph、Temporal、Azure Durable Functions
或 Microsoft Agent Framework 某一方的专属限制。
workflow runtime 管理的是过程和执行；
裸金属工具链管理的是硬件、安装、资源池、作业和生命周期事实。
选型真正要比较的是：在这个事实层之外，哪个 runtime 能更少扭曲地承载
process-level control path、运行中事件入口、局部失败追平和副作用边界。

### 裸金属 buildout 的状态分层

在这个认知基线上，一次真实 buildout 至少有四层状态，不能都塞进 workflow engine 的运行状态：

| 层 | 例子 | 选型含义 |
| --- | --- | --- |
| 资源事实层 | node、rack、switch port、BMC 地址、PXE 网络、firmware、RAID、OS image、Slurm partition。 | 应由 external inventory/resource graph/audit store 持有。 |
| 物理副作用层 | 刷固件、改 BIOS、创建 RAID、安装 OS、重启、上架、换线、供应商现场操作。 | 必须设计幂等、读后校验、锁、补偿和人工确认。 |
| 流程状态层 | blueprint、阶段、门禁、失败分支、修复分支、追平条件、验收级别。 | 主 process manager 应持有过程级状态和控制路径。 |
| 协作审计层 | 人工审批、供应商回复、AI 诊断、测试报告、验收事实。 | 需要可查询、可审计、可投影到业务 UI 的记录。 |

因此，平台选型的关键不是 DAG、Workflow、Task、Sensor、Signal 等术语是否相同，
而是运行时持久化什么状态、外部事件进入哪个对象、故障后恢复什么、
副作用如何隔离，以及计划如何在可审计边界内演进。

### 共同 POC gates 与一手建模锚点

本文不把所有工程前提都写成某个候选的缺陷。
比较应先分两层：

1. **共同 POC gates**：
   所有候选都必须证明 external inventory/resource graph、业务事件 schema、
   auth、dedup、ordering/concurrency、audit、长等待、HITL、幂等键、读后校验、
   补偿、真实设备 reconcile、版本/迁移纪律和 dashboard projection。
   runtime state、Event History、metadata DB、checkpoint、store 或 memory
   都不能替代资源事实层。
2. **runtime 一手建模锚点**：
   在共同 gates 满足后，再比较谁的一手对象更少扭曲地承载
   process-level control path：
   长期过程身份在哪里，外部事件进入哪个运行中对象，局部失败如何隔离和追平，
   replay/reset/fork/rerun/backfill 如何保护真实副作用，
   版本迁移恢复的到底是过程对象还是调度/graph 执行上下文。

这个区分不能反过来洗掉真实不匹配。
如果 Airflow、LangGraph、Azure Durable Functions、MAF Durable Extension
或 Temporal 方案依赖另一个 domain process service
持有长期过程状态、事件解释、局部追平、补偿决策和业务审计，
那套 service 才是本文定义下的主 process manager；
被它调用的 runtime 只是 scheduler、executor、durable execution runtime、
workflow adapter 或 agent/HITL adapter。
因此，产品差异不是“谁有没有 external inventory、幂等或 dashboard 问题”，
而是“为满足这些 gates，需要把多少主过程管理逻辑放到 runtime 之外，
以及 runtime 的一手对象是否会把长期资源过程压扁成相邻模型”。

### 第一批强候选的证据矩阵

Temporal、Azure Durable Functions / Durable Task 与 MAF Durable Workflow Extension
的差异很细，不能靠“谁文档多”排序。
下面矩阵区分已投影的一手证据、当前能支持的判断和仍需 PoC 的缺口：

| 维度 | Temporal | Azure Durable Functions / Durable Task | MAF Durable Workflow Extension | 当前判断 |
| --- | --- | --- | --- | --- |
| 长期过程身份 / 分区 | Workflow Execution、Child Workflow；Child Workflow 可按 host/resource 使用 Workflow ID 并隔离 Event History。 | Orchestration instance ID 可映射外部实体；sub-orchestration 是 SDK feature；instance ID 可指定但 random ID 更利于负载分布。 | graph workflow 注册为 Durable Task orchestration；subworkflow 映射 sub-orchestration；resource identity 需穿过 graph/executor/Durable Task 映射或 hybrid 边界。 | Temporal 证据更直接；Azure 不弱但需验证 resource-derived ID 热点和 sub-orchestration 追平；MAF 不丢失 Durable Task 身份原语，但资源身份绑定需要 POC。 |
| command/event entry | Signals 是异步消息；Updates 可验证、可追踪并返回结果，但仍不是完整 command gateway。 | external events 是 one-way async；instance management APIs 可 start/query/terminate/suspend/resume/purge，但同步 command result 需外层服务设计。 | request port 映射 external event；HITL 和 agent workflow 更一体，但 auth、timeout、dead-letter、审计仍需应用层。 | 若 buildout 命令需要同步校验和返回，Temporal 现有证据较强；Azure/MAF 不是不可行，而是 command service 边界更关键。 |
| 长等待 / timers | Timer 是 Workflow Execution 内持久等待。 | Durable timers 支持等待；JS/Python/PowerShell Durable Functions 有六天限制，.NET/Java 支持任意长 timer；Durable Task SDK 语言状态需复核。 | 继承 Durable Task-backed 等待路径，但 graph/request port 的长期等待、timeout 和恢复仍需 PoC。 | 目标语言会改变排序；不能泛化为 Azure 不支持多周等待。 |
| 版本、恢复、迁移 | Reset、Continue-As-New、Worker Versioning 边界较完整，但不是物理回滚或任意迁移。 | Orchestration versioning 是内建机制；instance 创建时绑定 version，worker/client 可做 version matching 和条件分支。 | checkpoint/recover 支撑 graph workflow；checkpoint 不承诺任意 topology migration；durable graph versioning 仍需目标版本实测。 | Azure versioning gap 已缩小；MAF 的 graph/executor/checkpoint 兼容性是不确定性核心。 |
| hosting/backend | 需要验证 Temporal server/backend、worker placement、history growth 和运维成本。 | Durable Functions 与 standalone SDKs 共享核心能力；standalone workers 可在 Kubernetes/VM 等 compute 上运行，但 SDK 连接 Durable Task Scheduler managed backend。 | 支持 Azure Functions 与 BYOC/self-host worker；self-host worker 仍连接 Durable Task Scheduler backend；文档安装使用 `--pre` / `--prerelease`。 | 如果必须完全自托管或 air-gapped，Azure/MAF 的 Scheduler 依赖是关键风险；如果接受 Azure-connected backend，Azure/MAF 竞争力上升。 |
| AI / HITL integration | 通过 Activity、Signals/Updates 和外部 agent platform 集成。 | 通过 activity、external events、entities 或外部服务集成。 | agent、multi-agent、HITL、graph workflow 是一手能力，并映射到 Durable Task-backed execution。 | 若 Agent Framework control 是一等需求，MAF 是 Azure / Durable Task 路线内优先 POC；边界在于它不是 direct primitives 的 strict graph-level superset。 |

因此，本文后续使用“baseline”时只表示 PoC 对照或 reference architecture，
不是最终 winner。
Temporal 的价值不只是证据完整或变量少，而是在核心资源过程建模上同构度最高；
Azure Durable Task 必须作为同批强候选补齐对照；
MAF 是否进入主 baseline 取决于 graph / hybrid 是否亲自承担主过程职责，
而不是取决于“使用 MAF 是否天然削弱 Durable Task primitives”。

### Direct Durable primitives 与 MAF 的关系

本文把 Direct Durable primitives 定义为 Durable Functions / Durable Task
直接暴露给 orchestrator、client 和 entity 作者的 durable runtime / control
原语：activity、sub-orchestration、durable timer、external event wait / raise、
entity call / signal / lock、`ContinueAsNew`、custom status、replay-safe time / GUID、
以及 start、query、terminate、suspend、resume、purge、restart 等 instance
management API。它们是底层 durable execution/control surface，不等于“不要 MAF”。

MAF Durable Extension 不会把这些底层能力删掉。源码显示 ordinary executor
映射为 `CallActivityAsync`，RequestPort 映射为 `SetCustomStatus` +
`WaitForExternalEvent`，agent executor 走 Durable Entity-backed `DurableAIAgent`，
subworkflow 走 `CallSubOrchestratorAsync`；`ConfigureDurableOptions` 支持 agents
和 workflows 的 additive configuration，并开放 Durable Task worker / client
builder；`DurableAgentContext` 还把 schedule orchestration、get status 和 raise
event 暴露给 durable agent / tool context。

但 MAF graph surface 也不是 strict superset。普通 executor 执行时拿到的是
`DurableWorkflowContext` / `IWorkflowContext`，不是任意可调用的
`TaskOrchestrationContext`。因此，复杂 direct primitive 需要通过 graph mapping、
agent/tool context、服务层 `DurableTaskClient`、自写 Durable orchestrator 或 hybrid
composition 接入。对裸金属 buildout 的实际含义是：如果一等需求是可控 agent /
graph / HITL process，MAF Durable Extension 应在 Azure / Durable Task 路线内部
被升级为优先 POC 或 hybrid 候选；如果一等需求主要是资源状态机和 direct durable
orchestration，直接 Durable Task / Azure Durable Functions 仍是必要对照。

### 仅看业务建模扭曲时的 Temporal / MAF 结论

若评价目标函数被收窄为“业务场景建模扭曲程度”，Temporal 与 MAF Durable Extension
的差距会比总评矩阵更清楚。裸金属 buildout 的主过程对象是长期、可寻址、可局部追平的
cluster / rack / node / fabric 资源过程，而不是 agent graph 本身。
在这个业务本体下，Temporal 的一手对象更接近过程模型；MAF Durable Extension
需要把资源过程穿过 Agent Framework graph、executor、superstep、Durable Task
orchestration/activity/entity/external event 以及外部资源图之间的映射。

| 建模维度 | Temporal | MAF Durable Extension | 建模扭曲判断 |
| --- | --- | --- | --- |
| 长期资源过程身份 | Cluster buildout 可是 Workflow Execution；node/rack/fabric 可是 Child Workflow。 | Graph workflow instance 可承载总过程，resource identity 需穿过 graph node、executor、Durable Task instance/entity 和外部资源图。 | Temporal 更少扭曲。 |
| 资源分区与局部失败追平 | Child Workflow 可隔离历史、等待、失败和修复后追平。 | subworkflow 可映射 sub-orchestration，但 graph/executor/checkpoint 与资源身份的绑定需额外约定。 | Temporal 更少扭曲。 |
| 运行中业务事件入口 | Signal/Update/Query/Cancellation 分别覆盖异步消息、可验证命令、只读查询和协作取消。 | RequestPort 更像 workflow 主动等待外部输入；pending status 是发现投影，respond 不等于业务处理完成。 | 面向通用 buildout command/event，Temporal 更少扭曲；面向表单式 HITL，MAF 局部更自然。 |
| 物理副作用边界 | Activity 是明确外部 I/O 边界，进入 Event History / mutable state 的是调度、完成和失败事实。 | ordinary executor 走 activity，agent executor 走 entity，RequestPort 走 external event，subworkflow 走 sub-orchestration。 | 两者都能表达副作用边界；Temporal taxonomy 更统一，MAF 多一层 executor 映射。 |
| 图路由、fan-in/fan-out 和 target routing | 需要业务代码建模并发和汇聚，但 runtime 不把它压成另一个 graph projection。 | Durable runner 的 fan-in、fan-out selector 和 targeted message 语义不是 MAF in-process graph 的完整保真。 | 对资源过程建模，MAF graph projection 增加额外扭曲。 |
| 历史治理与版本演进 | Continue-As-New、Reset、workflow patching / versioning 和 Worker Versioning 是显式 runtime 面。 | 继承 Durable Task 长运行与 replay，但当前 graph runner 未暴露等价 graph-level history-chain、reset、topology migration 或 worker-code-version routing 面。 | Temporal 更少扭曲。 |
| 过程审计事实线 | Event History 是 Workflow Execution 的恢复与审计事实日志。 | custom status 是 live projection，完成后还需从结果 events 取回；Durable Task dashboard 是 runtime 观察面，不等于 MAF 业务 graph 审计线。 | Temporal 更少扭曲。 |
| Agent/HITL 作为业务本体 | Agent session、memory、LLM/tool schema 需业务层或外部 agent platform 建模。 | AIAgent、DurableAIAgent、AgentEntity、RequestPort 和 graph executor 是一等 authoring surface。 | 如果 buildout 被定义成 agent/HITL/graph 协作过程，MAF 可在该局部更少扭曲。 |

因此，**在“长期资源状态机 + 外部事件 + 局部追平”的裸金属主 process manager
模型下，Temporal 相对 MAF Durable Extension 可判为建模扭曲更少，且在核心资源过程维度上强胜。**
这个结论不推翻总评边界：两者仍共同需要 external inventory/resource graph、业务事件契约、
幂等键、读后校验、补偿和业务 dashboard；如果业务本体改成 AI/HITL/agent graph 协作，
MAF 的局部建模优势会重新进入主比较。

这个例外不能被泛化。裸金属控制面本来就不是简单 shell 命令；
MAAS、Ironic、Tinkerbell、Redfish、Slurm、供应商现场操作和人工验收都更像
外部控制面或外部事实事件。人工参与比例高，通常不是“纯 Agent Graph
更适合作主 process manager”的证据，反而增加了对持久事件入口、鉴权、幂等、
超时、审批版本、资源绑定、审计和恢复后追平的要求。若 Agent/HITL 只是辅助诊断、
审批 UI 或 operator copilot，它更稳妥的定位是被 durable process manager 调用的
Activity、Child Workflow、外部 agent service、Signal/Update/external event 入口，
或业务 UI / copilot surface；若 Agent Framework control 是一等主流程能力，
则应验证 MAF graph / hybrid 是否直接持有这些过程职责。

MAF 作为主 process manager 的成立条件因此不是“证明 agent graph、checkpoint
或 RequestPort 可运行”，而是证明 Durable Extension-backed graph / hybrid
亲自持有资源过程身份、业务事件解释、局部追平、补偿决策、副作用边界和审计事实线。
若这些职责仍由 external inventory/resource graph、command service 或另一个 durable
workflow 持有，MAF graph 就是 agent/HITL adapter，而不是本文定义下的主 process manager。

因此，“MAF 的 AI workflow-native 集成度更高”需要精确定义。源码层面，`AIAgentBinding`
把 AIAgent 作为 workflow executor binding；`DurableAIAgent` 在 orchestration 中创建
`DurableAgentSession`，并通过 Durable Entity 调用 `AgentEntity.Run`；`AgentEntity`
把 conversation history 与 TTL 持久化在 entity state；Azure Functions hosting 的
respond path 把 RequestPort response 转成 Durable Task external event。这些机制的真实价值是：
减少 agent/HITL graph 方案中的 plan interpreter / graph runner、agent session
persistence、pending input discovery / response loop，以及 AI/HITL authoring surface
胶水层。

但这不是主 process manager 语义上的自动胜出。裸金属 buildout 仍然需要业务自己的
`PlanPatch` schema、command API、鉴权/RBAC、幂等键、request/result contract、
资源绑定、external inventory / reconcile、补偿策略、审计事实线和 dashboard projection。
Temporal + 外部 agent + `PlanPatch` 在“业务 plan / resource graph 的受控 diff”
这一层可以表达同一类动态计划演进；差异在于 MAF 把 agent/HITL authoring 与 session
状态放进框架，而 Temporal 要由应用层或外部 agent platform 建 façade。换言之，
MAF 的优势是 agent/HITL graph 方案的 authoring/runtime ergonomic 与状态放置优势，
不是已经证明的核心资源过程建模优势。

实践证据也不支持把“dynamic workflow”理解成 agent 在生产过程中任意自修改 workflow
topology。Claude Code 的 dynamic workflows 是由 JavaScript script 编排多个 subagents；
官方文档明确说 workflow 的 plan 由 script 持有，而不是由 Claude 在每个 turn 中临时决定。
Claude Agent SDK 的 todo/task tracking 也更像结构化 task state 的 `TaskCreate` /
`TaskUpdate`，而不是任意拓扑迁移。MAF 自身的 workflow state 文档同样把 builders
描述为可变、built workflows 描述为没有 public API 可修改；checkpoints 捕获的是执行状态，
不承诺自动迁移到任意变更后的 graph topology。因此更稳妥的行业模式是：
稳定外层 orchestration + 受控计划/任务状态更新 + 审计/审批/回滚边界，
而不是“放飞自我”的 agent graph。

### Temporal 接入 Agent 与计划修订的边界

Temporal 可以接入 agent，但 agent 是应用负载，不是 Workflow replay 路径中的非确定性解释器。
LLM、tool 调用、外部诊断和供应商系统访问应放在 Activity、Child Workflow 或外部 agent service
中；Workflow 保存的是 agent 输出被接受后的过程状态、计划版本、事件和副作用边界。

如果 agent 需要“改图”，应先区分两种图：

| 图的含义 | 正确边界 |
| --- | --- |
| Workflow Definition / code graph | 不能由 agent 在运行时原地改写；需要代码部署、workflow patching/versioning、Worker Versioning 和 replay-safe 分支。 |
| 业务 plan / resource graph | 可由 agent 生成 `PlanPatch`，但应作为不可信业务输入，经外部 command API 与 Workflow Update/Signal 进入运行中 Workflow。 |

推荐形态是：agent 产出带 `basePlanVersion`、资源范围、操作 diff、风险级别、幂等键和前置条件的
`PlanPatch`；外部 command API 先做鉴权、schema、RBAC、大小限制和基础安全检查；
需要同步校验和返回结果时用 Temporal Update，异步通知时用 Signal，只读读取用 Query。
Workflow 再按当前 deterministic state 判断是否可接受该 patch，必要时通过 Activity
读取 external inventory、策略引擎或真实设备状态，完成物理 reconcile 和 policy validation。

Continue-As-New 不是 agent 直接调用的“改图 API”，也不是物理回滚或任意计划迁移魔法。
agent 或客户端最多通过 Update/Signal 请求进入一个受控 rollover 边界；
Workflow 主逻辑在确认 handler 已完成、危险副作用无未决重放风险、compact state 已准备好后，
用 Continue-As-New 把 plan version、processed update IDs、child workflow IDs、
pending approvals 和必要过程状态交给同一 Workflow ID 下的新 Run 与新 Event History。

### Temporal 的 reference architecture 价值与限制

Temporal 的优势在于 Workflow Execution 是长期、durable 的过程对象；
Event History 支撑 replay 恢复控制状态；
Signals/Updates 可以把外部消息送入运行中的 Workflow Execution；
Timer 可以表达 execution 内部的持久等待；
Activity 是外部 I/O 和真实世界副作用的边界；
Child Workflow 可以按 host、node、rack、fabric 或 validation domain
把长期过程拆成资源实体相关的子执行。

在 durable orchestration runtime 层，这较直接匹配裸金属 buildout 的主过程管理问题，
也使 Temporal 适合作为最小 reference architecture：

- 一次 cluster buildout 可以是可寻址的长期 Workflow Execution。
- 单节点、机架或 fabric 的处理可以通过 Child Workflow 隔离历史、等待、重试和局部失败。
- BMC/Redfish、MAAS/Ironic/Tinkerbell、Foreman/Cobbler/xCAT、Slurm、
  通知和 AI Agent 调用应落在 Activity 或外部事件边界。
- 人工确认、供应商回复、现场操作结果和计划变更请求可以通过 Signals/Updates
  进入运行中的过程对象。
- 在前述领域事实层之外，Temporal 保存过程级状态、控制路径、事件入口和可审计执行历史。

必须降调的点同样重要：
Signals/Updates 不是完整 command gateway，仍需要外部入口处理鉴权、schema、
去重、审计和同步返回语义；
Temporal Reset 不是物理回滚；
Continue-As-New 是 Run 边界状态交接和 Event History 截断点，不是任意计划迁移魔法；
Worker Versioning 是 worker/deployment routing 与 replay-safe 升级机制，
不自动迁移已发生的物理副作用；
Activity retry 不是 exactly-once。
所有真实设备操作仍必须通过幂等键、状态读回、外部锁、补偿流程和人工确认保护。
Temporal 仍需和 Azure/MAF 一样通过 PoC 证明 worker placement、Event History 增长、
in-flight versioning、业务 dashboard projection 和目标运维成本。

### Azure Durable Functions / Durable Task 的候选定位

Azure Durable Functions / Durable Task 应被视为接近 Temporal 的 durable
orchestration 强候选，而不是按 Airflow 或普通 agent graph 的标准排除。
在同等 external inventory/resource graph、业务事件 schema、幂等键、读回校验、
锁和补偿纪律下，它与 Temporal 的相似点非常实质：
orchestration instance 可以承载长期过程身份；
sub-orchestration 可以作为资源过程分区候选；
activity 是真实 I/O 与物理副作用边界；
durable timer 可以表达跨维护窗口等待；
external event 可以让人工审批、供应商回调或现场操作结果进入运行中实例；
entity 可以承载小粒度串行协调状态；
execution history / checkpoint / replay 支撑故障后的过程恢复。

因此，Azure Durable Functions / Durable Task 的问题不是“它也需要外部资源事实层”、
“activity 也要幂等”或“orchestrator 也有 deterministic replay 约束”。
这些同样适用于 Temporal，应放入共性 POC checklist，
不能写成 Azure 专属缺点。
真正要比较的是：共同前提满足后，Azure 体系的原生语义分别降低或增加了哪些
主 process manager 负担。

第一组差异是产品与 hosting 边界。
Durable Task 可以通过 Azure Durable Functions 使用，
也可以通过 standalone Durable Task SDKs self-host。
两者共享 durable execution 基础能力，
但触发器、scaling、storage provider、monitoring、management APIs 和运行面不同。
若 buildout worker 必须长期位于私有 out-of-band 管理网访问 BMC、PXE、
MAAS/Ironic 或交换机控制面，就不能只用 Azure Functions HTTP starter、
timer demo 或云上 plan 成功来证明目标方案成立；
必须先明确最终运行面到底是 Azure Functions plan，
还是 AKS、VM、on-premises 上的 standalone Durable Task worker。
Temporal 也要证明 worker placement、backend、容量和 rollout；
但它的候选定义直接围绕 Temporal server/backend + worker 展开，
Azure 方案则更早需要把“Durable Functions 产品面”
与“Durable Task standalone runtime 面”分清。

第二组差异是交互模型。
Durable external events 可以把外部异步信号送入 orchestration。
例如供应商完成换线后 raise event 到 `BuildoutCluster-2026w25`，
让等待中的 `ValidateFabric` 阶段继续。
Temporal Signals/Updates 也面向运行中 Workflow；
其中 Updates 更适合表达带校验和同步结果返回的变更请求。
于是当操作员提交“给 rack-7 追加 12 台节点”
或“批准跳过某台机器的 burn-in 重跑”时，
Azure 方案需要明确由哪一层完成命令鉴权、schema 校验、审计、同步返回和
event 投递。
Azure 并非不能做，而是需要把 command service、external event
和 orchestration state 的边界画清楚。

第三组差异是观察与运维证据边界。
Durable Task storage provider 保存的是 runtime state、history、entity state
和 internal messages；Temporal Event History 也不是业务资源图。
两者都不应替代 node/rack/BMC/firmware/OS/network/validation 的事实层。
真正需要 POC 比较的是：目标运行面是否能稳定暴露 buildout 所需的过程观察点，
例如某个 rack 卡在人工审批、某批节点正在等待 BMC 重启、
某个 activity 因现场修复后需要重试、
某个 orchestration/entity 在 worker 崩溃后恢复。
若这些观察、告警和 dashboard projection 主要由外部系统补齐，
则应承认外部系统承担了部分 process manager 职责。

第四组差异是版本、replay 与副作用纪律。
Durable orchestrator replay、storage provider 恢复、worker failover
和 external event 等待恢复的是 durable runtime 的过程执行状态，
不是物理设备当前事实。
Azure 方案必须像 Temporal 一样证明 activity 幂等、外部事实 reconcile、
在途 instance 的代码/版本兼容和危险副作用保护。
需要降调的一点是：当前已投影证据显示 Durable Task 生态有
orchestration versioning；
orchestration instance 创建时永久关联 version，
worker/client 可以用 version matching 或条件分支让新旧 instance 并存。
因此，不能再把 Azure 的版本演进简单写成未知弱项。
区别在于这些证明要落到选定的 Azure Functions plan、standalone Durable Task
worker、storage provider 和部署/监控边界上。

第五组差异是 backend 与 worker placement。
Durable Task SDKs 可以在 Azure Container Apps、Kubernetes、VM 等 compute
上运行 worker；
Durable Task Scheduler 是 SDKs 的 managed backend，并可通过 private endpoints
支持私有连接。
这让 Azure/Durable Task 在 Azure-connected 或 private-link 可接受的环境中很有竞争力；
但如果目标是完全离线、完全自托管的裸金属控制面，
Scheduler 依赖会成为必须单独验证的约束。

结论是：Azure Durable Functions / Durable Task 可以竞争
“durable orchestration process manager”位置，
尤其适合组织已经接受 Azure Functions 或 Durable Task 运行面，
并能把 external events、activities、entities 与外部资源事实层清晰分层的场景。
但如果方案成立依赖另一套 domain service 持有 process-level control path、
事件解释、局部追平和补偿决策，
那么那套 service 才是本文定义下的主 process manager，
Azure Durable Functions / Durable Task 只是 durable execution runtime。

### Microsoft Agent Framework Durable Workflow Extension 的候选定位

Microsoft Agent Framework Durable Workflow Extension 比普通 agent graph
更接近 durable process manager，
因为它不是只依赖 in-process graph checkpoint，
而是把 graph-based Agent Framework workflows 接入 Durable Task-backed execution。
现有证据显示，`ConfigureDurableWorkflows` 会配置 durable graph workflows，
并注册 orchestrations、activities 和 agent entities；
dispatcher 会把普通 executor 调成 Durable Task activity，
把 subworkflow 调成 sub-orchestration，
把 agent executor 走 Durable Entity，
并把 request port 映射为 external event 等待。
Durable Extension 文档还支持 Azure Functions 与 self-hosted worker 两种 hosting
model，并描述了跨多个 stateless worker processes/hosts 的 checkpoint 与 recover。
但 self-hosted worker 仍连接 Durable Task Scheduler backend；
它不等于自带生产级 durable backend。

因此，MAF Durable Workflow Extension 不能被归入未接入 durable orchestration
的调度层或普通 agent graph 候选。
它继承了 Durable Task 的长期执行、activity 副作用边界、external event、
entity、sub-orchestration 和恢复能力；
在同等 external inventory/resource graph、业务事件 schema、幂等、
副作用隔离和 replay 纪律下，它确实可以进入 Temporal 相邻的 POC。
它相对 Temporal 的关键差异不是 Durable Task backend 本身，
而是 Agent Framework 在 Durable Task 之上增加的 graph / executor /
superstep / agent entity 抽象层。

第一组风险是 workflow surface 与资源过程身份映射。
Microsoft Agent Framework 有多个 workflow surface。
Durable Extension 文档和源码投影支撑的是 graph-based workflows
经 Durable Task infrastructure checkpoint/recover 的路径；
不能把 standard checkpoint storage、functional workflow surface
或未启用 Durable Extension 的 core workflow 直接等同为同一能力。
例如一个 Python functional workflow 只使用普通 checkpoint storage，
不能因为同属 Microsoft Agent Framework 就被写成 Durable Task-backed
long-running process manager。

在资源建模上，Temporal 的建模面可以围绕 cluster Workflow、node/rack/fabric
Child Workflows、Activities 和 Signals/Updates 展开。
MAF Durable Extension 则需要说明：
一个长期 buildout 过程对应哪个 graph workflow instance；
`DiscoverNodes`、`ProvisionNode`、`OperatorApproval` 等 executor
如何映射到 durable activity、sub-orchestration、agent entity 或 request port；
node/rack/fabric 的长期身份如何与 graph node、executor binding、
Durable Task instance/entity 以及外部资源图关联。
例如 `ProvisionNode(node-42)` 作为 executor activity 失败后，
现场修复 BMC 凭据并重新提交事件，
这个事件应该进入哪个 request port、唤醒哪个 graph workflow、
如何只追平 `node-42` 而不误触其他节点，必须在架构中显式建模。

第二组风险是迁移与 checkpoint 兼容性。
MAF checkpoint 可以捕获 executor state、pending messages、
pending requests/responses 和 shared states；
workflow state 文档同时提示 built workflow 没有 public API 可修改。
Temporal 也有 deterministic replay、Continue-As-New、Reset 和 Worker Versioning
纪律，不能被写成任意迁移或物理回滚。
区别在于 Temporal 的迁移讨论主要围绕 Workflow Execution、Event History、
Run 边界和 worker routing；
MAF 还要叠加 graph definition、executor 拆分、edge/superstep 结构、
agent entity 与 checkpoint shape 的兼容性。
例如把原来的 `ProvisionNode` executor 拆成 `FlashFirmware`、`InstallOS`、
`JoinScheduler` 后，
已经 checkpoint 在旧 superstep 的 buildout instance 如何恢复、继续、
跳转或重新入队，不能只用“有 checkpoint”概括。

第三组风险是观测与运维分层。
Durable Task backend 能 dispatch orchestrator、activity 和 entity work items，
并管理 durable state；
但 MAF 方案还需要证明 Agent Framework 层的 graph execution、
executor dispatch、agent entity、request port、checkpoint/recover 状态
能被稳定观察和诊断。
对裸金属 buildout 来说，POC 不能只证明 multi-agent HITL demo 可运行；
它必须证明 worker 崩溃、activity retry、external event 等待、
agent approval、subworkflow 失败和恢复后的 graph 位置都能被定位，
并能投影到业务 dashboard。
Temporal 也需要可观测性和运维 POC；
MAF 的额外问题是中间抽象层是否带来不可接受的映射和诊断成本。

MAF Durable Workflow Extension 的强点在于 agent、multi-agent、workflow graph
与 HITL integration。
如果主过程天然包含 AI 诊断、agent 协作、人工审批和可恢复 graph execution，
把这些能力放在同一框架中可能比 Temporal + 独立 agent platform 减少集成负担；
在 Azure / Durable Task 路线内部，也可能比纯 direct Durable Functions 更符合
Agent Framework control 需求。
但这只有在 MAF graph / hybrid 自己承载 process-level control path，
并把 agent/HITL interaction 写回长期资源过程身份、事件解释、局部追平、
补偿决策和审计事实线时，才是主 baseline 价值。
如果 AI/HITL 只是被主 process manager 调用的辅助能力，
MAF 的 Durable Task-backed graph layer 更适合作为上层 agent/control surface，
不应默认替代更小的 durable process substrate。
若长期资源状态、领域事件解释、局部失败追平、补偿决策和业务审计
仍由另一个 service 持有，
那么那个 service 才是主 process manager，
MAF Durable Workflow Extension 只是更强的 agent/HITL/durable workflow adapter。

### Airflow 的 runtime 建模锚点与适配扭曲

Airflow 不能被简单排除为“不能等人、不能等事件、不能动态展开”。
它有明确的 DAG/TaskInstance 调度模型，也有 Dynamic Task Mapping、deferrable
operators、event-driven scheduling、HITL operators、TaskInstance 状态和 Airflow UI。
这些能力需要被纳入判断，是为了避免把 Airflow 错判成“完全不能等待或响应事件”；
但它们并没有把 Airflow 变成裸金属 buildout 的长期 process manager。

Airflow 的关键限制不是“不能运行长等待 task”，而是主状态对象和恢复语义。
Airflow 更自然地持久化 DagRun、TaskInstance、mapped task、retry、deferred
和 removed 等 scheduler/task execution 状态。
这些状态可以很好表达“这张有限任务图执行到哪里”，
但不应直接替代“这个物理集群资源图在多周内经历哪些局部失效、修复、追平和验收事实”。

因此，如果一个方案声称“用 Airflow 做 process manager”，不能只用
external inventory/resource graph 来回答。
外部资源图保存领域事实、锁和审计是所有候选都需要的共性纪律；
它本身不会否定 Airflow。
真正要检验的是 process-level control path 在哪里：
长期资源身份如何映射到 DagRun/TaskInstance 或外部对象，外部事件如何进入运行中过程，
局部失败如何传播和追平，物理副作用补偿决策如何形成，过程审计真源由谁维护。

若这些控制职责实际由另一个 domain process service 或事件系统持有，
那它才是本文 scope 下的 process manager，Airflow 只是有限 DagRun 的
scheduler/executor。
若 Airflow 自己承担主 process manager，则必须正面解释其一手机制的限制：
scheduler 基于 timetable 创建 DagRun、推进可调度 TaskInstance 并交给 executor；
event-driven scheduling 更自然地触发 DagRun，而不是向任意运行中资源过程对象注入事件；
deferrable operator 解决 task 等待和 worker slot 占用，但 deferred 后本地状态不会自动持久化；
Dynamic Task Mapping 是 scheduler 基于上游数据创建 mapped task instances；
DAG file processing、serialization、DAG bundle versioning 和 `DagRun.verify_integrity`
提供部署/调度视图与既有 DagRun 的受控 reconciliation，
不是运行中资源状态机的任意拓扑演进。
这个区分是本文为了遵守 scope 必须保留的判断边界。

若仍坚持让 Airflow 承担主 process manager 职责，差异不在于它有没有某个单点能力，
而在于这些能力组合后是否自然承载长期资源过程。
下面三点不是把共同 gates 写成 Airflow 专属缺陷，
而是说明 Airflow 的一手对象会把这些 gates 映射到 DAG/DagRun/TaskInstance
和 schedule/data interval 上：

1. **资源身份更容易落到有限 mapped task，而不是长期资源过程对象。**
   例如 `discover_nodes` 产出 10 台 host，Airflow scheduler 可以为
   `provision(host)` 创建 10 个 mapped TaskInstances。
   这能表达“当前这批 host 扇出执行”。
   但如果两天后新增一个 rack、替换一台机器、某个 switch port 修复后需要只追平受影响节点，
   Dynamic Task Mapping 本身并不维护“host/rack/fabric 是长期过程对象”的身份和演进。
   Temporal 也不会自动理解拓扑；
   但 Child Workflow 可用 host/node/rack 等资源身份作为 Workflow ID 或分区边界，
   再用 Signals/Updates 把修复、追加和审批事件送入运行中的过程对象。
   因此在同样需要业务建模的前提下，Temporal 的资源过程分区语义更贴近这个问题。
   Azure Durable Task 的 orchestration instance/sub-orchestration/entity
   也属于同层 POC 候选；
   MAF Durable Extension 则必须证明 graph workflow instance、executor
   和 Durable Task instance/entity 的映射能达到同等稳定性。
2. **事件和等待更自然进入 TaskInstance 或新 DagRun，而不是运行中资源过程 mailbox。**
   Airflow HITL 可以让 DAG 暂停等待人工输入；
   deferrable operator 可以释放 worker slot 等待 trigger；
   event-driven scheduling 可以基于符合 `BaseEventTrigger` 的事件触发 DagRun。
   这些能力有价值，但它们更自然地落在 TaskInstance 等待、DAG 分支或新 DagRun 入口。
   event schema、鉴权、去重、顺序/并发和审计是所有候选的共同 gate；
   Airflow 的特有待证点是这些事件最终如何绑定到可寻址的长期资源过程，
   而不是只触发一个新的 DagRun 或恢复某个 task。
   资源依赖传播、局部失败追平和物理副作用补偿仍要由业务控制路径显式实现。
   Temporal 也不自动解决这些业务问题；
   但 Signals/Updates/Timers 直接进入长期 Workflow Execution，
   Activity 明确隔离真实世界副作用，
   所以同一套业务逻辑更容易围绕“这个 cluster/node/rack 过程现在处于什么状态、收到什么事件、下一步怎么追平”来建模。
3. **DAG version、backfill/catchup 和 removed task 把迁移压力落到调度图重处理语义上。**
   Airflow 的 DAG file processing、serialized DAG、DAG bundle versioning、
   `DagRun.verify_integrity`、backfill 和 catchup 处理的是 scheduler 看到的 DAG 版本、
   TaskInstance reconciliation 以及历史 logical date 的 DagRun 创建/重处理。
   replay、reset、fork、rerun、retry 或恢复只要跨真实副作用边界，
   所有候选都必须先 reconcile external inventory 与真实设备状态。
   Airflow 的相对问题是：
   backfill/catchup/rerun 与 removed task reconciliation
   原生围绕 logical date、DagRun 和 TaskInstance，
   对裸金属 buildout 更容易把“过程迁移”表现为“调度图重处理”。
   Temporal 同样有严格迁移纪律：
   deterministic replay、Continue-As-New、Reset 和 Worker Versioning 都有限制，
   Reset 也不是物理回滚。
   差异是 Temporal 的纪律围绕 Workflow Execution/Event History/Run 边界展开，
   更接近“一个长期过程对象如何演进和恢复”；
   Airflow 的纪律围绕 DAG 代码、DagRun、TaskInstance 和 schedule/data interval 展开，
   更容易把真实资源过程压扁成调度图重处理问题。

### LangGraph 的定位与主 process manager 待证点

LangGraph 也不能被低估成“不能长期运行、不能持久化、不能 HITL”。
它面向 long-running stateful agents/workflows；
通过 checkpointers 保存 thread-scoped graph state，通过 stores 提供跨 thread
long-term memory；
`interrupt()` / resume 支持 human-in-the-loop；
fault tolerance 提供 graph/node 级 retries、timeouts 和 error handlers；
Agent Server 有 persistence database、task queue 和 queue worker。
graph migrations 与 time travel 支持受约束的 checkpoint replay、fork
和已有 thread 在新 graph definition 下恢复。

公平比较时，不能把所有 runtime 都必须遵守的业务纪律写成 LangGraph 独有缺陷。
Temporal 也不会自动理解裸金属资源过程：
它不知道 `node-42`、rack、fabric、BMC、Slurm validation 的领域含义；
Temporal Event History 也不是 external inventory/resource graph，更不是资源事实库。
所有候选都需要业务层定义资源身份、事件 schema、锁、审计、幂等键、
真实状态 reconcile 和副作用边界。

真正差异在于 runtime 的建模重心和一手语义是否足够稳定地承载本文定义的
主过程控制路径。
Temporal 的重心是 durable Workflow Execution、Child Workflow、Activity、Timer、
Signal/Update mailbox 和 Event History。
它仍需要业务映射，
但这些对象可以作为架构锚点：
cluster Workflow 表示总 buildout 过程；
node/rack/fabric Child Workflows 表示可独立寻址、可局部失败、
可单独追平的资源过程分区；
Signals/Updates 把审批、修复、供应商回执和下层系统事件投递到运行中的过程对象；
Activities 隔离真实世界副作用。

LangGraph 的重心则落在 agent graph、thread、run、checkpoint、store、
interrupt/resume 和 graph node execution 上。
这非常适合 AI diagnosis、operator copilot、stateful agent automation
和 HITL 决策支持；
但若把它提升为裸金属 buildout 的主 process manager，
方案必须额外证明这些 graph/thread/run 语义能长期、稳定、可审计地承载
resource-partitioned、externally-addressable、long-running process manager，
而不是只承载一个可恢复的 agent graph 执行上下文。

在现有证据下，LangGraph 作为主 process manager 的主要待证点应集中在
resource-process contract，而不是把所有 runtime 都有的 checkpoint、
fork 或 worker 队列边界写成能力缺陷：

1. **资源过程身份需要从 thread/run/graph 映射出来。**
   这不是说 LangGraph 不能映射资源过程。
   业务层完全可以约定 `thread_id = buildout-123`，
   或为每个 node/rack 建 thread、subgraph、外部过程对象与事件路由。
   但这套映射必须由方案自己证明稳定性。
   例如 `node-42` 在刷 firmware 后失败，两天后人工修复网线，
   只需要从 rack-level validation 前追平。
   方案必须说明：
   `node-42` 的长期过程身份在哪里；
   修复事件如何路由到正确的运行中过程；
   其他 39 台机器是否被隔离；
   追平条件由 graph state、外部资源图，还是另一个 domain process service 决定。
   Temporal 也需要业务定义这些含义；
   但 Child Workflow ID、Workflow Execution、Signals/Updates
   可以直接作为 durable process identity 和消息入口的映射锚点。
   Azure Durable Task 和 MAF Durable Extension 也需要业务映射，
   但它们至少可以围绕 orchestration instance、sub-orchestration、
   entity、activity 和 external event 建立相邻锚点。
2. **interrupt/resume 是强 HITL 机制，但不是完整业务事件模型。**
   `interrupt()` / resume 能很好表达“graph 暂停，等待 operator 输入，再继续”。
   例如 operator 批准“允许重启 `node-42`”后，
   LangGraph 可以把批准结果带回 graph。
   但主 process manager 还需要处理更多外部消息：
   BMC power event、provisioning result、供应商换线回执、rack validation result、
   调度器 drain 完成、人工 override 撤销等。
   这些事件需要 schema、鉴权、去重、顺序/并发处理、资源身份绑定和审计。
   Temporal Signals/Updates 也不自动解决业务语义，
   但它们是一手投递到 durable Workflow Execution 的 message entry。
   LangGraph 若通过 resume、webhook、自建 event router 或 store polling 注入事件，
   必须证明这些入口不会和 thread/resource identity、审批上下文、失败恢复路径混淆。
3. **fault tolerance 恢复 graph/node execution，资源级追平仍要成为过程契约。**
   retries、timeouts 和 error handlers 是有价值的执行恢复能力；
   但裸金属控制面还必须知道真实设备发生了什么。
   例如 graph node 调用 Redfish 重启 `node-42` 超时后重试，
   并不能说明机器是否已经重启、是否卡在 BIOS、是否进入 PXE、
   是否需要人工拔插电源线。
   Temporal Activity retry 也有同样风险；
   差异不是 Temporal 自动理解物理状态，
   而是 Activity 边界、Workflow/Child Workflow 状态和 Signal/Update 入口
   可以围绕“哪个长期过程对象正在等待哪个事件、哪个副作用已发出、
   下一步如何 reconcile”组织。
   LangGraph 方案若承担主过程控制路径，必须补齐同等的副作用记录、读后校验、
   幂等键、补偿和人工确认模型。

另外三类能力应写成证据边界或通用 POC gate，而不是 LangGraph 独有缺陷：

- **checkpoint/store 是 graph state/memory 持久化能力。**
  它有价值，但不能单独证明 resource-process audit、external inventory
  或局部追平已经成立。
  这与 Temporal Event History、Durable Task backend state、Airflow metadata DB
  都不是资源事实库是同一类共性边界。
- **time travel/fork 是诊断和受控分支能力。**
  它不是不能用于主控制路径；
  但只要 fork/replay 跨越真实副作用边界，
  就必须和 Temporal Reset、Durable orchestration 恢复后的后续 Activity、
  Airflow rerun/backfill 一样先 reconcile external inventory 与真实设备状态，
  并保护后续副作用节点不被无条件重放。
  这属于通用 side-effect guard，不是 LangGraph 能力不足。
- **Agent Server queue worker 证明的是 graph run execution queue。**
  它说明 LangGraph run 可以被队列化、worker 化、持久化执行；
  但不能单独证明 node/rack/fabric 资源过程调度、局部失败隔离和长期业务审计已经成立。
  若业务层把每个 resource process 映射成 thread/run，
  并实现事件路由、锁、追平和审计，
  queue worker 可以成为该方案的执行基础之一；
  但它本身不是主 process manager 适配性的充分证据。

因此，如果方案声称“LangGraph 做主 process manager”，
不能仅说“LangGraph 有持久化、HITL、fault tolerance 和 Agent Server queue”。
它必须正面回答：
长期资源身份在哪里；
外部事件如何投递到正确过程对象；
局部失败如何隔离和追平；
operator approval 如何进入审计链；
真实世界副作用如何被隔离、去重、补偿和保护。

如果 external inventory/resource graph 只保存领域事实、锁和审计投影，
而 LangGraph graph/thread 明确持有过程控制路径、事件解释、恢复策略和副作用边界，
那么不能仅因使用外部资源图否定 LangGraph。
但在现有证据下，LangGraph 更稳妥的定位仍是 AI diagnosis、operator copilot、
HITL decision support，或由主 process manager 调用的 agent automation adapter。
若 POC 证明“业务层 + LangGraph”能够稳定承担上述主过程控制路径，
并且在资源分区、事件路由、局部追平、审计和副作用保护上达到同等要求，
则应按新的证据重新评估。

## 后果

无论选择 Temporal、Azure Durable Functions / Durable Task、
Microsoft Agent Framework Durable Workflow Extension、Airflow 还是 LangGraph，
都必须建设 external inventory/resource graph、业务事件模型、副作用纪律、
dashboard projection 和迁移/版本纪律。
这些是裸金属 buildout 的共性工程前提，
不是任何单个候选的专属缺陷。

即使采用 Temporal 作为 reference architecture 或主 process manager，
也不是只部署 Temporal runtime。
在前述领域事实层和裸金属控制面基线之上，还应承诺建设以下配套能力：

1. **资源实体分区策略**：
   明确哪些对象用 Child Workflow 表示，哪些只作为 external state 引用。
2. **副作用纪律**：
   所有 Redfish/IPMI、provisioning、OS、Slurm、通知、AI Agent 调用都要有幂等键、
   读后校验、重试边界和补偿策略。
3. **运行中变更纪律**：
   Continue-As-New、Reset、Worker Versioning 和 blueprint schema 迁移必须按 Run
   边界、外部事实 reconcile 和人工审批处理。
4. **业务 dashboard projection**：
   不要把 Temporal UI 当作操作员产品界面；需要从 Temporal、inventory/resource graph
   和下层控制面投影业务状态。

如果组织仍要求在方案中使用 Airflow，且尚未证明 Airflow DagRun/TaskInstance
与业务层共同承载主过程控制路径，应在架构文档中把它标为被主 process manager
调用的 scheduler/executor/UI adapter，而不是把这个角色写成本文选型问题的答案。
若 POC 证明 Airflow 方案可承担这些主过程职责，应按新的证据重评。

如果组织要求在方案中使用 LangGraph，且尚未证明 LangGraph graph/thread
与业务层共同承载主过程控制路径，应先把它标为 agent/HITL adapter，
并明确哪些事件和决策回写到主 process manager 与 external inventory/resource graph。
若 POC 证明 LangGraph 方案可承担这些主过程职责，应按新的证据重评。

如果组织要求使用 Azure Durable Functions / Durable Task，应把它当作同批
durable orchestration 强候选，而不是外围 adapter。
但方案必须显式写清最终运行面是 Azure Functions plan 还是 standalone Durable Task SDK，
并解释 Durable Task Scheduler / storage provider、网络/private endpoint、
语言 SDK、external event / management API 交互模型、orchestration versioning、
业务 dashboard 和 external inventory/resource graph 的责任边界。

如果组织要求使用 Microsoft Agent Framework Durable Workflow Extension，
应先确认它是否承担主过程控制路径，还是只承担 agent/HITL 辅助层。
若承担，应把它当作 Azure / Durable Task 路线内的 Durable Task-backed
graph workflow 或 hybrid POC 候选，
并显式写清 Durable Extension 是否覆盖目标 workflow surface、chosen hosting/backend、
executor/activity/entity/sub-orchestration/external-event 映射、direct durable primitives
的接入方式、checkpoint 兼容性、agent/HITL 边界，以及 Agent Framework 中间层是否
增加不可接受的映射和诊断成本。
如果 graph / hybrid 亲自持有资源过程身份、事件解释、局部追平、补偿决策、
副作用边界和审计事实线，它可以作为主 baseline；
如果 AI diagnosis、multi-agent 和 HITL 只是辅助能力，它应被标为上层
agent/HITL/control adapter，而不是主 process manager。

## 重新审视触发条件

以下条件出现时，应重新评估这个决策：

- 决策 scope 从“主 process manager”缩小为“有限批次调度/执行/UI adapter”。
- 组织明确接受另一个 external domain process service 才是真正 process manager，
  Airflow 只承担被调用的 scheduler/executor。
- 组织明确接受另一个 external domain process service 或 durable orchestrator
  才是真正 process manager，LangGraph 只承担被调用的 agent/HITL adapter。
- Azure/Durable Task 的证据矩阵或 PoC 显示 orchestration instance/sub-orchestration、
  entity、external event、orchestration versioning、Durable Task Scheduler/backend
  和 private connectivity 比 Temporal reference architecture 更适合目标组织。
- 组织已经标准化 Microsoft Agent Framework Durable Extension / Durable Task，
  并且目标 workflow surface 明确运行在 Durable Extension-backed graph workflow 上，
  graph/executor/checkpoint 兼容性和 agent/HITL 集成约束不会削弱 process manager 目标。
  如果 graph workflow 同时亲自持有资源过程身份、事件解释、局部追平、
  补偿决策、副作用边界和审计事实线，该条件应触发 MAF 主 baseline 重评，
  而不是仅作 adapter。
- 团队没有 Temporal 运维经验，且无法承担 workflow versioning、Activity 幂等和 dashboard
  projection 的建设成本。
- 目标 buildout 场景被重新定义为短生命周期、批量验证或报表加工，
  而不是长期交互式资源状态机。
- POC 显示 Temporal 的建模、可观测性或运维成本高于 Airflow + 外部状态机组合。
- POC 显示 Airflow 方案在同等 external inventory/resource graph 和副作用纪律下，
  能用 DagRun/TaskInstance、event scheduling、deferral、HITL、backfill/catchup
  和 DAG version/reconciliation 纪律稳定承载长期过程控制路径。
- POC 显示 Azure Durable Functions / Durable Task 在明确 hosting/runtime/backend
  边界后，其 durable orchestration、external event、entity、versioning
  和运行面约束比 Temporal 更适合目标组织。
- POC 显示 Microsoft Agent Framework Durable Workflow Extension 的 graph workflow、
  executor dispatch、Durable Task-backed orchestration、external event 和 checkpoint/recover
  能稳定承载主过程控制路径，且中间层映射和诊断成本可接受；
  若 graph workflow 亲自持有资源过程身份、事件解释、局部追平、补偿决策、
  副作用边界和审计事实线，它可与 Temporal/Azure 作为同批主 baseline 比较。
- POC 显示 LangGraph graph/thread 明确持有长期控制路径、事件解释、局部追平、
  迁移策略和副作用边界，而不是由外部 domain process service 承担这些职责。

## POC 验证边界

在把本页判断转成采购或工程基线前，至少验证通用 gates：

- external inventory/resource graph 保存资源事实、锁、验收结果和业务审计投影。
- resource identity / process partition 能稳定表达 cluster、node、rack、fabric
  等长期过程对象。
- event schema、auth、dedup、ordering/concurrency 和 audit 能覆盖人工、供应商、
  BMC、provisioning、scheduler 和 validation 事件。
- 所有真实世界副作用都有幂等键、读后校验、重试边界、补偿和人工确认模型。
- replay、reset、fork、rerun、retry 或恢复只要跨越真实副作用边界，
  都必须先 reconcile external inventory 与真实设备状态，并保护后续副作用节点。
- 局部失败隔离、修复后追平、迁移/版本纪律和 dashboard projection 不依赖
  runtime UI 临时解释。

共同 gates 不是产品缺点清单。
候选附加验证要证明一手 runtime 对象如何满足这些 gates，
以及满足 gates 时是否需要把主过程控制逻辑外移：

- Temporal 单节点 workflow 覆盖 BMC read、firmware/BIOS 检查、OS provisioning、
  driver install 和 Slurm validation job。
- Temporal 10 个节点 Child Workflows 中部分失败时，未受影响节点继续，
  失败节点修复后可追平到集成门禁。
- Temporal Reset 前后必须先 reconcile 外部 inventory 与真实设备状态，
  危险 Activity 不能无条件重放。
- Temporal 方案必须同样验证 worker placement、Event History 增长、
  in-flight versioning、business dashboard projection 和目标运维成本；
  不能把 reference architecture 当成已通过的 winner baseline。
- 若有人主张 Airflow 可做主 process manager，POC 必须证明 Airflow 方案能解释
  长期资源身份、外部事件、局部失败传播、追平条件和物理副作用补偿；
  只证明 Dynamic Task Mapping、HITL、deferrable 或 event scheduling 可运行，
  只能证明它适合作为执行/调度层。
- Airflow 方案必须证明 DAG 代码变更、既有 DagRun、removed task、
  backfill/reprocessing/catchup
  不会破坏 buildout 过程审计；否则该方案仍不是合格的主 process manager。
- Azure Durable Functions 方案必须证明 orchestrator deterministic replay、durable
  timers、external events、entities、storage provider、hosting plan 和网络连通
  能承载目标 buildout 周期。
- Azure Durable Functions 方案必须把 Durable Functions 与 standalone Durable Task SDKs
  的 hosting model 选择写清楚；如果部署目标是 AKS、VM 或 on-premises，
  不能用 Azure Functions 触发器和内置 HTTP management APIs 偷换 standalone SDK 的能力。
- Azure Durable Functions 方案必须证明在途 orchestration instance 的代码/版本兼容、
  storage provider 恢复和后续 Activity 副作用保护，
  而不是把 deterministic replay 写成物理事实恢复。
- Azure Durable Task 方案必须验证 fixed/resource-derived instance ID 与 sub-orchestration
  是否会造成热点或延迟，external event 的 one-way async 语义如何补齐同步 command result，
  Durable Task Scheduler/backend/private endpoint 是否满足目标网络与可用性边界，
  以及 entities 是否只承载小粒度协调状态而不替代资源图。
- Microsoft Agent Framework Durable Workflow Extension 方案必须证明目标流程实际运行在
  Durable Extension-backed graph workflow 上，而不是只使用 standard checkpoints
  或未启用 Durable Extension 的 workflow surface。
- Microsoft Agent Framework Durable Workflow Extension 方案必须证明 graph workflow
  能稳定表达长期资源身份、运行中事件入口、局部失败追平、物理副作用边界和过程审计；
  只证明 executor/agent graph、checkpoint 或 HITL 可运行，只能证明它适合作为
  agent/HITL/workflow adapter。
- Microsoft Agent Framework Durable Workflow Extension 方案必须测试 chosen hosting/backend、
  stateless worker failover、Durable Task activity/entity/sub-orchestration dispatch、
  external event 等待、checkpoint 恢复、graph definition/checkpoint 兼容性，
  direct durable primitives / `DurableTaskClient` 的组合边界，
  以及 Agent Framework 中间层的观测和诊断成本。
- 如果把 MAF 作为主 baseline，POC 必须证明 Durable Extension-backed graph workflow
  或 hybrid 亲自持有资源过程身份、事件解释、局部失败追平、补偿决策、副作用边界和审计事实线；
  agent entity、request port、tool approval、LLM/tool side-effect 隔离和审计
  不能只是外围 adapter 能力。
- 若有人主张 LangGraph 可做主 process manager，POC 必须证明 LangGraph 方案能解释
  长期资源身份、领域事件、局部失败传播、追平条件、物理副作用补偿、过程审计
  和 graph/thread migration；只证明 persistence/checkpoint、interrupt/resume、
  time travel/fork、fault tolerance 或 Agent Server queue worker 可运行，
  只能证明这些是可用机制，不能单独证明它已经承担主过程控制路径。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| user | 用户在 2026-06-16 表示认可 `raw/10-ai-generated-drafts/2026-06-13-cluster-buildout-platform-selection-bare-metal-research-report.md` 中关于长期、交互式、事件驱动、资源实体导向 buildout process manager 的核心判断，并要求抽取 analysis pages。 | 确立本页的场景边界和用户认可的判断方向。 |
| user | 用户在 2026-06-16 纠正候选排序方式：“也许顺序其实应该调整，我也不确定，你不能假定就是这样了，我们应该先找证据再决定，不是开枪再画靶”。 | 支撑本页不把 Temporal 写成已证实采购 winner，并把 Azure Durable Task 与 MAF 重新纳入证据优先的同批候选比较。 |
| user | 用户在 2026-06-17 先收窄问题：“仅考虑对业务场景建模的扭曲程度……运维成本方面可以摊薄，AI方面属于收益不明确，对接起来也不复杂”；随后继续 challenge MAF Graph 反方观点，要求明确“集成度更高”到底带来什么额外价值。 | 确立 Temporal / MAF 建模扭曲子判断边界，并将 AI ergonomic 收益从“暂不计入”改为“纳入讨论但限定为 agent/HITL authoring 与 adapter 层收益”。 |
| user | 用户在 2026-06-17 进一步指出：裸金属控制面不是简单 shell 命令，很多节点可能需要人异步执行；并询问纯 Agent Graph 作为主控制面是否实际不成立，以及 Temporal 是否可以通过 agent、plan patch 和 Continue-As-New 承载计划修订。 | 确立本页对 MAF agent-graph 例外条件的进一步收窄，以及 Temporal 接入 agent 的架构边界。 |
| user | 用户在 2026-06-17 继续指出：Azure Durable Functions 的 orchestrator 本来就是手写，用 MAF 不代表不能在 orchestrator 层控制 Durable primitives；选择 MAF 恰恰是为了获得 Agent Framework 的可控 agent 能力，并要求基于 Azure Durable Extension 与 MAF 源码澄清 Direct Durable primitives。 | 触发本次撤回“MAF 天然弱于 direct Azure Durable Functions”的过强判断，并补充 Direct Durable primitives 与 MAF composition 边界。 |
| session | 本会话 `caa042f4-ce50-4fa6-93b5-e07f577d64a8` 中 `decision-semantics`、`decision-maf-fairness`、`decision-temporal-strength`、`decision-page-structure` 四个 GPT-5.5 审查代理。 | 支撑本次对“决策”段入口结构、Temporal 强度、MAF 条件和页面读者入口的重排；审查意见只作为结构和一致性校验，不作为第三方技术事实。 |
| session | 本会话 `caa042f4-ce50-4fa6-93b5-e07f577d64a8` 中 `azure-direct-primitives`、`maf-composition`、`maf-superset-skeptic`、`durable-maf-final` 四个 GPT-5.5 审查代理。 | 支撑本次对 Direct Durable primitives、MAF composition、strict superset 边界和 Azure / Durable Task 路线内 MAF 定位的对抗审查；技术事实仍回到 raw 源码。 |
| raw | [`2026-06-13-cluster-buildout-platform-selection-bare-metal-research-report.md`](../../raw/10-ai-generated-drafts/2026-06-13-cluster-buildout-platform-selection-bare-metal-research-report.md) | 非权威 AI 调研草稿；只作为线索和本页问题来源，不作为技术事实主证据。 |
| wiki | [工作流概念比较](workflow-concepts-comparison.md) | 提供控制表示面、执行解释器、状态真源、恢复模型、副作用边界和时间/触发语义的通用比较轴。 |
| wiki | [Temporal 与 MAF Durable Extension 的能力边界](temporal-vs-maf-durable-extension.md) | 提供 Temporal 与 MAF Durable Extension 在 Event History、Task Queue、Signal/Update/Query、Continue-As-New/Reset、graph durable adapter、RequestPort、agent entity 和 graph 语义保真边界上的直接比较。 |
| wiki | [Temporal Workflows 文档](../sources/temporal/workflows-docs.md) | Temporal Workflow Execution、Event History 和 replay 的基础语义。 |
| wiki | [Temporal Activities 文档](../sources/temporal/activities-docs.md) | Activity 作为外部 I/O 和副作用边界。 |
| wiki | [Temporal Message Passing 文档](../sources/temporal/message-passing-docs.md) | Signals、Updates 和 Queries 与运行中 Workflow 交互。 |
| wiki | [Temporal Timers and Start Delays 文档](../sources/temporal/timers-delays-docs.md) | Timer 作为 Workflow Execution 内部持久等待语义。 |
| wiki | [Temporal Child Workflows 文档](../sources/temporal/child-workflows-docs.md) | Child Workflow 按大工作负载或单资源分区。 |
| wiki | [Temporal Continue-As-New 文档](../sources/temporal/continue-as-new-docs.md) | Continue-As-New 的 Run 边界和 Event History 截断语义。 |
| wiki | [Temporal Reset 文档](../sources/temporal/reset-docs.md) | Reset 的历史前缀和新 execution 语义。 |
| wiki | [Temporal Worker Versioning 文档](../sources/temporal/worker-versioning-docs.md) | Worker version routing 与在途 execution 的版本边界。 |
| wiki | [Temporal 动态 AI Agent 博客](../sources/temporal/dynamic-ai-agents-blog.md) | Temporal 可用 durable workflow 承载动态 agent 模式，且模型/tool 调用仍落在 Workflow/Activity 边界内。 |
| wiki | [Azure Durable Functions Overview 文档](../sources/azure-durable-functions/overview-docs.md) | Durable Functions 作为 Azure Functions stateful workflow extension 的定位。 |
| wiki | [Durable Task Orchestrations 文档](../sources/azure-durable-functions/orchestrations-docs.md) | Durable orchestration、instance identity、event sourcing、execution history 和 replay 语义。 |
| wiki | [Durable Task Code Constraints 文档](../sources/azure-durable-functions/code-constraints-docs.md) | Orchestrator deterministic replay 与外部 I/O 边界。 |
| wiki | [Durable Task Timers 文档](../sources/azure-durable-functions/timers-docs.md) | Durable timers 和 timeout 语义。 |
| wiki | [Durable Task External Events 文档](../sources/azure-durable-functions/external-events-docs.md) | Orchestration external events 语义和单向异步限制。 |
| wiki | [Durable Task Entities 文档](../sources/azure-durable-functions/entities-docs.md) | Durable entities 小块状态与串行 operation 语义。 |
| wiki | [Durable Task Storage Providers 文档](../sources/azure-durable-functions/storage-providers-docs.md) | Durable Task runtime state backend 和 storage provider 边界。 |
| wiki | [Durable Task Instance Management 文档](../sources/azure-durable-functions/instance-management-docs.md) | Orchestration instance management APIs 与 instance ID 边界。 |
| wiki | [Durable Task Orchestration Versioning 文档](../sources/azure-durable-functions/orchestration-versioning-docs.md) | Durable Functions 与 Durable Task SDKs orchestration versioning 边界。 |
| wiki | [Durable Task Hosting Model 文档](../sources/azure-durable-functions/hosting-model-docs.md) | Durable Functions 与 standalone Durable Task SDKs 的 hosting model 差异。 |
| wiki | [Durable Task SDKs Overview 文档](../sources/microsoft-durable-task/sdk-overview-docs.md)、[Durable Task Scheduler 文档](../sources/microsoft-durable-task/scheduler-docs.md) | Standalone Durable Task SDKs 的 compute placement、Scheduler backend、dashboard、private connectivity 与 backend 边界。 |
| wiki | [Azure Functions Scale and Hosting 文档](../sources/azure-functions/scale-hosting-docs.md) | Azure Functions hosting plans、scale、资源、网络/容器支持和成本边界。 |
| raw | `raw/git/github.com/Azure/azure-functions-durable-extension/src/WebJobs.Extensions.DurableTask/ContextInterfaces/IDurableOrchestrationContext.cs:87-114,116-169,331-430,432-558`、`raw/git/github.com/Azure/azure-functions-durable-extension/src/WebJobs.Extensions.DurableTask/ContextInterfaces/IDurableOrchestrationClient.cs:117-338` | Azure Durable Functions direct orchestrator/client primitives：Continue-As-New、custom status、Durable HTTP、entity call/signal、sub-orchestration、timer、external event、entity lock、activity/retry、start/raise/manage/query/purge/restart。 |
| wiki | [Microsoft Agent Framework Durable Extension 文档](../sources/microsoft-agent-framework/durable-extension-docs.md) | Durable Task-backed execution、checkpoint/recover、HITL、Azure Functions 与 self-hosted worker、Durable Task Scheduler backend 边界。 |
| wiki | [Microsoft Agent Framework Durable Workflow Registration 源码](../sources/microsoft-agent-framework/durable-workflow-registration-source.md)、[Microsoft Agent Framework Durable Executor Dispatcher 源码](../sources/microsoft-agent-framework/durable-executor-dispatcher-source.md) | Durable graph workflows 到 orchestrations/activities/entities/sub-orchestrations/external events 的注册与 dispatch 映射。 |
| raw | `raw/git/github.com/microsoft/agent-framework/dotnet/src/Microsoft.Agents.AI.DurableTask/Workflows/DurableWorkflowRunner.cs:72,162-190,294-323,365-399,494-515`、`raw/git/github.com/microsoft/agent-framework/dotnet/src/Microsoft.Agents.AI.DurableTask/Workflows/EdgeRouters/DurableEdgeMap.cs:75-190`、`raw/git/github.com/microsoft/agent-framework/dotnet/src/Microsoft.Agents.AI.DurableTask/Workflows/DurableExecutorDispatcher.cs:51-66,104-125,172-185` | MAF durable graph runner 的 superstep 上限、message queue / fan-in 聚合、routing、activity/entity/sub-orchestration/external-event dispatch 和 RequestPort custom status / external event 行为。 |
| raw | `raw/git/github.com/microsoft/agent-framework/dotnet/src/Microsoft.Agents.AI.Workflows/AIAgentBinding.cs:14-38`、`raw/git/github.com/microsoft/agent-framework/dotnet/src/Microsoft.Agents.AI.DurableTask/DurableAIAgent.cs:36-39,89-140,147-168`、`raw/git/github.com/microsoft/agent-framework/dotnet/src/Microsoft.Agents.AI.DurableTask/AgentEntity.cs:32-151,197-214`、`raw/git/github.com/microsoft/agent-framework/dotnet/src/Microsoft.Agents.AI.DurableTask/AgentSessionId.cs:23-58`、`raw/git/github.com/microsoft/agent-framework/dotnet/src/Microsoft.Agents.AI.Hosting.AzureFunctions/BuiltInFunctions.cs:98-112,116-190` | MAF AIAgent binding、durable agent session/entity conversation history/TTL、RequestPort pending input projection 和 respond/RaiseEvent 行为。 |
| raw | `raw/git/github.com/microsoft/agent-framework/dotnet/src/Microsoft.Agents.AI.DurableTask/ServiceCollectionExtensions.cs:32-90,92-145,230-273`、`raw/git/github.com/microsoft/agent-framework/dotnet/src/Microsoft.Agents.AI.DurableTask/Workflows/DurableExecutorDispatcher.cs:51-88,104-125,139-157,172-185`、`raw/git/github.com/microsoft/agent-framework/dotnet/src/Microsoft.Agents.AI.DurableTask/DurableAgentContext.cs:21-49,80-122`、`raw/git/github.com/microsoft/agent-framework/dotnet/src/Microsoft.Agents.AI.DurableTask/Workflows/DurableActivityExecutor.cs:28-56`、`raw/git/github.com/microsoft/agent-framework/dotnet/src/Microsoft.Agents.AI.DurableTask/Workflows/DurableWorkflowContext.cs:19-99` | MAF Durable Extension 的 additive configuration、graph executor 到 Durable Task primitives 的映射、durable agent context 对 schedule/status/raise event 的暴露，以及 ordinary executor 通过 `IWorkflowContext` 运行的边界。 |
| wiki | [Microsoft Agent Framework Workflows 概览](../sources/microsoft-agent-framework/workflows-overview-docs.md)、[Microsoft Agent Framework WorkflowBuilder 文档](../sources/microsoft-agent-framework/workflow-builder-docs.md)、[Microsoft Agent Framework Functional Workflows 文档](../sources/microsoft-agent-framework/functional-workflows-docs.md) | Agent Framework workflows、graph workflow、executors、edges、superstep execution 与 functional workflow surface。 |
| wiki | [Microsoft Agent Framework Workflow Checkpoints 文档](../sources/microsoft-agent-framework/checkpoints-docs.md)、[Microsoft Agent Framework Workflow State 文档](../sources/microsoft-agent-framework/state-docs.md) | Checkpoint 捕获范围、恢复/迁移语境、workflow state 与 built workflow immutability。 |
| wiki | [Claude Code Dynamic Workflows 文档](../sources/claude-code/dynamic-workflows-docs.md)、[Claude Agent SDK Todo Tracking 文档](../sources/claude-code/todo-tracking-docs.md) | Claude Code dynamic workflows 中 script 持有 orchestration plan，以及 Agent SDK task/todo tracking 的受控任务状态更新语义。 |
| wiki | [Airflow DAG 文档](../sources/apache-airflow/dags-docs.md) | DAG、task dependencies、DagRun 和控制流基础语义。 |
| wiki | [Airflow Dag Run 文档](../sources/apache-airflow/dag-run-docs.md)、[Airflow Backfill 文档](../sources/apache-airflow/backfill-docs.md) | DagRun、catchup、backfill、reprocessing behavior 和历史区间 run 创建语义。 |
| wiki | [Airflow Scheduler 文档](../sources/apache-airflow/scheduler-docs.md) | scheduler、metadata DB、DagRun 和 TaskInstance 推进语义。 |
| wiki | [Airflow Dynamic Task Mapping 文档](../sources/apache-airflow/dynamic-task-mapping-docs.md) | runtime task fan-out 和 mapped task instances。 |
| wiki | [Airflow Deferrable Operators 文档](../sources/apache-airflow/deferrable-operators-docs.md) | task/operator deferral、triggerer 等待和状态传递限制。 |
| wiki | [Airflow Event-Driven Scheduling 文档](../sources/apache-airflow/event-scheduling-docs.md) | `BaseEventTrigger` 和 event-driven Dag scheduling 约束。 |
| wiki | [Airflow HITL 文档](../sources/apache-airflow/hitl-docs.md) | 人工输入、审批、分支选择和通知能力。 |
| wiki | [Airflow Task States 文档](../sources/apache-airflow/task-states-docs.md) | TaskInstance 状态、deferred、removed 和 heartbeat timeout 语义。 |
| wiki | [Airflow DAG File Processing 文档](../sources/apache-airflow/dagfile-processing-docs.md)、[Airflow DAG Serialization 文档](../sources/apache-airflow/dag-serialization-docs.md)、[Airflow DAG Bundles 文档](../sources/apache-airflow/dag-bundles-docs.md)、[Airflow DagRun verify_integrity 源码](../sources/apache-airflow/dagrun-verify-integrity-source.md) | DAG 文件处理、serialized DAG 调度视图、bundle versioning 和既有 DagRun task instance reconciliation 边界。 |
| wiki | [LangGraph Overview 文档](../sources/langgraph/overview-docs.md) | LangGraph long-running stateful agents/workflows 与 runtime 定位。 |
| wiki | [LangGraph Persistence 文档](../sources/langgraph/persistence-docs.md) | checkpointers、stores、threads/thread_id 等持久化语义。 |
| wiki | [LangGraph Interrupts 文档](../sources/langgraph/interrupts-docs.md) | `interrupt()`、resume 和 HITL 语义。 |
| wiki | [LangGraph Fault Tolerance 文档](../sources/langgraph/fault-tolerance-docs.md) | retries、timeouts 和 error handlers 的 graph/node execution 语义。 |
| wiki | [LangGraph Agent Server 文档](../sources/langgraph/agent-server-docs.md) | Agent Server persistence database、task queue 和 queue worker 边界。 |
| wiki | [LangGraph Graph Migrations 文档](../sources/langgraph/graph-migrations-docs.md) | existing thread 在新 graph definition 下恢复的受限边界。 |
| wiki | [LangGraph Time Travel 文档](../sources/langgraph/time-travel-docs.md) | checkpoint replay、fork 和 `update_state` 对后续执行路径的影响。 |
| wiki | [DMTF Redfish Standards 页面](../sources/dmtf/redfish-standards-page.md)、[Canonical MAAS README](../sources/canonical/maas-readme.md)、[OpenStack Ironic README](../sources/openstack/ironic-readme.md)、[Tinkerbell README](../sources/tinkerbell/readme.md) | 裸金属硬件管理、机器生命周期和 provisioning 控制面证据。 |
| wiki | [Foreman README](../sources/the-foreman/readme.md)、[Cobbler README](../sources/cobbler/readme.md)、[xCAT Documentation Index](../sources/xcat/docs-index.md)、[Metal3 Baremetal Operator API 文档](../sources/metal3/baremetal-operator-api.md)、[Slurm Overview 文档](../sources/slurm/overview-docs.md) | 生命周期管理、安装、集群管理、CRD 裸金属资源和作业调度控制面证据。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| 裸金属 Cluster Buildout 是现有 workflow 通用比较页之外的独立决策边界。 | 用户输入；raw 草稿；工作流概念比较。 | raw 草稿不是技术事实证据；本页仍需由一手 source projections 支撑。 |
| 平台选型应比较长期过程对象、状态真源、外部事件入口、等待模型、副作用边界、局部失败和流程演进，而不是只比较 task 执行能力。 | 工作流概念比较；Temporal、Azure Durable Functions / Durable Task、Microsoft Agent Framework Durable Extension、Airflow 和 LangGraph source pages。 | 这是本 wiki 的综合分析框架，不是厂商官方分类。 |
| Temporal 应作为核心资源过程建模的主 baseline / reference architecture 强锚点，但不能因此被写成已证实的采购或工程总评第一名；Azure Durable Functions / Durable Task 应继续作为同批 durable orchestration 强候选对照。 | Temporal、Azure Durable Functions / Durable Task、Microsoft Agent Framework Durable Extension、Durable Task SDKs、Durable Task Scheduler source pages；用户对“先找证据再决定”的纠正；多路 GPT-5.5 决策段审查。 | 这是当前证据约束下的建模语义与候选定位，不是采购结论；仍需目标场景 PoC；Temporal-vs-MAF 子结论不覆盖 Azure Durable Task。 |
| Temporal 的 durable Workflow Execution、message passing、Timer、Activity 和 Child Workflow 适合作为核心资源过程建模的第一锚点。 | Temporal Workflows、Activities、Message Passing、Timers、Child Workflows source pages。 | Temporal 不保存全部领域事实；Signals/Updates 不替代完整 command gateway，也不自动处理物理副作用幂等、补偿和业务 dashboard；它仍需验证 worker placement、history growth、versioning 和运维成本。 |
| 若目标函数只比较 Temporal 与 MAF Durable Extension 对裸金属主 process manager 业务模型的扭曲程度，并把运维成本、组织栈和云托管便利性留给后续 PoC，同时把 AI ergonomic 收益限定为 agent/HITL authoring 与 adapter 层收益，Temporal 在长期资源过程身份、资源分区、运行中事件入口、局部失败追平、物理副作用边界、历史治理、版本演进和过程审计等核心资源过程维度上显著更少扭曲。 | 用户在 2026-06-17 收窄问题并随后要求复核 MAF “集成度更高”的额外价值；Temporal 与 MAF Durable Extension 的能力边界；Temporal Workflows、Activities、Message Passing、Child Workflows、Continue-As-New、Reset、Worker Versioning source pages；MAF Durable Extension、Durable Workflow Registration、Durable Executor Dispatcher source pages；MAF durable runner / edge map / dispatcher raw 源码；MAF AIAgentBinding、DurableAIAgent、AgentEntity、AgentSessionId 和 Azure Functions BuiltInFunctions raw 源码。 | 这是严格收窄后的建模语义判断，不是采购或工程总评，也不是所有业务建模子维度的无条件全面胜出；不覆盖 Azure Durable Task；两者仍共同需要 external inventory/resource graph、幂等、副作用读回、补偿、审计和 dashboard。 |
| 裸金属控制面不是 shell 命令、很多节点需要人异步执行，并不让纯 Agent Graph 自动成为主 process manager；这些因素通常更需要 durable/event-sourced process manager 来持有事件入口、资源绑定、审批版本、审计和恢复后追平。 | 用户在 2026-06-17 的进一步问题；裸金属工具链 source pages；Temporal Message Passing、Activities、Child Workflows source pages；MAF Durable Extension、Durable Executor Dispatcher 和 RequestPort 相关源码证据。 | 如果 MAF Durable Extension-backed graph / hybrid 亲自持有长期资源过程身份、事件解释、局部追平、补偿决策、副作用边界和审计事实线，而不是只做辅助 agent/HITL surface，则仍可作为主 baseline。 |
| Temporal 接入 agent 的正确边界是 agent 作为 Activity、Child Workflow 或外部 agent service 参与；agent 生成的 plan/resource graph 变更应作为不可信 `PlanPatch` 经 command API 与 Update/Signal 进入 Workflow，Workflow 在受控边界调用 Continue-As-New 交接显式状态。 | Temporal 动态 AI Agent 博客；Temporal Activities、Message Passing、Continue-As-New、Worker Versioning source pages；用户在 2026-06-17 的架构假设。 | Agent 不应在 Workflow replay 路径内直接做 LLM/tool I/O；Continue-As-New 不是 agent 直接调用的改图 API，也不是物理回滚或任意计划迁移；外部鉴权、schema、policy、inventory reconcile、幂等和人工审批仍需设计。 |
| 公开实践证据更支持“稳定外层 orchestration + 受控计划/任务状态更新”，而不是 agent 在生产 workflow 中任意自修改 topology。 | Claude Code Dynamic Workflows 文档；Claude Agent SDK Todo Tracking 文档；Microsoft Agent Framework Workflow State 与 Checkpoints 文档；Temporal Dynamic Workflow 与 deterministic constraints 相关 source pages。 | Claude Code 是软件工程 agent 编排产品，不直接等同裸金属 buildout；该主张是跨来源机制归纳，不是所有 agent workflow 框架的统计结论。 |
| Temporal Reset、Continue-As-New 和 Worker Versioning 不能被写成物理回滚、任意计划迁移或自动升级。 | Temporal Reset、Continue-As-New、Worker Versioning source pages。 | 这些机制仍可作为受约束的恢复、历史截断和版本路由工具。 |
| Azure Durable Functions / Durable Task 具备 durable orchestration、activity、timer、external event、entity、event sourcing、checkpoint/replay、sub-orchestration、instance identity、instance management 和 orchestration versioning 等与主 process manager 相邻的能力，因此应作为与 Temporal 同批对照的强候选。 | Azure Durable Functions Overview、Durable Task Orchestrations、Timers、External Events、Entities、Instance Management、Orchestration Versioning source pages。 | Durable Functions 与 Temporal 都需要外部事实层、幂等和 replay discipline；真实差异在 command model、hosting/backend、versioning rollout、观察和运维边界。 |
| Azure Durable Functions / Durable Task 的核心差异是 Azure Functions 产品面、standalone Durable Task SDKs、Durable Task Scheduler managed backend、语言 SDK 状态和 private connectivity 必须先分清。 | Durable Task Hosting Model、Durable Task SDKs Overview、Durable Task Scheduler、Azure Functions Scale and Hosting、Durable Task Storage Providers source pages。 | 本页没有实测不同 hosting/backend、private endpoint、air-gapped 约束或网络环境下的性能和运维成本。 |
| Durable orchestrator replay、storage provider、entities、external events、orchestration versioning 和 management APIs 是 durable runtime 语义与边界；在裸金属 buildout 中，它们必须与 external inventory/resource graph、业务事件契约和副作用纪律组合使用，不能单独证明或否定候选资格。 | Durable Task Orchestrations、Code Constraints、Storage Providers、External Events、Entities、Instance Management、Orchestration Versioning source pages；裸金属工具链 source pages。 | 这些不是 Azure 独有缺陷；也不能被写成 Azure 已自动满足业务 command gateway、资源图或物理副作用安全。 |
| Direct Durable primitives 是 Durable Functions / Durable Task 的 direct orchestrator/client/entity surface，不是“不用 MAF”的同义词；MAF Durable Extension 可以作为 Durable Task-backed graph/agent/HITL composition 层组合这些能力，但 MAF graph surface 不是 direct primitives 的 strict superset。 | Azure Durable Extension direct context/client raw 源码；MAF ServiceCollectionExtensions、DurableExecutorDispatcher、DurableAgentContext、DurableActivityExecutor、DurableWorkflowContext raw 源码；Azure/MAF 关系页。 | 这是源码层边界判断；普通 MAF executor 不自动拥有完整 `TaskOrchestrationContext`，复杂 direct primitives 需要通过 graph mapping、agent/tool context、service layer、custom orchestrator 或 hybrid composition 进入。 |
| Microsoft Agent Framework Durable Workflow Extension 具备 Durable Task-backed graph workflow、checkpoint/recover、activity/entity/sub-orchestration/external event dispatch 和多 host/stateless worker 恢复证据；在 Agent Framework control 是一等需求时，它应作为 Azure / Durable Task 路线内的优先 POC 或 hybrid 候选。 | Microsoft Agent Framework Durable Extension、Durable Workflow Registration、Durable Executor Dispatcher、Workflows Overview、WorkflowBuilder、Functional Workflows、Durable Task Scheduler source pages；MAF composition raw 源码；Direct Durable primitives raw 源码。 | 这些证据支撑的是 Durable Extension-backed graph/hybrid 方案；不能自动外推到 standard checkpoints、functional workflow surface 或未启用 Durable Extension 的 core workflow；self-host worker 仍连接 Durable Task Scheduler backend；是否作为主 baseline 取决于 graph/hybrid 是否亲自承担主过程职责。 |
| Microsoft Agent Framework Durable Workflow Extension 的真实差异在于 Durable Task 之上的 Agent Framework graph/executor/superstep/agent entity 抽象层：它能减少 graph runner、agent session persistence、pending input discovery/respond loop 和 AI/HITL authoring surface 胶水，但不会自动替代主 process manager 的 PlanPatch schema、command API、鉴权、幂等、资源绑定、reconcile、补偿、审计和 dashboard projection。 | Microsoft Agent Framework Workflows Overview、WorkflowBuilder、Functional Workflows、Workflow Checkpoints、Workflow State、Durable Executor Dispatcher、Durable Extension source pages；MAF AIAgentBinding、DurableAIAgent、AgentEntity、AgentSessionId、DurableAgentContext 和 Azure Functions BuiltInFunctions raw 源码；Temporal Child Workflows、Message Passing、Continue-As-New、Worker Versioning source pages。 | 资源分区是本文裸金属 buildout 架构映射，不是 Microsoft 或 Temporal 针对该场景的官方推荐架构；MAF 的 agent/HITL 优势是 authoring/control/runtime ergonomic 与状态放置优势，只有当 POC 证明 graph/hybrid 持有主过程控制职责时才转化为主 process manager 价值。 |
| Airflow 的 Dynamic Task Mapping、Deferrable Operators、Event-Driven Scheduling、HITL、TaskInstance 状态、DagRun/catchup/backfill、DAG processing/serialization、bundle versioning 和 `DagRun.verify_integrity` 能证明它有等待、触发、人工输入、fan-out、历史区间重处理、部署版本和受控 DagRun reconciliation 能力；但这些机制的一手对象围绕 DAG/DagRun/TaskInstance/schedule/data interval，作为裸金属主 process manager 时比 Temporal Workflow/Child Workflow/Signals/Updates/Run 边界更容易把长期资源过程压扁成调度图重处理问题。 | Airflow DAG、Dag Run、Backfill、Scheduler、Dynamic Task Mapping、Deferrable Operators、Event-Driven Scheduling、HITL、Task States、DAG File Processing、DAG Serialization、DAG Bundles、DagRun verify_integrity source pages；Temporal Child Workflows、Message Passing、Reset、Continue-As-New、Worker Versioning source pages。 | 事件 schema、reconcile、迁移、副作用和外部事实层是共同 gates；本页判断的是在共同 gates 之外哪个 runtime 的一手建模锚点更自然。 |
| Airflow 的核心状态对象是 DagRun/TaskInstance/mapped task/deferred task 等 scheduler/task execution 状态，不应直接替代裸金属资源事实。 | Airflow DAG、Scheduler、Task States、Deferrable Operators source pages。 | Airflow 可以通过 task 读写外部领域状态；本页反对的是把 Airflow metadata DB 当领域真源。 |
| LangGraph 的 persistence、interrupt/resume、fault tolerance、Agent Server、graph migrations 和 time travel 证明它能运行长期 stateful agent graph/thread；但现有证据的建模重心是 graph/thread/run/checkpoint/store，而不是一手 durable resource process identity、child execution 和 workflow message entry。 | LangGraph Overview、Persistence、Interrupts、Fault Tolerance、Agent Server、Graph Migrations、Time Travel source pages；Temporal Workflows、Message Passing、Child Workflows source pages。 | Temporal 也需要业务层定义资源含义；差异不是“谁自动理解资源”，而是现有一手证据分别提供了哪些过程建模锚点。 |
| LangGraph 作为主 process manager 的 POC 必须证明 graph/thread 明确持有长期控制路径、事件解释、局部追平、审计、迁移策略和副作用边界；否则更稳妥的定位是 AI diagnosis、operator copilot、HITL decision support 或 agent automation adapter。 | LangGraph Persistence、Interrupts、Fault Tolerance、Time Travel、Agent Server source pages；Temporal Reset、Activities、Message Passing、Child Workflows source pages。 | checkpoint/store、time travel/fork 和 Agent Server queue worker 是可用机制或证据边界，不是 LangGraph 独有缺陷；不能单独外推为主 process manager 适配性。 |
| external inventory/resource graph/audit store、业务事件模型、副作用纪律、dashboard projection 和迁移/版本纪律是裸金属 buildout 的共性 POC gates，不是任何单个候选的专属缺陷；但共同 gates 不能洗掉 runtime 原生模型差异，若另一个 domain process service 持有长期过程状态、事件解释、局部追平和补偿决策，它才是主 process manager。 | Temporal、Azure Durable Functions、Microsoft Agent Framework、Airflow、LangGraph source pages；裸金属工具链 source pages。 | 具体数据模型、锁协议和审计 schema 需另行设计；使用这些共性前提本身不能证明某个候选不适合作为主 process manager，也不能证明某个 runtime 已经承担主过程控制路径。 |
| Redfish、MAAS、Ironic、Tinkerbell、Foreman、Cobbler、xCAT、Metal3 和 Slurm 不是无状态命令集合，而是协议、控制面、资源模型或调度系统，应被上层 process manager 协调和观察。 | DMTF Redfish、MAAS、Ironic、Tinkerbell、Foreman、Cobbler、xCAT、Metal3、Slurm source pages。 | 这些工具覆盖面、成熟度、项目状态和适用性不同；本页只用它们支撑“下层领域控制面”边界。 |
| 本页判断仍需要 POC、运维和组织约束验证后才能变成采购或工程基线。 | 用户输入；raw 草稿边界；各 source pages 的限制。 | 当前没有实测数据、规模参数、团队经验、成本模型或 UI/运维成熟度评估。 |
