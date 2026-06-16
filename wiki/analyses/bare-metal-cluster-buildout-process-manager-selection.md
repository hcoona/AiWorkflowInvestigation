---
schema_version: 2
page_type: analysis
title: "裸金属 Cluster Buildout 的 Process Manager 平台选型"
status: active
created: 2026-06-16
updated: 2026-06-16
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
默认优先评估 Temporal；Azure Durable Functions / Durable Task 与 Microsoft Agent
Framework Durable Workflow Extension 是相邻的 durable orchestration 候选，
但必须连同 hosting/runtime、storage backend、语言、框架 surface 和运维约束一起评估；
Apache Airflow 与 LangGraph 不应被写成同一 scope 下的主 process manager 等价方案。

这里的核心抽象不是“谁能跑更多 task”，而是一次 buildout 是否需要承载：
长期运行、交互式事件、资源实体导向的局部状态、真实世界副作用、局部失败恢复、
人工/供应商/AI Agent 介入，以及跨节点、机架、网络、固件、OS、集群资源管理和验收的追平。
在这个抽象下，Temporal 更适合作为主过程管理地基；
Azure Durable Functions 与 Microsoft Agent Framework Durable Workflow Extension
有足够接近的 durable orchestration 语义，值得进入 POC；
Airflow 的有限 DAG 调度、批处理、审批入口或报表能力，LangGraph 的 stateful
agent graph、HITL 和 checkpoint 能力，都不能被写成同一 scope 下的等价答案。
如果长期领域状态、事件解释、局部失败追平和物理副作用补偿
都由这些框架之外的系统负责，
那么真正的 process manager 是那个外部系统，
这些框架只是它调用的执行、展示或 agent adapter。

这个决策是条件性技术判断，不是最终采购结论。
它不覆盖 POC、压测、运维成本、团队熟练度、目标版本许可、UI 成熟度、
组织已有平台投资、框架版本成熟度或供应商支持。
但在本文 scope 内，组织已有 Airflow 或 Airflow 能运行若干 buildout 子流程，
组织已有 LangGraph/agent platform 能处理若干人工与 AI 子流程，
或组织已有 Microsoft Agent Framework，都不能直接推出它们适合做主 process manager。

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

### Temporal 的主 process manager 适配点

Temporal 的优势在于 Workflow Execution 是长期、durable 的过程对象；
Event History 支撑 replay 恢复控制状态；
Signals/Updates 可以把外部消息送入运行中的 Workflow Execution；
Timer 可以表达 execution 内部的持久等待；
Activity 是外部 I/O 和真实世界副作用的边界；
Child Workflow 可以按 host、node、rack、fabric 或 validation domain
把长期过程拆成资源实体相关的子执行。

在 durable orchestration runtime 层，这较直接匹配裸金属 buildout 的主过程管理问题：

- 一次 cluster buildout 可以是可寻址的长期 Workflow Execution。
- 单节点、机架或 fabric 的处理可以通过 Child Workflow 隔离历史、等待、重试和局部失败。
- BMC/Redfish、MAAS/Ironic/Tinkerbell、Foreman/Cobbler/xCAT、Slurm、
  通知和 AI Agent 调用应落在 Activity 或外部事件边界。
- 人工确认、供应商回复、现场操作结果和计划变更请求可以通过 Signals/Updates
  进入运行中的过程对象。
- 在前述领域事实层之外，Temporal 保存过程级状态、控制路径、事件入口和可审计执行历史。

必须降调的点同样重要：
Temporal Reset 不是物理回滚；
Continue-As-New 是 Run 边界状态交接和 Event History 截断点，不是任意计划迁移魔法；
Worker Versioning 是 worker/deployment routing 与 replay-safe 升级机制，
不自动迁移已发生的物理副作用；
Activity retry 不是 exactly-once。
所有真实设备操作仍必须通过幂等键、状态读回、外部锁、补偿流程和人工确认保护。

### Azure Durable Functions / Durable Task 的候选定位

