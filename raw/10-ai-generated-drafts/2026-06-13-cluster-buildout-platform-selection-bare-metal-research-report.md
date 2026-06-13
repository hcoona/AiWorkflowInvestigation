---
source_type: ai-generated-draft
title: "Copilot research report: physical/bare-metal Cluster Buildout platform selection"
origin: "GitHub Copilot CLI research output revised after first-principles analysis and adversarial review"
generator: "GitHub Copilot CLI"
recorded: 2026-06-13
language: zh-Hans
topic: "AI workflow platform selection"
authority: "non-authoritative"
raw_admission_reason: "User requested renewed research after a prior AI report incorrectly scoped Cluster Buildout as Kubernetes/GitOps buildout."
preservation_mode: ai-research-report
full_text_preserved: true
cleanup_note: "Generated from the corrected human request; scoped to physical/bare-metal machine cluster buildout."
---

> [!WARNING] 非权威 AI 调研报告
> 本文件是 GitHub Copilot CLI 生成的调研草稿。虽然本轮调研优先核验了官方文档和开源仓库，并经过独立对抗审查，但它仍不是 wiki 结论证据，也不是基于 POC、压测、运维成本、团队熟练度或 UI 成熟度的最终采购结论。不要直接把其中的产品能力、平台比较、选型结论或外部链接作为决策依据；如需复用，必须重新核验一手来源，并在 `wiki/` 中建立明确的 claim-to-evidence 映射。

# 物理机/裸金属 Cluster Buildout 场景下 Temporal 与 Apache Airflow 选型调研

## 调研边界与方法

本报告讨论的是 **物理机/裸金属机器集群的 Cluster Buildout**：从物理节点、机架/网络、BMC、固件/BIOS/RAID/NIC、PXE/iPXE、OS provisioning、驱动/内核、物理集群资源管理/作业调度器、基础服务，到烧机、验收和集成验证的建设流程。

本报告明确不把问题转写为 Kubernetes cluster provisioning、Crossplane/GitOps/Helm/Kustomize 工作流，也不把应用部署流水线当作 buildout 主体。Metal3/Ironic/Kubernetes CRD 或 GitOps 可以在已有管理平面中作为子系统出现，但不是本文默认主推荐路径。

调研方法：

1. 以用户原始请求为场景边界。
2. 优先使用 Temporal、Apache Airflow、Ironic、Tinkerbell、Cobbler、xCAT、MAAS、Foreman、Slurm、DMTF Redfish 等官方文档或官方开源仓库。
3. 按第一性原则比较能力：不是比较术语是否相同，而是比较运行时持久化什么状态、外部事件进入哪个对象、故障后恢复什么、真实世界副作用如何隔离、计划如何演进。
4. 使用独立 GPT-5.5 对抗审查代理挑战结论，特别修正 Temporal Reset / Continue-As-New / Worker Versioning 的过强表述，以及 Airflow 3.x event-driven scheduling / HITL 的低估风险。

## 执行摘要

如果把裸金属 Cluster Buildout 的核心抽象为“长期、交互式、事件驱动、资源实体导向、可局部失效恢复的 buildout process manager”，**Temporal 是更强的默认主编排候选**。原因不是 Temporal 有 “Workflow” 这个术语，而是 Temporal Workflow Execution 本身就是 durable/reliable/scalable function execution；Event History 是 Workflow Execution 控制状态恢复与 replay 的 source of truth；运行中的 Workflow 可以接收 Signal/Update；Workflow 可以长期等待 Timer/Signal；Activity 明确承载外部副作用；Child Workflow 可按 node、rack、fabric、scheduler partition 等资源实体隔离状态。物理设备状态、人工操作、供应商事件和验收事实仍必须由外部 inventory/resource graph/audit store 作为领域真源，并通过 reconcile 与 workflow 状态对齐。[^temporal-workflow][^temporal-execution][^temporal-message][^temporal-child]

