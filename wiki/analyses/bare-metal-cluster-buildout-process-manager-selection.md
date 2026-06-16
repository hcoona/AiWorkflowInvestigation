---
schema_version: 2
page_type: analysis
title: "裸金属 Cluster Buildout 的 Process Manager 平台选型"
status: active
created: 2026-06-16
updated: 2026-06-16
summary: "比较 Temporal 与 Apache Airflow 承载裸金属 Cluster Buildout 主过程管理职责的边界。"
maintenance:
  edit_policy: update
validation:
  body_contract: analysis-decision-memo
tags:
  - bare-metal
  - cluster-buildout
  - platform-selection
  - temporal
  - airflow
---

## 决策

如果目标是新建裸金属 Cluster Buildout 的主 process manager，
默认优先评估 Temporal，而不是把 Apache Airflow 作为主长期资源状态机。

这里的核心抽象不是“谁能跑更多 task”，而是一次 buildout 是否需要承载：
长期运行、交互式事件、资源实体导向的局部状态、真实世界副作用、局部失败恢复、
人工/供应商/AI Agent 介入，以及跨节点、机架、网络、固件、OS、集群资源管理和验收的追平。
在这个抽象下，Temporal 更适合作为主过程管理地基；
Airflow 的有限 DAG 调度、批处理、审批入口或报表能力不能被写成同一 scope
下的等价答案。
如果长期领域状态、事件解释、局部失败追平和物理副作用补偿都由 Airflow
外部系统负责，那么真正的 process manager 是那个外部系统，
Airflow 只是它调用的执行或展示层。

这个决策是条件性技术判断，不是最终采购结论。
它不覆盖 POC、压测、运维成本、团队熟练度、目标版本许可、UI 成熟度、
组织已有平台投资或供应商支持。
但在本文 scope 内，组织已有 Airflow 或 Airflow 能运行若干 buildout 子流程，
都不能直接推出 Airflow 适合做主 process manager。

## 范围

本页讨论物理机/裸金属机器集群的 buildout：
节点、机架和网络连接、BMC、固件/BIOS/RAID/NIC、PXE/iPXE、OS provisioning、
驱动/内核、裸金属资源管理、HPC/集群调度器、基础服务、烧机、验收和集成验证。

本页不把问题改写成 Kubernetes cluster provisioning、GitOps 应用部署、
普通 ETL DAG 或单次 CI/CD pipeline。
Metal3、Ironic、MAAS、Tinkerbell、Foreman、Cobbler、xCAT、Slurm 和 Redfish
可以成为 buildout 的下层或相邻控制面，但本页只讨论 Temporal/Airflow
是否适合承载上层长期过程管理职责。

## 理由

### 裸金属 buildout 的状态分层

一次真实 buildout 至少有四层状态，不能都塞进 workflow engine 的运行状态：

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

这正好匹配裸金属 buildout 的主过程管理问题：

- 一次 cluster buildout 可以是可寻址的长期 Workflow Execution。
- 单节点、机架或 fabric 的处理可以通过 Child Workflow 隔离历史、等待、重试和局部失败。
- BMC/Redfish、MAAS/Ironic/Tinkerbell、Foreman/Cobbler/xCAT、Slurm、
  通知和 AI Agent 调用应落在 Activity 或外部事件边界。
- 人工确认、供应商回复、现场操作结果和计划变更请求可以通过 Signals/Updates
  进入运行中的过程对象。
- 外部 inventory/resource graph 保存领域事实，Temporal 保存过程级状态、
  控制路径、事件入口和可审计执行历史。

必须降调的点同样重要：
Temporal Reset 不是物理回滚；
Continue-As-New 是 Run 边界状态交接和 Event History 截断点，不是任意计划迁移魔法；
Worker Versioning 是 worker/deployment routing 与 replay-safe 升级机制，
不自动迁移已发生的物理副作用；
Activity retry 不是 exactly-once。
所有真实设备操作仍必须通过幂等键、状态读回、外部锁、补偿流程和人工确认保护。

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

因此，如果一个方案声称“用 Airflow 做 process manager”，必须先回答：
长期资源身份、领域事件解释、局部失败传播、追平条件、物理副作用补偿和审计真源
到底由谁持有。
如果答案是 external inventory/resource graph、domain state service 或另一套事件系统，
那它们才是本文 scope 下的 process manager；
Airflow 只是有限 DagRun 的 scheduler/executor。
这个区分是本文为了遵守 scope 必须保留的判断边界。