Azure Durable Functions / Durable Task 应被视为接近 Temporal 的 durable
orchestration 强候选，而不是按 Airflow 或普通 agent graph 的标准排除。
在同等 external inventory/resource graph、业务事件 schema、幂等键、读回校验、
锁和补偿纪律下，它与 Temporal 的相似点非常实质：
orchestration instance 可以承载长期过程身份；
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

因此，MAF Durable Workflow Extension 不能被归入 Airflow/LangGraph 式外围候选。
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
把这些能力放在同一框架中可能比 Temporal + 独立 agent platform 减少集成负担。
但这只有在 MAF 自己承载 process-level control path 时才成立。
若长期资源状态、领域事件解释、局部失败追平、补偿决策和业务审计
仍由另一个 service 持有，
那么那个 service 才是主 process manager，
MAF Durable Workflow Extension 只是更强的 agent/HITL/durable workflow adapter。

### Airflow 作为主 process manager 的不匹配点

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
而在于这些能力组合后是否自然承载长期资源过程：

1. **Dynamic Task Mapping 是有限集合展开，不是长期拓扑演进。**
   例如 `discover_nodes` 产出 10 台 host，Airflow scheduler 可以为
   `provision(host)` 创建 10 个 mapped TaskInstances。
   这能表达“当前这批 host 扇出执行”。
   但如果两天后新增一个 rack、替换一台机器、某个 switch port 修复后需要只追平受影响节点，
   Dynamic Task Mapping 本身并不维护“host/rack/fabric 是长期过程对象”的身份和演进。
   Temporal 也不会自动理解拓扑；
   但 Child Workflow 可用 host/node/rack 等资源身份作为 Workflow ID 或分区边界，
   再用 Signals/Updates 把修复、追加和审批事件送入运行中的过程对象。
   因此在同样需要业务建模的前提下，Temporal 的资源过程分区语义更贴近这个问题。
2. **HITL、deferrable 和 event-driven scheduling 是等待/触发/审批入口，不是资源追平模型。**
   Airflow HITL 可以让 DAG 暂停等待人工输入；
   deferrable operator 可以释放 worker slot 等待 trigger；
   event-driven scheduling 可以基于符合 `BaseEventTrigger` 的事件触发 DagRun。
   这些能力有价值，但它们更自然地落在 TaskInstance 等待、DAG 分支或新 DagRun 入口。
   资源依赖传播、局部失败追平和物理副作用补偿仍要由业务控制路径显式实现。
   Temporal 也不自动解决这些业务问题；
   但 Signals/Updates/Timers 直接进入长期 Workflow Execution，
   Activity 明确隔离真实世界副作用，
   所以同一套业务逻辑更容易围绕“这个 cluster/node/rack 过程现在处于什么状态、收到什么事件、下一步怎么追平”来建模。
3. **DAG 版本、在途 DagRun、backfill/catchup 和 removed task 是调度图迁移纪律，不是物理过程迁移。**
   Airflow 的 DAG file processing、serialized DAG、DAG bundle versioning、
   `DagRun.verify_integrity`、backfill 和 catchup 处理的是 scheduler 看到的 DAG 版本、
   TaskInstance reconciliation 以及历史 logical date 的 DagRun 创建/重处理。
   对裸金属 buildout 来说，这些机制一旦重跑或补跑，就可能触发刷固件、装 OS、
   改 BIOS、重启等真实副作用，所以必须单独证明不会破坏过程审计和物理安全。
   Temporal 同样有迁移纪律：
   deterministic replay、Continue-As-New、Reset 和 Worker Versioning 都有限制，
   Reset 也不是物理回滚。
   差异是 Temporal 的纪律围绕 Workflow Execution/Event History/Run 边界展开，
   更接近“一个长期过程对象如何演进和恢复”；
   Airflow 的纪律围绕 DAG 代码、DagRun、TaskInstance 和 schedule/data interval 展开，
   更容易把真实资源过程压扁成调度图重处理问题。

### LangGraph 作为主 process manager 的不匹配点

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

在现有证据下，LangGraph 的主要风险应这样表述：