但 Temporal 不是“自动回滚物理世界”的魔法层。Reset 只是终止一个 Workflow Execution 并从 reset point 创建新的 execution，不会撤销已刷写的固件、已改过的 RAID、已执行的 PXE 安装或已发生的现场操作；Continue-As-New 主要是 checkpoint 状态、开启 fresh Event History，不等于任意运行中改计划；Worker Versioning 管理 worker 版本路由，不等于自动迁移在途流程；Activity retry 也不是 exactly-once。真实裸金属操作必须设计幂等键、读后校验、外部 inventory/resource graph、resource lock、reconcile 和补偿流程。[^temporal-reset][^temporal-continue][^temporal-worker-versioning]

Apache Airflow 不应被简单写成“不能等人/不能等事件”。Airflow 是 batch-oriented workflow 平台，但 Airflow 3.0 引入基于 AssetWatcher/BaseEventTrigger 的 event-driven scheduling，3.1 引入 HITL operators，3.3 起 HITL 等待可进入 scheduler-managed `awaiting_input` 状态而不占 worker/triggerer；它还具备 Dynamic Task Mapping、Trigger Rules、Deferrable Operators、UI 和 REST/API 能力。它可以很好承载有限批处理、节点 fan-out 验证、烧机批次、周期健康检查、报表、审批子流程，甚至在组织已有 Airflow 基础时作为务实调度层。真正的限制是：Airflow 更自然地持久化和恢复 DagRun/TaskInstance 调度状态，而不是一次 buildout 的长期领域资源状态机；若拿它做主控，资源图、局部失效传播、追平、计划演进和领域事件源通常需要在 Airflow 外自建。[^airflow-index][^airflow-dags][^airflow-dtm][^airflow-deferrable][^airflow-event][^airflow-hitl][^airflow-tasks]

裸金属工具链不应被当作被动 shell 命令。MAAS、Ironic、Tinkerbell、Foreman、Cobbler、xCAT、Metal3、Slurm 等本身就是领域控制面或邻接状态机：它们拥有 machine / host / node / job / provisioning lifecycle 等自己的状态和约束。主 process manager 应协调、观察、补偿它们，而不是替代它们的底层生命周期语义。[^maas][^ironic][^tinkerbell][^foreman][^cobbler][^xcat][^metal3][^slurm]

## 第一性能力模型

平台选型的核心问题不是“谁有 DAG / workflow / task / retry / sensor / signal”，而是这些概念在系统中的 **执行语义** 是否等价。

| 维度 | 裸金属 buildout 的第一性问题 | Temporal | Apache Airflow |
| --- | --- | --- | --- |
| 主状态对象 | 一次 buildout 是否能成为长期可寻址对象？ | Workflow Execution 是运行中对象，有 Workflow ID、Event History、Signals/Updates。 | DagRun/TaskInstance 是运行对象；长期 buildout 领域状态通常需要外置。 |
| 状态真源 | 崩溃后恢复的是什么？ | Event History replay 重建 Workflow 控制状态与控制点；领域事实仍在外部 inventory/resource graph。 | metadata DB 中的 DagRun/TaskInstance 状态驱动 scheduler 再调度；领域事实通常也需外部存储。 |
| 外部事件入口 | 人工、AI、BMC、供应商事件进入哪里？ | Signal/Update 进入特定 Workflow Execution。 | 事件可触发 Dag、恢复 deferred/HITL task，或通过外部状态再被 task 读取。 |
| 等待模型 | 数天/数周等待是否是核心语义？ | Workflow 可等待 Timer/Signal/condition，不占 Activity worker；Timer 写入历史。 | Deferrable 可不占 worker；HITL 在 3.3+ 可不占 worker/triggerer；语义仍落在 task/DagRun 上。 |
| 副作用边界 | BMC/PXE/固件/RAID/OS/Slurm 调用如何重试？ | Activity 是副作用边界，需幂等；结果写入 Event History。 | Task/operator 是副作用边界，需幂等；状态写入 metadata DB/XCom/外部系统。 |
| 动态工作 | 蓝图运行中发现新检查项怎么办？ | Workflow code 可按状态启动 Activity/Child Workflow；计划变更需显式版本和迁移。 | Dynamic Task Mapping 可按上游输出展开有限任务；运行中任意拓扑演进通常外置。 |
| 局部失败 | 已通过组件后续集成失败，如何分裂/追平？ | 可按资源实体拆 Child Workflow，但失效传播和追平仍是领域逻辑。 | Trigger rules/branching 支持固定图内路由；长期局部追平通常依赖外部状态机。 |
| 流程演进 | 在途 run 如何安全承受代码/蓝图变化？ | Worker Versioning、patching、Continue-As-New、Reset 是工具；不自动迁移物理副作用。 | DAG 代码版本、DagRun、clear/rerun、backfill、外部状态共同承担；需自定迁移纪律。 |
| UI | 操作员看什么？ | Temporal UI 偏 execution/history/debug；业务看板多半需 projection。 | Airflow Grid/Graph/HITL UI 开箱更友好；业务资源图仍需外部建模。 |