若仍坚持让 Airflow 承担主 process manager 职责，架构上必须显式接受：

1. external inventory/resource graph 是必需品，不是可选优化；
2. Airflow metadata DB 不应成为裸金属领域事件源；
3. Dynamic Task Mapping 负责有限集合展开，不负责长期拓扑演进；
4. HITL、deferrable 和 event-driven scheduling 解决等待/触发/审批入口，
   不解决资源依赖传播、局部追平和物理副作用补偿；
5. DAG 版本、在途 DagRun、clear/rerun/backfill 和 removed task 需要单独的迁移纪律。

### 裸金属控制面不是普通 shell 命令

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

这也解释了为什么 Temporal/Airflow 都不应成为领域事实唯一真源：
workflow runtime 管理的是过程和执行；
裸金属工具链管理的是硬件、安装、资源池、作业和生命周期事实。
两者之间需要 external inventory/resource graph/audit store 做归一化状态、锁和证据账本。

## 后果

采用 Temporal 作为主 process manager 时，应同时承诺建设以下配套能力：

1. **External inventory/resource graph**：
   保存 node/rack/network/BMC/PXE/firmware/OS/scheduler/validation 的领域事实、
   依赖、锁和审计字段。
2. **资源实体分区策略**：
   明确哪些对象用 Child Workflow 表示，哪些只作为 external state 引用。
3. **副作用纪律**：
   所有 Redfish/IPMI、provisioning、OS、Slurm、通知、AI Agent 调用都要有幂等键、
   读后校验、重试边界和补偿策略。
4. **运行中变更纪律**：
   Continue-As-New、Reset、Worker Versioning 和 blueprint schema 迁移必须按 Run
   边界、外部事实 reconcile 和人工审批处理。
5. **业务 dashboard projection**：
   不要把 Temporal UI 当作操作员产品界面；需要从 Temporal、inventory/resource graph
   和下层控制面投影业务状态。

如果组织仍要求在方案中使用 Airflow，应在架构文档中把它标为被主 process manager
调用的 scheduler/executor/UI adapter，而不是把这个角色写成本文选型问题的答案。
否则读者会把“Airflow 能承载若干 buildout 任务”误解成
“Airflow 适合承载 buildout 的长期过程管理职责”。

## 重新审视触发条件

以下条件出现时，应重新评估这个决策：

- 决策 scope 从“主 process manager”缩小为“有限批次调度/执行/UI adapter”。
- 组织明确接受另一个 external domain state service 才是真正 process manager，
  Airflow 只承担被调用的 scheduler/executor。
- 团队没有 Temporal 运维经验，且无法承担 workflow versioning、Activity 幂等和 dashboard
  projection 的建设成本。
- 目标 buildout 场景被重新定义为短生命周期、批量验证或报表加工，
  而不是长期交互式资源状态机。
- POC 显示 Temporal 的建模、可观测性或运维成本高于 Airflow + 外部状态机组合。

## POC 验证边界