1. **资源过程身份不是 LangGraph 的一手建模中心。**
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
2. **checkpoint/store 的边界是共性纪律；真正问题是能否承担过程审计与重放语义。**
   不应把“checkpoint/store 不是资源事实库”单独写成 LangGraph 缺点。
   Temporal Event History、Durable Task backend state、Airflow metadata DB
   也都不是资源事实库。
   external inventory/resource graph 仍应保存资源事实、锁、验收结果和业务审计投影。
   对 LangGraph 的关键问题是：
   checkpoint 记录的 graph state、thread state、memory 和 fork/replay 语义，
   是否足以成为主过程控制路径的审计与恢复依据。
   如果它只说明“agent graph 可以从某个 checkpoint 继续”，
   还不足以说明“裸金属 buildout 的长期过程对象可以被审计、迁移、局部追平并安全恢复”。
   方案需要明确哪些事实进入 external inventory，
   哪些决策进入过程日志，
   哪些 checkpoint 只用于 agent execution recovery，
   以及 operator 如何解释一次失败、重试、人工批准和后续追平。
3. **HITL pause/resume 不等于完整业务事件入口。**
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
4. **fault tolerance 覆盖 graph/node execution，不自动覆盖物理副作用追平。**
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
5. **time travel/fork 不能被误写成安全的物理回滚或过程迁移。**
   LangGraph time travel/fork 可用于 checkpoint replay、分支实验或诊断；
   但后续 graph node 可能重新执行 LLM/API/tool calls。
   对裸金属来说，这可能意味着重复通知、重复调用 provisioning API，
   甚至重复触发固件、BIOS、power、PXE 等危险副作用。
   Temporal Reset 也不是物理回滚；
   两者都必须先 reconcile external inventory 与真实设备状态。
   这里的差异是：
   Temporal Reset 明确围绕 Workflow history 前缀和新的 execution 讨论；
   LangGraph fork 更偏 graph checkpoint 分支执行。
   如果 LangGraph 位于主控制路径，
   POC 必须证明 fork/replay 前后的副作用保护、审批继承、事件去重和审计解释。
6. **Agent Server queue worker 只证明 run-level graph execution queue。**
   文档支撑 queue worker 获取 run、执行 graph code 并写 checkpoints；
   不能由此推出它提供 node/rack/fabric 级资源过程调度、局部失败隔离或长期业务审计。
   例如 queue worker 能把 `buildout-123` 这个 run 分配给某个 worker 执行 graph；
   但这不同于调度 `rack-7` 中 40 台机器的局部追平窗口、锁和验收门禁。
   Temporal Worker 也不是资源调度器；
   Temporal 的适配点是 Workflow Execution、Child Workflow、Activity 和 message entry
   提供的 durable process anchors。

因此，如果方案声称“LangGraph 做主 process manager”，
不能仅说“LangGraph 有持久化、HITL、fault tolerance 和 Agent Server queue”。
它必须正面回答：
长期资源身份在哪里；
外部事件如何投递到正确过程对象；
局部失败如何隔离和追平；
operator approval 如何进入审计链；
真实世界副作用如何被隔离、去重、补偿和保护；
checkpoint/fork/replay 如何不破坏过程审计。

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

即使采用 Temporal 作为主 process manager，也不是只部署 Temporal runtime。
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

如果组织要求使用 Azure Durable Functions，应把它当作 Temporal 的 durable
orchestration 近邻候选，而不是外围 adapter。
但方案必须显式写清最终运行面是 Azure Functions plan 还是 standalone Durable Task，
并解释 storage provider、网络、冷启动/常驻实例、语言 SDK、external event
交互模型、业务 dashboard 和 external inventory/resource graph 的责任边界。

如果组织要求使用 Microsoft Agent Framework Durable Workflow Extension，
应先确认它是否承担主过程控制路径。
若承担，应把它当作 Durable Task-backed graph workflow POC 候选，
并显式写清 Durable Extension 是否覆盖目标 workflow surface、chosen hosting/backend、
executor/activity/entity/sub-orchestration/external-event 映射、checkpoint 兼容性、
agent/HITL 边界，以及 Agent Framework 中间层是否增加不可接受的映射和诊断成本。
若不承担，它应被标为 agent/HITL/workflow adapter，而不是主 process manager。

## 重新审视触发条件

以下条件出现时，应重新评估这个决策：