## 场景抽象：裸金属 buildout 不是普通任务流

一次真实的物理机集群 buildout 至少有四层状态：

1. **资源事实层**：节点、机架、交换机端口、BMC 地址、PXE 网络、固件版本、RAID 卷、NIC 配置、OS 镜像、驱动、内核参数、Slurm/PBS partition、GPU/IB/RoCE 拓扑。
2. **物理副作用层**：刷固件、改 BIOS、创建 RAID、安装 OS、重启、上架、换线、供应商现场操作。这些动作不可假设 exactly-once，也不可假设可自动撤销。
3. **流程状态层**：Blueprint、阶段、门禁、并行分支、失败节点、修复分支、追平条件、验收级别、人工审批、AI 诊断结果。
4. **审计与协作层**：谁在什么时候批准、哪个 Agent 提出什么判断、供应商回复什么、现场人员确认什么、哪些测试支撑验收。

所以平台选型的本质不是“谁能跑 N 个 task”，而是谁更少扭曲地承载 **长期资源状态机 + 外部事件 + 真实世界副作用**。在这个抽象下，Temporal 更像主 process manager，Airflow 更像批处理/调度/可视化执行层；两者都需要一个外部 inventory/resource graph 承担领域事实。

## Temporal 适配分析

### 能力契合点

**长期 durable execution。** Temporal 文档将 Workflow Execution 定义为 durable、reliable、scalable function execution；Workflow 可以运行数年，失败后由 Event History replay 恢复。对 buildout 来说，这匹配数天到数周的等待、验证和修复循环。[^temporal-workflow][^temporal-execution]

**Event History 是 Workflow 控制状态恢复语义的一部分。** Temporal 不通过内存快照恢复，而是重新执行 Workflow code，并用 Event History 指导代码回到同一控制状态；Activity 结果会被记录，replay 时复用而非重新执行。这个差异使它更适合作为长期过程状态机，而不只是任务调度器。但 Event History 不应成为 node、BMC、firmware、OS、现场操作或验收事实的唯一账本；这些领域事实仍需要外部 inventory/resource graph/audit store。[^temporal-workflow]

**消息进入运行中对象。** Temporal 把 Workflow 描述为可接收消息的 stateful web service。Queries 读状态，Signals 是异步写请求，Updates 是同步、可追踪写请求。人工确认、AI 诊断结果、BMC/MAAS/Ironic/Slurm 状态回调，都可以进入具体 Workflow Execution，而不是只触发一个新批处理 run。[^temporal-message]

**资源实体分区。** Child Workflow 可用于把问题分成更小块，也可一对一表示单个资源；官方例子提到 host upgrade per host。裸金属 buildout 可按 node、rack、fabric、storage domain、scheduler partition 建模 Child Workflow，从而隔离 Event History、重试、等待和人工事件。[^temporal-child]

**副作用边界清晰。** Workflow code 必须确定性；API、DB、LLM、文件 I/O 等外部交互应放入 Activity。裸金属场景下，Redfish/IPMI、PXE/iPXE、Ironic/MAAS/Tinkerbell、Slurm 命令/API、LLM/AI Agent 调用、人类通知都应是 Activity 或消息事件，而不是 Workflow replay 路径内的非确定行为。[^temporal-workflow]

### 必须降调的点

Temporal 的优势不是“自动完成局部回滚/运行中改图”，而是提供更合适的状态机地基：