在把本页判断转成采购或工程基线前，至少验证：

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
- Airflow 方案必须证明 DAG 代码变更、既有 DagRun、removed task、clear/rerun/backfill
  不会破坏 buildout 过程审计；否则该方案仍不是合格的主 process manager。

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
| wiki | [Airflow DAG 文档](../sources/apache-airflow/dags-docs.md) | DAG、task dependencies、DagRun 和控制流基础语义。 |
| wiki | [Airflow Scheduler 文档](../sources/apache-airflow/scheduler-docs.md) | scheduler、metadata DB、DagRun 和 TaskInstance 推进语义。 |
| wiki | [Airflow Dynamic Task Mapping 文档](../sources/apache-airflow/dynamic-task-mapping-docs.md) | runtime task fan-out 和 mapped task instances。 |
| wiki | [Airflow Deferrable Operators 文档](../sources/apache-airflow/deferrable-operators-docs.md) | task/operator deferral、triggerer 等待和状态传递限制。 |
| wiki | [Airflow Event-Driven Scheduling 文档](../sources/apache-airflow/event-scheduling-docs.md) | `BaseEventTrigger` 和 event-driven Dag scheduling 约束。 |
| wiki | [Airflow HITL 文档](../sources/apache-airflow/hitl-docs.md) | 人工输入、审批、分支选择和通知能力。 |
| wiki | [Airflow Task States 文档](../sources/apache-airflow/task-states-docs.md) | TaskInstance 状态、deferred、removed 和 heartbeat timeout 语义。 |
| wiki | [DMTF Redfish Standards 页面](../sources/dmtf/redfish-standards-page.md)、[Canonical MAAS README](../sources/canonical/maas-readme.md)、[OpenStack Ironic README](../sources/openstack/ironic-readme.md)、[Tinkerbell README](../sources/tinkerbell/readme.md) | 裸金属硬件管理、机器生命周期和 provisioning 控制面证据。 |
| wiki | [Foreman README](../sources/the-foreman/readme.md)、[Cobbler README](../sources/cobbler/readme.md)、[xCAT Documentation Index](../sources/xcat/docs-index.md)、[Metal3 Baremetal Operator API 文档](../sources/metal3/baremetal-operator-api.md)、[Slurm Overview 文档](../sources/slurm/overview-docs.md) | 生命周期管理、安装、集群管理、CRD 裸金属资源和作业调度控制面证据。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| 裸金属 Cluster Buildout 是现有 workflow 通用比较页之外的独立决策边界。 | 用户输入；raw 草稿；工作流概念比较。 | raw 草稿不是技术事实证据；本页仍需由一手 source projections 支撑。 |
| 平台选型应比较长期过程对象、状态真源、外部事件入口、等待模型、副作用边界、局部失败和流程演进，而不是只比较 task 执行能力。 | 工作流概念比较；Temporal 和 Airflow source pages。 | 这是本 wiki 的综合分析框架，不是厂商官方分类。 |
| 新建主 buildout process manager 时，Temporal 的 durable Workflow Execution、message passing、Timer、Activity 和 Child Workflow 更贴近长期交互式资源过程管理。 | Temporal Workflows、Activities、Message Passing、Timers、Child Workflows source pages。 | Temporal 不保存全部领域事实，也不自动处理物理副作用幂等、补偿和业务 dashboard。 |
| Temporal Reset、Continue-As-New 和 Worker Versioning 不能被写成物理回滚、任意计划迁移或自动升级。 | Temporal Reset、Continue-As-New、Worker Versioning source pages。 | 这些机制仍可作为受约束的恢复、历史截断和版本路由工具。 |
| Airflow 的 Dynamic Task Mapping、Deferrable Operators、Event-Driven Scheduling、HITL 和 TaskInstance 状态只能证明它能承载有限 DAG 内的等待、触发、人工输入和 fan-out；这些能力不足以证明 Airflow 适合作为裸金属 buildout 的主 process manager。 | Airflow DAG、Scheduler、Dynamic Task Mapping、Deferrable Operators、Event-Driven Scheduling、HITL、Task States source pages。 | 如果另一个外部系统持有长期领域状态和追平逻辑，那么那个外部系统才是本文 scope 下的 process manager，Airflow 只是 scheduler/executor/UI adapter。 |
| Airflow 的核心状态对象是 DagRun/TaskInstance/mapped task/deferred task 等 scheduler/task execution 状态，不应直接替代裸金属资源事实。 | Airflow DAG、Scheduler、Task States、Deferrable Operators source pages。 | Airflow 可以通过 task 读写外部领域状态；本页反对的是把 Airflow metadata DB 当领域真源。 |
| external inventory/resource graph/audit store 应保存裸金属领域事实、依赖、锁和审计，而 Temporal/Airflow 保存过程执行语义。 | Temporal/Airflow source pages；裸金属工具链 source pages。 | 这是架构判断；具体数据模型、锁协议和审计 schema 需另行设计。 |
| Redfish、MAAS、Ironic、Tinkerbell、Foreman、Cobbler、xCAT、Metal3 和 Slurm 不是无状态命令集合，而是协议、控制面、资源模型或调度系统，应被上层 process manager 协调和观察。 | DMTF Redfish、MAAS、Ironic、Tinkerbell、Foreman、Cobbler、xCAT、Metal3、Slurm source pages。 | 这些工具覆盖面、成熟度、项目状态和适用性不同；本页只用它们支撑“下层领域控制面”边界。 |
| 本页判断仍需要 POC、运维和组织约束验证后才能变成采购或工程基线。 | 用户输入；raw 草稿边界；各 source pages 的限制。 | 当前没有实测数据、规模参数、团队经验、成本模型或 UI/运维成熟度评估。 |