- 决策 scope 从“主 process manager”缩小为“有限批次调度/执行/UI adapter”。
- 组织明确接受另一个 external domain process service 才是真正 process manager，
  Airflow 只承担被调用的 scheduler/executor。
- 组织明确接受另一个 external domain process service 或 durable orchestrator
  才是真正 process manager，LangGraph 只承担被调用的 agent/HITL adapter。
- 组织已经标准化 Azure Functions / Durable Task，并且目标 hosting/runtime
  边界清晰，网络、storage provider、语言 SDK、监控和成本约束不会削弱
  process manager 目标。
- 组织已经标准化 Microsoft Agent Framework Durable Extension / Durable Task，
  并且目标 workflow surface 明确运行在 Durable Extension-backed graph workflow 上，
  graph/executor/checkpoint 兼容性和 agent/HITL 集成约束不会削弱 process manager 目标。
- 团队没有 Temporal 运维经验，且无法承担 workflow versioning、Activity 幂等和 dashboard
  projection 的建设成本。
- 目标 buildout 场景被重新定义为短生命周期、批量验证或报表加工，
  而不是长期交互式资源状态机。
- POC 显示 Temporal 的建模、可观测性或运维成本高于 Airflow + 外部状态机组合。
- POC 显示 Airflow 方案在同等 external inventory/resource graph 和副作用纪律下，
  能用 DagRun/TaskInstance、event scheduling、deferral、HITL、backfill/catchup
  和 DAG version/reconciliation 纪律稳定承载长期过程控制路径。
- POC 显示 Azure Durable Functions / Durable Task 在明确 hosting/runtime 边界后，
  其 durable orchestration、external event、entity 和运行面约束比 Temporal
  更适合目标组织。
- POC 显示 Microsoft Agent Framework Durable Workflow Extension 的 graph workflow、
  executor dispatch、Durable Task-backed orchestration、external event 和 checkpoint/recover
  能稳定承载主过程控制路径，且中间层映射和诊断成本可接受。
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
- 局部失败隔离、修复后追平、迁移/版本纪律和 dashboard projection 不依赖
  runtime UI 临时解释。

候选专属 gates 至少包括：

- Temporal 单节点 workflow 覆盖 BMC read、firmware/BIOS 检查、OS provisioning、
  driver install 和 Slurm validation job。
- Temporal 10 个节点 Child Workflows 中部分失败时，未受影响节点继续，
  失败节点修复后可追平到集成门禁。
- Temporal Reset 前后必须先 reconcile 外部 inventory 与真实设备状态，
  危险 Activity 不能无条件重放。
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
  以及 Agent Framework 中间层的观测和诊断成本。
- 若有人主张 LangGraph 可做主 process manager，POC 必须证明 LangGraph 方案能解释
  长期资源身份、领域事件、局部失败传播、追平条件、物理副作用补偿、过程审计
  和 graph/thread migration；只证明 persistence、interrupt/resume、fault tolerance
  或 Agent Server queue worker 可运行，只能证明它适合作为 agent/HITL adapter。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| user | 用户在 2026-06-16 表示认可 `raw/10-ai-generated-drafts/2026-06-13-cluster-buildout-platform-selection-bare-metal-research-report.md` 中关于长期、交互式、事件驱动、资源实体导向 buildout process manager 的核心判断，并要求抽取 analysis pages。 | 确立本页的场景边界和用户认可的判断方向。 |