- **Reset 不是物理回滚。** Temporal Reset 会终止一个 Workflow Execution，并复制原 execution 到 reset point 的历史前缀，创建新的 execution 继续；它不会撤销真实设备状态。对固件、RAID、OS、网络端口这类副作用，Reset 前后必须先 reconcile 外部事实。[^temporal-reset]
- **Continue-As-New 不是任意计划迁移。** Continue-As-New checkpoint 最新相关状态并开启 fresh Event History，适合作为阶段边界、历史截断、版本切换点；但蓝图 schema、迁移、审批、兼容性仍要自己设计。[^temporal-continue]
- **Worker Versioning 不是在途流程自动升级。** Pinned Workflow 保证 execution 在启动时的 Worker Deployment Version 上完成；Auto-Upgrade 仍需 replay-safe。是否把在途 buildout 切到新逻辑，是业务迁移问题。[^temporal-worker-versioning]
- **Activity retry 不是 exactly-once。** BMC/Redfish、固件刷写、PXE reinstall、Slurm job submission 等都需要幂等键、状态读回、操作锁、补偿或人工确认。

## Apache Airflow 适配分析

### 必须公平承认的能力

Airflow 官方文档称其为 developing、scheduling、monitoring batch-oriented workflows 的开源平台，并强调对 clear start/end、schedule-driven workflows 很适合。它的强项是 Python workflows-as-code、成熟 UI、scheduler、DagRun/TaskInstance、operator/provider 生态和可运维性。[^airflow-index][^airflow-dags]

但 Airflow 不是“只能静态定时任务”：

- **Dynamic Task Mapping** 允许基于上游 task 输出在 runtime 创建 mapped task copies，适合按节点列表、机架列表或测试矩阵做有限 fan-out。[^airflow-dtm]
- **Trigger Rules / Branching** 支持固定 DAG 拓扑内的条件分支和不同上游状态门禁。[^airflow-dags]
- **Deferrable Operators** 可在等待时释放 worker slot，由 triggerer 运行等待逻辑；文档也强调 deferral 过程中 operator 会停止并移出 worker，状态需通过 resume method/kwargs 传递。[^airflow-deferrable]
- **Event-driven scheduling** 在 3.0 引入，允许 DAG 基于外部事件触发，并通过 AssetWatcher/BaseEventTrigger 关联消息队列等外部事件源。[^airflow-event]
- **HITL** 在 3.1 引入人工输入；3.3 文档称等待输入改为 scheduler-managed `awaiting_input` 状态，不占 worker slot 或 triggerer；3.1/3.2 的 HITL 等待仍走较早的 deferral/triggerer 路径。[^airflow-hitl][^airflow-tasks]

因此，不能把 Airflow 简单排除为“不能等人、不能等事件、不能动态展开”。它在很多 buildout 子问题上是有效工具。但 Airflow event-driven scheduling 主要围绕 Asset/AssetEvent/DagRun 调度，HITL 输入作用于等待中的 TaskInstance；它不是任意外部事件注入任意在途 buildout 资源状态机的通用事件总线。

### 真正的能力缺口

Airflow 的关键差异是 **主状态对象和恢复语义**。Airflow 运行的是 DagRun 和 TaskInstance；TaskInstance 有 `scheduled`、`queued`、`running`、`deferred`、`awaiting_input`、`success`、`failed`、`removed` 等状态，其中 `awaiting_input` 的不占 worker/triggerer 行为需要按 Airflow 3.3+ 版本判断。这个模型适合表达“这个有限任务图现在执行到哪”，但不天然表达“这个物理集群 buildout 资源图在多周内经过哪些局部失效、修复、追平和验收状态”。[^airflow-tasks]

如果把 Airflow 当主控，通常会产生以下工程形态：

1. 外部 inventory/resource graph 保存 node/rack/network/firmware/OS/scheduler/validation 的事实状态。
2. Airflow DAG 读取外部状态，展开一批有限任务。
3. 人工或外部事件通过 HITL、event-driven scheduling、deferrable trigger 或外部 API 恢复某个 task 或触发新 DagRun。
4. 局部失败后的“哪些继续、哪些等待、哪些重跑、哪些追平”由外部状态机决定。
5. DAG 代码变更、在途 DagRun、清理/重跑/removed task 等需要严格版本和迁移纪律。

这不是不可行，而是意味着 Airflow 承担的是调度/执行/UI 层，核心长期领域状态机在 Airflow 外部。若组织已有 Airflow，且 buildout 可被切分为事件触发的有限 DagRun、批量 fan-out、验证、审批、报表和周期性 reconcile，Airflow 可以成为务实的调度层/操作界面；若目标是新建主 process manager，Temporal 的语义摩擦更小。

## 裸金属工具链的边界

裸金属工具链本身已经包含大量领域状态和生命周期，不应被 workflow 平台重写：

| 工具/协议 | 官方证据支持的定位 | 在本文架构中的角色 |
| --- | --- | --- |
| Redfish | DMTF Redfish 是面向现代工具链的简单、安全管理标准。 | BMC/固件/硬件管理协议层。[^redfish] |
| MAAS | MAAS 把 physical servers 变成 elastic cloud-like resource，可 boot、check、deploy、tear down、redeploy。 | 机器生命周期和裸金属资源池控制面。[^maas] |
| OpenStack Ironic | Ironic 通过 API 和插件以安全、容错方式管理和 provisioning physical machines，默认用 PXE 与 IPMI/Redfish。 | 裸金属 provisioning 控制面。[^ironic] |
| Tinkerbell | Tinkerbell 是 bare metal provisioning engine，支持 network/ISO boot、BMC interactions、metadata service、workflow engine。 | OS provisioning/硬件发现/metadata 子系统。[^tinkerbell] |
| Foreman | Foreman 自动化 repetitive tasks，管理 server lifecycle，覆盖 provisioning/configuration/orchestration/monitoring，支持 bare-metal。 | 生命周期管理、配置、审计和 API 控制面。[^foreman] |
| Cobbler | Cobbler 是 Linux installation server，可自动化 network installation、DNS/DHCP、package updates、power management 等。 | PXE/安装/电源管理子系统。[^cobbler] |
| xCAT | xCAT 是集群部署与管理工具，可发现硬件、远程系统管理、provision OS、并行系统管理。 | HPC/大规模集群部署与管理控制面。[^xcat] |
| Metal3 BareMetalHost | BareMetalHost 定义 physical host；provisioning 需要 BMC details 等条件。 | K8s/CRD/Ironic 生态中的裸金属子控制面；不是本文默认主路径。[^metal3] |
| Slurm | Slurm 是 fault-tolerant、scalable cluster management and job scheduling system，管理 compute node 资源、job 启动/监控与队列。 | buildout 后段的集群资源管理/验证作业执行面。[^slurm] |

更准确的架构说法是：Temporal 或 Airflow 不应替代这些系统的底层生命周期。主 process manager 应在上层协调它们、监听它们、在不一致时触发 reconcile/补偿/人工决策。

## 推荐架构

### 默认推荐：Temporal 作为 buildout process manager

适用前提：

- buildout 是长期、交互式、事件驱动过程；
- 资源实体之间存在拓扑依赖和局部失效传播；
- 人工、AI Agent、确定性自动化混合；
- 在途流程需要版本化、审计和可解释的状态迁移；
- 团队愿意建设 domain inventory/resource graph 和业务 dashboard。

该推荐是基于能力匹配的技术判断，不是基于 POC、压测、运维成本、团队熟练度或 UI 成熟度的最终采购结论。

建议分层：

1. **External inventory/resource graph**：保存 node/rack/network/BMC/PXE/firmware/OS/scheduler/validation 的领域事实、锁、依赖、审计字段。
2. **Temporal Blueprint Workflow**：代表一次 cluster buildout 的长期过程；保存流程级状态、阶段门禁和资源实体引用，而不是复制所有领域事实。
3. **Temporal Child Workflows**：按 node、rack、fabric、storage、scheduler partition 或 validation domain 分区；每个实体独立接收事件、等待人工、执行修复和追平。这个边界是架构设计选择，不是自动收益；必须先设计资源图、依赖传播和补偿边界。
4. **Activities**：封装 Redfish/IPMI、MAAS/Ironic/Tinkerbell/Foreman/Cobbler/xCAT/Slurm、通知、AI Agent、报告生成等外部副作用；所有 Activity 设计幂等与读后校验。
5. **Signals/Updates**：用于人工确认、供应商回复、AI 决策、外部系统回调、计划变更请求。
6. **Dashboard projection**：从 Temporal Search Attributes、Queries、inventory/resource graph、工具链状态中投影业务 UI；不要只依赖 Temporal UI 当操作员产品界面。