| raw | [`2026-06-13-cluster-buildout-platform-selection-bare-metal-research-report.md`](../../raw/10-ai-generated-drafts/2026-06-13-cluster-buildout-platform-selection-bare-metal-research-report.md) | 非权威 AI 调研草稿；只作为线索和本页问题来源，不作为技术事实主证据。 |
| wiki | [工作流概念比较](workflow-concepts-comparison.md) | 提供控制表示面、执行解释器、状态真源、恢复模型、副作用边界和时间/触发语义的通用比较轴。 |
| wiki | [Temporal Workflows 文档](../sources/temporal/workflows-docs.md) | Temporal Workflow Execution、Event History 和 replay 的基础语义。 |
| wiki | [Temporal Activities 文档](../sources/temporal/activities-docs.md) | Activity 作为外部 I/O 和副作用边界。 |
| wiki | [Temporal Message Passing 文档](../sources/temporal/message-passing-docs.md) | Signals、Updates 和 Queries 与运行中 Workflow 交互。 |
| wiki | [Temporal Timers and Start Delays 文档](../sources/temporal/timers-delays-docs.md) | Timer 作为 Workflow Execution 内部持久等待语义。 |
| wiki | [Temporal Child Workflows 文档](../sources/temporal/child-workflows-docs.md) | Child Workflow 按大工作负载或单资源分区。 |
| wiki | [Temporal Continue-As-New 文档](../sources/temporal/continue-as-new-docs.md) | Continue-As-New 的 Run 边界和 Event History 截断语义。 |
| wiki | [Temporal Reset 文档](../sources/temporal/reset-docs.md) | Reset 的历史前缀和新 execution 语义。 |
| wiki | [Temporal Worker Versioning 文档](../sources/temporal/worker-versioning-docs.md) | Worker version routing 与在途 execution 的版本边界。 |
| wiki | [Azure Durable Functions Overview 文档](../sources/azure-durable-functions/overview-docs.md) | Durable Functions 作为 Azure Functions stateful workflow extension 的定位。 |
| wiki | [Durable Task Orchestrations 文档](../sources/azure-durable-functions/orchestrations-docs.md) | Durable orchestration、instance identity、event sourcing、execution history 和 replay 语义。 |
| wiki | [Durable Task Code Constraints 文档](../sources/azure-durable-functions/code-constraints-docs.md) | Orchestrator deterministic replay 与外部 I/O 边界。 |
| wiki | [Durable Task Timers 文档](../sources/azure-durable-functions/timers-docs.md) | Durable timers 和 timeout 语义。 |
| wiki | [Durable Task External Events 文档](../sources/azure-durable-functions/external-events-docs.md) | Orchestration external events 语义和单向异步限制。 |
| wiki | [Durable Task Entities 文档](../sources/azure-durable-functions/entities-docs.md) | Durable entities 小块状态与串行 operation 语义。 |
| wiki | [Durable Task Storage Providers 文档](../sources/azure-durable-functions/storage-providers-docs.md) | Durable Task runtime state backend 和 storage provider 边界。 |
| wiki | [Durable Task Hosting Model 文档](../sources/azure-durable-functions/hosting-model-docs.md) | Durable Functions 与 standalone Durable Task SDKs 的 hosting model 差异。 |
| wiki | [Azure Functions Scale and Hosting 文档](../sources/azure-functions/scale-hosting-docs.md) | Azure Functions hosting plans、scale、资源、网络/容器支持和成本边界。 |
| wiki | [Microsoft Agent Framework Durable Extension 文档](../sources/microsoft-agent-framework/durable-extension-docs.md) | Durable Task-backed execution、checkpoint/recover、HITL、Azure Functions 与 self-hosted hosting 边界。 |
| wiki | [Microsoft Agent Framework Durable Workflow Registration 源码](../sources/microsoft-agent-framework/durable-workflow-registration-source.md)、[Microsoft Agent Framework Durable Executor Dispatcher 源码](../sources/microsoft-agent-framework/durable-executor-dispatcher-source.md) | Durable graph workflows 到 orchestrations/activities/entities/sub-orchestrations/external events 的注册与 dispatch 映射。 |
| wiki | [Microsoft Agent Framework Workflows 概览](../sources/microsoft-agent-framework/workflows-overview-docs.md)、[Microsoft Agent Framework WorkflowBuilder 文档](../sources/microsoft-agent-framework/workflow-builder-docs.md)、[Microsoft Agent Framework Functional Workflows 文档](../sources/microsoft-agent-framework/functional-workflows-docs.md) | Agent Framework workflows、graph workflow、executors、edges、superstep execution 与 functional workflow surface。 |
| wiki | [Microsoft Agent Framework Workflow Checkpoints 文档](../sources/microsoft-agent-framework/checkpoints-docs.md)、[Microsoft Agent Framework Workflow State 文档](../sources/microsoft-agent-framework/state-docs.md) | Checkpoint 捕获范围、恢复/迁移语境、workflow state 与 built workflow immutability。 |
| wiki | [Durable Task Scheduler 文档](../sources/microsoft-durable-task/scheduler-docs.md) | Durable Task Scheduler dispatch orchestrator/activity/entity work items 并管理 durable state 的后端边界。 |
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
| 新建主 buildout process manager 时，在前述领域事实层之外，Temporal 的 durable Workflow Execution、message passing、Timer、Activity 和 Child Workflow 更贴近长期交互式资源过程管理。 | Temporal Workflows、Activities、Message Passing、Timers、Child Workflows source pages。 | Temporal 不保存全部领域事实，也不自动处理物理副作用幂等、补偿和业务 dashboard。 |
| Temporal Reset、Continue-As-New 和 Worker Versioning 不能被写成物理回滚、任意计划迁移或自动升级。 | Temporal Reset、Continue-As-New、Worker Versioning source pages。 | 这些机制仍可作为受约束的恢复、历史截断和版本路由工具。 |
| Azure Durable Functions / Durable Task 具备 durable orchestration、activity、timer、external event、entity、event sourcing、checkpoint/replay 和 instance identity 等与主 process manager 相邻的能力，因此应作为 Temporal 之外的 POC 候选，而不是按 Airflow/LangGraph 的外围角色直接排除。 | Azure Durable Functions Overview、Durable Task Orchestrations、Timers、External Events、Entities source pages。 | Durable Functions 与 Temporal 都需要外部事实层、幂等和 replay discipline；真实差异在 hosting/runtime、交互模型、观察和运维边界。 |
| Azure Durable Functions / Durable Task 的核心差异是 Azure Functions 产品面与 standalone Durable Task runtime 面必须先分清；在 AKS、VM 或 on-premises 等目标平台上，standalone Durable Task SDKs 可能才是对应 hosting model。 | Durable Task Hosting Model、Azure Functions Scale and Hosting、Durable Task Storage Providers source pages。 | 本页没有实测不同 hosting plan、storage provider 或网络环境下的性能和运维成本。 |
| Durable orchestrator replay、storage provider、entities 和 external events 是 durable runtime 语义与边界；在裸金属 buildout 中，它们必须与 external inventory/resource graph、业务事件契约和副作用纪律组合使用，不能单独证明或否定候选资格。 | Durable Task Orchestrations、Code Constraints、Storage Providers、External Events、Entities source pages；裸金属工具链 source pages。 | 这些不是 Azure 独有缺陷；它们只是 Azure/Durable Task 进入 POC 时必须明确的运行时边界。 |
| Microsoft Agent Framework Durable Workflow Extension 具备 Durable Task-backed graph workflow、checkpoint/recover、activity/entity/sub-orchestration/external event dispatch 和多 host/stateless worker 恢复证据，因此应作为 Durable Task 相邻的 POC 候选，而不是按普通 agent graph 或 Airflow/LangGraph 外围角色直接排除。 | Microsoft Agent Framework Durable Extension、Durable Workflow Registration、Durable Executor Dispatcher、Workflows Overview、WorkflowBuilder、Functional Workflows、Durable Task Scheduler source pages。 | 这些证据支撑的是 Durable Extension-backed graph workflow；不能自动外推到 standard checkpoints、functional workflow surface 或未启用 Durable Extension 的 core workflow。 |
| Microsoft Agent Framework Durable Workflow Extension 的真实差异在于 Durable Task 之上的 Agent Framework graph/executor/superstep/agent entity 抽象层：它可能降低 agent/HITL 集成成本，也可能增加资源身份映射、checkpoint 兼容性、观测和诊断成本。 | Microsoft Agent Framework Workflows Overview、WorkflowBuilder、Functional Workflows、Workflow Checkpoints、Workflow State、Durable Executor Dispatcher source pages；Temporal Child Workflows、Message Passing、Continue-As-New、Worker Versioning source pages。 | 资源分区是本文裸金属 buildout 架构映射，不是 Microsoft 或 Temporal 针对该场景的官方推荐架构。 |
| Airflow 的 Dynamic Task Mapping、Deferrable Operators、Event-Driven Scheduling、HITL、TaskInstance 状态、DagRun/catchup/backfill、DAG processing/serialization、bundle versioning 和 `DagRun.verify_integrity` 能证明它有等待、触发、人工输入、fan-out、历史区间重处理、部署版本和受控 DagRun reconciliation 能力；但这些机制围绕 DAG/DagRun/TaskInstance/schedule/data interval，作为裸金属主 process manager 时比 Temporal Workflow/Child Workflow/Signals/Updates/Run 边界更容易把长期资源过程压扁成调度图重处理问题。 | Airflow DAG、Dag Run、Backfill、Scheduler、Dynamic Task Mapping、Deferrable Operators、Event-Driven Scheduling、HITL、Task States、DAG File Processing、DAG Serialization、DAG Bundles、DagRun verify_integrity source pages；Temporal Child Workflows、Message Passing、Reset、Continue-As-New、Worker Versioning source pages。 | Temporal 也需要迁移、副作用和外部事实层纪律；本页判断的是在现有限制下哪个 runtime 的过程建模面更自然。 |
| Airflow 的核心状态对象是 DagRun/TaskInstance/mapped task/deferred task 等 scheduler/task execution 状态，不应直接替代裸金属资源事实。 | Airflow DAG、Scheduler、Task States、Deferrable Operators source pages。 | Airflow 可以通过 task 读写外部领域状态；本页反对的是把 Airflow metadata DB 当领域真源。 |
| LangGraph 的 persistence、interrupt/resume、fault tolerance、Agent Server、graph migrations 和 time travel 证明它能运行长期 stateful agent graph/thread；但现有证据的建模重心是 graph/thread/run/checkpoint/store，而不是一手 durable resource process identity、child execution 和 workflow message entry。 | LangGraph Overview、Persistence、Interrupts、Fault Tolerance、Agent Server、Graph Migrations、Time Travel source pages；Temporal Workflows、Message Passing、Child Workflows source pages。 | Temporal 也需要业务层定义资源含义；差异不是“谁自动理解资源”，而是现有一手证据分别提供了哪些过程建模锚点。 |
| LangGraph 作为主 process manager 的 POC 必须证明 graph/thread 明确持有长期控制路径、事件解释、局部追平、审计、迁移策略和副作用边界；否则更稳妥的定位是 AI diagnosis、operator copilot、HITL decision support 或 agent automation adapter。 | LangGraph Persistence、Interrupts、Fault Tolerance、Time Travel、Agent Server source pages；Temporal Reset、Activities、Message Passing、Child Workflows source pages。 | checkpoint/store 不是资源事实库、time travel 不是物理回滚等是共性纪律；本页不把它们写成 LangGraph 独有缺陷。 |
| external inventory/resource graph/audit store、业务事件模型、副作用纪律、dashboard projection 和迁移/版本纪律是裸金属 buildout 的共性工程前提，不是任何单个候选的专属缺陷；各 runtime 更适合保存过程执行、runtime 或 agent/workflow graph 语义。 | Temporal、Azure Durable Functions、Microsoft Agent Framework、Airflow、LangGraph source pages；裸金属工具链 source pages。 | 具体数据模型、锁协议和审计 schema 需另行设计；使用这些共性前提本身不能证明某个候选不适合作为主 process manager。 |
| Redfish、MAAS、Ironic、Tinkerbell、Foreman、Cobbler、xCAT、Metal3 和 Slurm 不是无状态命令集合，而是协议、控制面、资源模型或调度系统，应被上层 process manager 协调和观察。 | DMTF Redfish、MAAS、Ironic、Tinkerbell、Foreman、Cobbler、xCAT、Metal3、Slurm source pages。 | 这些工具覆盖面、成熟度、项目状态和适用性不同；本页只用它们支撑“下层领域控制面”边界。 |
| 本页判断仍需要 POC、运维和组织约束验证后才能变成采购或工程基线。 | 用户输入；raw 草稿边界；各 source pages 的限制。 | 当前没有实测数据、规模参数、团队经验、成本模型或 UI/运维成熟度评估。 |