### Airflow 的合理定位

Airflow 可作为：

- 固件版本批量采集；
- 批量 OS 安装后验证；
- 烧机测试 fan-out/fan-in；
- Slurm job 验证批次；
- 周期健康检查；
- 报表和审计数据加工；
- 已有 Airflow 组织中的审批/调度界面。

如果 Airflow 被要求承担主控，应明确架构代价：

- 外部 domain state service 是必需品，不是可选优化；
- Airflow metadata DB 不应成为裸金属领域事件源；
- Dynamic Task Mapping 只负责有限集合展开，不负责长期拓扑演进；
- HITL/deferrable/event-driven scheduling 解决等待和触发，不解决资源图、局部失效传播和追平语义；
- DAG 代码版本与在途 DagRun 迁移必须有工程纪律。

## POC 验证项

### Temporal POC

1. **单节点 workflow**：BMC read -> 固件/BIOS 检查 -> OS provisioning -> 驱动安装 -> Slurm 验证 job，全部通过 Activity 封装。
2. **长等待与人工事件**：Workflow 等待现场上架/换线确认 24 小时以上，Signal/Update 恢复后状态一致。
3. **局部失败隔离**：10 个节点 Child Workflow 中 2 个失败，未受影响节点继续；失败节点修复后追平并重新进入集成门禁。
4. **Reset 安全性**：对一个节点 workflow 做 reset，验证外部 inventory 与真实设备状态 reconcile 后才允许重放危险 Activity。
5. **Continue-As-New**：在阶段边界 checkpoint 资源状态引用，切换 Run 后外部消息和 dashboard 仍可定位到同一 buildout。
6. **Worker Versioning**：在途 buildout 与新 buildout 使用不同 worker 版本，验证 pinned/auto-upgrade 策略和 replay-safe 约束。
7. **AI Agent 审计**：LLM 输入、模型、输出、人工批准、时间戳不进入 Workflow 非确定路径，而是作为 Activity 结果或外部审计记录。

### Airflow POC

1. **有限 fan-out DAG**：从外部 inventory 读取节点列表，用 Dynamic Task Mapping 展开固件检查/烧机验证。
2. **HITL 与 deferrable 等待**：比较 Airflow 3.3+ HITL `awaiting_input`、Airflow 3.1/3.2 HITL deferral 路径、deferrable trigger、外部 ticket system 对人工/供应商窗口的适配。
3. **event-driven scheduling**：用 AssetWatcher/BaseEventTrigger 接入外部事件源，触发 DAG 或任务恢复。
4. **外部状态机压力测试**：模拟局部失败、修复、追平、重新验收，确认 Airflow 只作为执行层时外部 domain state 是否可维护。
5. **DAG 版本迁移**：在 DagRun 运行中变更 DAG 文件，验证 removed task、trigger rules、clear/rerun 对业务审计的影响。

## 修正后的结论

| 问题 | 结论 |
| --- | --- |
| 是否推荐 Temporal？ | 是，作为新建主 buildout process manager 的更强候选；但这是能力模型推断，必须配套 POC、inventory/resource graph、幂等 Activity、补偿、版本策略和业务 dashboard。 |
| 是否否定 Airflow？ | 否。Airflow 能承载大量事件触发的有限 DagRun、批量 fan-out、验证、审批、报表、周期性 reconcile 和已有平台子流程；只是默认不应把它当长期裸金属资源状态机。 |
| Temporal 的关键风险 | 把 Reset/Continue-As-New/Worker Versioning 误用成物理回滚、任意流程迁移或自动升级；把 Activity retry 误认为 exactly-once。 |
| Airflow 的关键风险 | 把 metadata DB/TaskInstance 状态偷换成领域事件源；把 deferrable/HITL/event trigger 误认为长期资源状态机。 |
| 裸金属工具链定位 | MAAS/Ironic/Tinkerbell/Foreman/Cobbler/xCAT/Metal3/Slurm 是领域控制面或邻接状态机，应被协调和观察，不应被 workflow 平台替代。 |

最终一句话：

> 如果裸金属 buildout 的核心是长期、交互式、事件驱动、可局部失效恢复的资源状态机，优先评估 Temporal；如果它能被切分为事件触发的有限 DagRun、批量 fan-out、验证、审批、报表和周期性 reconcile，且长期领域状态由外部系统掌握，Airflow 可以务实承载大量子流程，甚至在组织约束下成为调度层。

## 来源

[^temporal-workflow]: Temporal documentation repository, `docs/encyclopedia/workflow/workflow-overview.mdx`, cloned 2026-06-13 from `https://github.com/temporalio/documentation`; official URL `https://docs.temporal.io/workflows`. Supports Workflow Definition/Execution distinction, years-long resilient workflows, Event History replay, Activities for external interactions.

[^temporal-execution]: Temporal documentation repository, `docs/encyclopedia/workflow/workflow-execution/workflow-execution.mdx`, cloned 2026-06-13 from `https://github.com/temporalio/documentation`; official URL `https://docs.temporal.io/workflow-execution`. Supports durable/reliable/scalable execution, local state, Signals, Activities, replay, Timer/Activity/Child Workflow awaitables.

[^temporal-message]: Temporal documentation repository, `docs/encyclopedia/workflow-message-passing/workflow-message-passing.mdx`, cloned 2026-06-13 from `https://github.com/temporalio/documentation`; official URL `https://docs.temporal.io/encyclopedia/workflow-message-passing` or current message-passing pages. Supports Queries, Signals, Updates and their read/write/synchronous/asynchronous distinctions.

[^temporal-child]: Temporal documentation repository, `docs/encyclopedia/child-workflows/child-workflows.mdx`, cloned 2026-06-13 from `https://github.com/temporalio/documentation`; official URL `https://docs.temporal.io/child-workflows`. Supports Child Workflow partitioning, per-resource modeling, Parent Close Policy caveats, Event History cost.

[^temporal-continue]: Temporal documentation repository, `docs/encyclopedia/workflow/workflow-execution/continue-as-new.mdx`, cloned 2026-06-13 from `https://github.com/temporalio/documentation`; official URL `https://docs.temporal.io/workflow-execution/continue-as-new`. Supports checkpointing state, fresh Event History, same Workflow ID/different Run ID, repeated Continue-As-New.

[^temporal-reset]: Temporal documentation repository, `docs/encyclopedia/workflow/workflow-execution/event.mdx`, cloned 2026-06-13 from `https://github.com/temporalio/documentation`; official URL `https://docs.temporal.io/workflow-execution/event#reset`. Supports Event History limits, no time constraint, Reset semantics and valid reset points.

[^temporal-worker-versioning]: Temporal documentation repository, `docs/production-deployment/worker-deployments/worker-versioning.mdx`, cloned 2026-06-13 from `https://github.com/temporalio/documentation`; official URL `https://docs.temporal.io/production-deployment/worker-deployments/worker-versioning`. Supports Worker Deployment Version, Pinned vs Auto-Upgrade, version routing and deployment strategy.

[^airflow-index]: Apache Airflow repository, `airflow-core/docs/index.rst`, cloned 2026-06-13 from `https://github.com/apache/airflow`; official URL `https://airflow.apache.org/docs/apache-airflow/stable/index.html`. Supports Airflow as platform for developing, scheduling, monitoring batch-oriented workflows, with UI and extensible Python framework.

[^airflow-dags]: Apache Airflow repository, `airflow-core/docs/core-concepts/dags.rst`, cloned 2026-06-13 from `https://github.com/apache/airflow`; official URL `https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dags.html`. Supports DAG/Task dependency model, DagRun, branching and trigger rules.

[^airflow-dtm]: Apache Airflow repository, `airflow-core/docs/authoring-and-scheduling/dynamic-task-mapping.rst`, cloned 2026-06-13 from `https://github.com/apache/airflow`; official URL `https://airflow.apache.org/docs/apache-airflow/stable/authoring-and-scheduling/dynamic-task-mapping.html`. Supports runtime mapped task creation from upstream outputs and its constraints.

[^airflow-deferrable]: Apache Airflow repository, `airflow-core/docs/authoring-and-scheduling/deferring.rst`, cloned 2026-06-13 from `https://github.com/apache/airflow`; official URL `https://airflow.apache.org/docs/apache-airflow/stable/authoring-and-scheduling/deferring.html`. Supports worker-slot release, triggerer, no automatic operator state persistence while deferred, trigger design constraints.

[^airflow-event]: Apache Airflow repository, `airflow-core/docs/authoring-and-scheduling/event-scheduling.rst`, cloned 2026-06-13 from `https://github.com/apache/airflow`; official URL `https://airflow.apache.org/docs/apache-airflow/stable/authoring-and-scheduling/event-scheduling.html`. Supports event-driven scheduling, AssetWatcher, BaseEventTrigger and external event triggering.

[^airflow-hitl]: Apache Airflow repository, `airflow-core/docs/tutorial/hitl.rst`, cloned 2026-06-13 from `https://github.com/apache/airflow`; official URL `https://airflow.apache.org/docs/apache-airflow/stable/tutorial/hitl.html`. Supports Airflow 3.1 HITL operator, human input/approval/branching, and Airflow 3.3 `awaiting_input` scheduler-managed behavior.

[^airflow-tasks]: Apache Airflow repository, `airflow-core/docs/core-concepts/tasks.rst`, cloned 2026-06-13 from `https://github.com/apache/airflow`; official URL `https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/tasks.html`. Supports Task, TaskInstance, states including `deferred`, `awaiting_input`, and timeout semantics.

[^redfish]: DMTF Redfish standards page, `https://www.dmtf.org/standards/redfish`, accessed 2026-06-13. Supports Redfish as a standard for simple and secure management, human-readable and machine-capable, exposing information to modern toolchains.

[^maas]: Canonical MAAS repository, `README.rst`, cloned 2026-06-13 from `https://github.com/canonical/maas`; official site `https://maas.io/`. Supports MAAS as Metal as a Service that treats physical servers like cloud-like resources and can boot/check/deploy/tear down/redeploy machines.

[^ironic]: OpenStack Ironic repository, `README.rst`, cloned 2026-06-13 from `https://github.com/openstack/ironic`; official docs `https://docs.openstack.org/ironic/latest/`. Supports Ironic as API/plugins for managing and provisioning physical machines, using PXE and IPMI/Redfish by default.

[^tinkerbell]: Tinkerbell repository, `README.md`, cloned 2026-06-13 from `https://github.com/tinkerbell/tinkerbell`; official docs `https://tinkerbell.org/docs/`. Supports Tinkerbell as bare metal provisioning engine with network/ISO boot, BMC interactions, metadata service and workflow engine.

[^foreman]: Foreman repository, `README.md`, cloned 2026-06-13 from `https://github.com/theforeman/foreman`; official site `https://theforeman.org/`. Supports Foreman as server lifecycle management, provisioning/configuration/orchestration/monitoring, web frontend, CLI, REST API and bare-metal support.

[^cobbler]: Cobbler repository, `README.md`, cloned 2026-06-13 from `https://github.com/cobbler/cobbler`; official docs `https://cobbler.readthedocs.io/`. Supports Cobbler as Linux installation server for network installation environments, installation, DNS/DHCP, package updates, power management and configuration management orchestration.

[^xcat]: xCAT repository, `README.md` and `docs/source/index.rst`, cloned 2026-06-13 from `https://github.com/xcat2/xcat-core`; official docs `https://xcat-docs.readthedocs.io/`. Supports xCAT as toolkit for deployment and administration of clusters, including hardware discovery, remote system management, OS provisioning and parallel system management.

[^metal3]: Metal3 baremetal-operator repository, `docs/api.md` and `docs/baremetalhost-states.md`, cloned 2026-06-13 from `https://github.com/metal3-io/baremetal-operator`; official site `https://metal3.io/`. Supports BareMetalHost as physical host resource with BMC details, provisioning, inspection and deprovisioning lifecycle.

[^slurm]: Slurm repository, `doc/html/overview.shtml`, cloned 2026-06-13 from `https://github.com/SchedMD/slurm`; official docs `https://slurm.schedmd.com/overview.html`. Supports Slurm as fault-tolerant, scalable cluster management and job scheduling system managing compute-node resources, job execution/monitoring and queues.
