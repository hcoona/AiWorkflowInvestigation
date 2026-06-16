---
source_type: ai-generated-draft
title: "Copilot research report: Temporal, Azure Durable Task, and Microsoft Agent Framework Durable Extension process manager capability comparison"
origin: "GitHub Copilot CLI research output synthesized from focused GPT-5.5 research subagents and adversarial review"
generator: "GitHub Copilot CLI"
recorded: 2026-06-16
language: zh-Hans
topic: "Bare-metal Cluster Buildout process manager platform capability comparison"
authority: "non-authoritative"
raw_admission_reason: "User requested deeper research on the three primary candidates selected by wiki/analyses/bare-metal-cluster-buildout-process-manager-selection.md, with multi-agent GPT-5.5 review, and asked to preserve the resulting draft under raw/10-ai-generated-drafts/."
preservation_mode: ai-research-report
full_text_preserved: true
cleanup_note: "Generated as raw research only; primary-source claims must be rechecked before wiki synthesis, architecture baseline, procurement, or implementation decisions."
---

> [!WARNING] 非权威 AI 调研草稿
> 本文件是 GitHub Copilot CLI 生成的调研草稿，综合了本仓库已有 source projections、2026-06-16 对官方文档的轻量复核，以及三个独立 GPT-5.5 研究子代理的机制级调研。它不是 `wiki/` 结论，也不是采购、架构或实现决策依据。复用其中任何产品能力、版本状态、源码解释、成熟度判断或选型建议前，必须回到一手文档、源码、官方 release notes 或已投影的 wiki source page 重新核验，并建立明确的 claim-to-evidence 映射。

# Temporal、Azure Durable Task 与 MAF Durable Extension 的 Process Manager 能力差异调研

## 调研边界

本草稿只回答一个问题：

**在裸金属 Cluster Buildout 主 process manager 选型中，Temporal、Azure Durable Functions / Durable Task、Microsoft Agent Framework Durable Workflow Extension 这三个强候选的能力差异到底是什么？**

本草稿不重新比较 Airflow、LangGraph、Kubernetes/GitOps、CI/CD pipeline、裸金属下层 provisioning 工具，也不做采购排序。现有 wiki analysis 已经把 Airflow 与 LangGraph 降为非同一 scope 的主候选。本草稿只深入三者之间的机制差异，供后续 wiki synthesis 或 POC 设计使用。

证据截止时间为 2026-06-16。调研方式是：

1. 读取 `wiki/analyses/bare-metal-cluster-buildout-process-manager-selection.md` 的当前候选边界。
2. 读取本仓库已有 Temporal、Azure Durable Functions / Durable Task、Microsoft Agent Framework source projections。
3. 轻量复核关键官方文档 URL 的当前内容。
4. 使用三个独立 GPT-5.5 research subagents 分别调研 Temporal、Azure Durable Task 和 MAF Durable Extension。
5. 用多个 GPT-5.5 review subagents 对草稿做阻断性审查，并按审查意见迭代；审查结果见末尾。

## 执行结论

三个候选都能进入第一批 POC，但它们不是“同一种东西换术语”。

最重要的分层结论是：

1. **Temporal 是独立的通用 durable process runtime。**
   它的核心对象是 Workflow Execution、Workflow ID、Event History、Activity、Signal/Query/Update、Timer、Child Workflow、Task Queue、Worker、Namespace。它更像一个可自托管或云托管的 durable execution platform，适合把长期 buildout 过程作为可寻址过程对象建模。
2. **Azure Durable Functions / Durable Task 是 Durable Task runtime 生态加 Azure hosting/backend 产品面。**
   它与 Temporal 在 durable orchestration 基本能力上非常接近：orchestration instance、event sourcing、replay、activity、sub-orchestration、durable timer、external event、entity、continue-as-new、orchestration versioning 都是实质能力。真正差异在 Functions hosting、standalone SDK、Durable Task Scheduler managed backend、storage provider、Azure Functions triggers、Application Insights、private endpoint、SDK 成熟度和 air-gapped 边界。
3. **Microsoft Agent Framework Durable Workflow Extension 是 Durable Task-backed 的 agent/workflow 集成层，不是新的底层 durable engine。**
   它把 Microsoft Agent Framework graph workflow、executor、agent entity、request port、HITL、agent thread 和 Durable Task execution 接起来；在 Azure Functions hosting / 已核验源码路径中还出现 generated endpoints。它的额外价值是 AI-native / multi-agent / HITL 开发效率；额外风险是 graph/executor/superstep 到 Durable Task orchestration/activity/entity/external event 的映射复杂度、preview 成熟度、graph topology 兼容和诊断成本。

因此，三者的差异既有本质层级差异，也有程度差异：

- **Temporal vs Azure Durable Task**：同属 durable orchestration 底座，核心能力不是有无差异，而是控制面所有权、hosting/backend、worker routing、message model、版本治理、reset/debug 运维和 Azure 集成程度的差异。
- **Azure Durable Task vs MAF Durable Extension**：存在本质层级差异。MAF Durable 的底层 durable 能力主要继承 Durable Task；它额外提供 Agent Framework 的 graph/agent/HITL surface。
- **Temporal vs MAF Durable Extension**：存在本质抽象差异。Temporal 更像通用 process substrate；MAF Durable 更像 AI workflow productization layer。若 AI/HITL 是主控制路径，MAF 可能更自然；若核心是基础设施长事务，Temporal 或直接 Durable Task 更接近底层过程管理。

## 共同底座：哪些不是三者之间的决定性差异

不要把以下共同工程前提写成某个候选的专属缺陷：

| 共同前提 | 为什么不是候选专属缺陷 |
| --- | --- |
| external inventory/resource graph | Temporal Event History、Durable Task task hub/state、MAF checkpoint/custom status 都不是 node/rack/BMC/firmware/OS/network/validation 的业务事实库。 |
| 幂等键、读后校验、外部锁和补偿 | Temporal Activity、Durable activity、MAF executor activity 都可能重试；真实物理副作用必须由业务层保护。 |
| command gateway、auth、schema、dedup、audit | Signal、Update、external event、RequestPort 都是 runtime message entry；它们不是完整业务 API gateway。 |
| business dashboard | Temporal UI、Durable Task Scheduler dashboard、Application Insights 或 MAF Azure Functions hosting / 已核验源码路径中的 generated status endpoint 都不是裸金属操作员产品界面。 |
| replay / reset / rerun 跨物理副作用边界 | 任何 runtime 恢复或重放，只要跨越刷固件、重启、装 OS、换线、Slurm 验收等动作，都必须先 reconcile 外部事实和真实设备状态。 |

真正要比较的是：**在这些共同前提都成立后，哪个 runtime 的一手对象更自然地承载长期过程身份、事件入口、局部失败追平、版本演进和副作用边界；以及为了满足这些前提，需要把多少主过程控制逻辑放到 runtime 之外。**

## 能力差异总表

| 维度 | Temporal | Azure Durable Functions / Durable Task | MAF Durable Workflow Extension | 能力差异判断 |
| --- | --- | --- | --- | --- |
| 抽象层级 | 通用 durable execution platform。 | Durable Task runtime + Durable Functions / standalone SDK hosting + backend providers。 | Agent Framework graph/agent/HITL integration layer backed by Durable Task。 | MAF 与另外两者不是同一层；Temporal 与 Durable Task 更接近同层。 |
| 长期过程身份 | Workflow ID + Run ID；同一 Namespace 内 Workflow ID 可作为业务过程标识；Continue-As-New 保持 Workflow ID 并换 Run ID。 | Orchestration instance ID；可指定，也可随机；非随机 ID 适合外部实体映射，但官方建议默认随机 ID 以利 scale-out。 | Graph workflow run / Durable Task orchestration instance / agent entity / request port 的组合映射；需要显式说明资源身份穿过 graph 与 Durable Task 的方式。 | Temporal 的过程对象最直接；Azure 具备相邻能力；MAF 多一层 graph/executor 映射。 |
| 资源分区 | Child Workflow 可用 host/node/rack/fabric 等资源身份分区，并有独立 Event History。Task Queue 可按 worker fleet / 网络域 / 能力路由。 | Sub-orchestration 可拆分子流程；entities 可做小状态串行协调；task hub 持有 instance/entity state 和 messages。 | Subworkflow executor 映射 sub-orchestration；普通 executor 映射 activity；agent executor 映射 Durable Entity；RequestPort 映射 external event。 | Azure 与 MAF 有分区能力，但资源过程 contract 需要更多架构约定；Temporal Child Workflow + Workflow ID 更容易作为 reference architecture。 |
| 运行中交互 | Signal 异步；Query 同步只读；Update 可验证、可追踪、可返回结果。 | External event 是 one-way async；instance management APIs 可 start/query/terminate/suspend/resume/purge，但多数是 runtime control-plane / enqueue 语义，不等于同步业务 command result。 | RequestPort/HITL 映射 external event；Azure Functions 可自动生成 status/respond endpoint；agent session/thread 可被 durable storage 维护。 | Temporal 的 Update/Query/Signal 三分法对 command/read/mutate 边界更强；Azure/MAF 需要 command service 补齐同步语义和审计。 |
| 长等待 | Timer 是 Workflow Execution 内持久等待。 | Durable timer 支持等待和 timeout；语言与 hosting 可能影响长 timer 边界，JS/Python/PowerShell Durable Functions 文档提到六天限制，.NET/Java 支持任意长 timer。 | 继承 Durable Task timer/external event 等待；RequestPort wait 文档/源码语义更偏 HITL，timeout 需额外建模。 | 三者都能长等待；差异在语言/hosting 与具体 message surface。 |
| 副作用边界 | Activity 是外部 I/O 和真实世界副作用边界；Workflow replay 不重跑已完成 Activity；Activity heartbeat 可用于长 activity checkpoint。 | Activity 是副作用边界；orchestrator deterministic，外部 I/O 放 activity；retry/timeout 与进度 checkpoint 需要按 SDK/业务设计。 | 普通 executor 作为 Durable Task activity；agent entity、subworkflow、RequestPort 走专门路径。 | Temporal 对长 activity heartbeat/progress 的一手支持更强；Azure/MAF 可做但往往需要外部状态或分段 activity。 |
| 恢复语义 | Event History + replay；Reset 可基于 reset point 创建新 execution；Continue-As-New 用 fresh history 接续；Worker Versioning 支持 deployment routing。 | Event sourcing + execution history + replay；continue-as-new、suspend/resume、terminate/purge、orchestration versioning；未发现与 Temporal Reset 完全等价的通用 reset point 复制能力。 | Durable Task replay + graph workflow mapping；standard checkpoint storage 与 Durable Extension checkpoint/recover 不应混淆。 | 核心 replay 同类；Temporal 运维恢复和 rollout 工具更平台化；Azure versioning 已缩小差距；MAF 叠加 graph topology 兼容风险。 |
| 版本治理 | Workflow patching/GetVersion、Worker Versioning、Pinned/Auto-Upgrade、ramping/draining 等生产部署语义。 | Orchestration versioning 让 instance 创建时绑定 version，orchestrator 可读 `context.Version` 分支，worker/client 可做 version matching；依赖具体 hosting/SDK 版本。 | 未发现同等 MAF graph topology versioning API；需要底层 Durable Task versioning、workflow 名称版本化、side-by-side workers 或 drain 策略。 | 不能再说 Azure 没有 versioning；更准确差异是 Temporal 的 worker deployment lifecycle 更完整，MAF 的 graph 兼容需 PoC。 |
| hosting/backend | Temporal Cloud 或 self-host Temporal Service；用户 worker 在 Service 外运行；Task Queue 显式路由。 | Durable Functions 使用 Azure Functions hosting；standalone Durable Task SDK 可在 AKS/VM/on-prem compute 运行，但现代 SDK 连接 Durable Task Scheduler managed backend；Durable Functions 可选 Scheduler、Azure Storage、MSSQL、Netherite 等 storage provider。 | Azure Functions hosting 或 BYOC/self-host worker；self-host 表示自管 worker/process/container/Kubernetes，不等于自带 durable backend，仍连接 Durable Task Scheduler。 | 完全自托管/air-gapped 时 Temporal 边界更自然；Azure Durable Functions + MSSQL 可能支持 disconnected，但 standalone SDK / MAF Durable 当前更 Azure Scheduler-centered。 |
| 可观测/诊断 | Temporal UI/CLI/Visibility/metrics 可看 workflow runtime；业务 dashboard 仍需投影。 | Application Insights、Durable Functions management APIs、Durable Task Scheduler dashboard；业务 dashboard 仍需投影。 | DTS dashboard + MAF status/streaming；generated endpoints 需限定在 Azure Functions hosting / 已核验源码路径。诊断要跨 MAF graph、Durable Task orchestration、agent entity 和 hosting。 | Azure/MAF 产品化入口更强；MAF 中间层可能增加根因定位成本。 |
| AI/HITL | 通过 Activity、Signal/Query/Update、外部 agent platform 集成；不是 AI-native 产品层。 | 通过 activity、external events、entities、Functions triggers 和外部服务集成。 | Agents、multi-agent orchestration、agent sessions、RequestPort/HITL、MCP trigger、reliable streaming pattern 是一手能力；generated endpoints 需按 Azure Functions hosting 与目标语言/源码路径限定。 | 如果 AI/HITL 是主控制路径，MAF 有实质额外能力；如果只是 adapter，Temporal/Azure + 外部 agent platform 更小。 |
| 成熟度信号 | 通用 runtime 成熟；具体自托管/Cloud/SDK/worker versioning 仍需目标版本核验。 | Durable Functions 成熟；standalone SDK .NET/Python/Java GA、JS/TS Preview；Scheduler 是 Azure managed backend。 | 文档安装使用 `--pre` / `--prerelease`；NuGet/PyPI 包状态需目标版本复核；应按 preview 风险处理。 | MAF 不宜写成与 Temporal 同等成熟的通用 process manager 底座。 |

## Temporal：最直接的通用 process runtime 候选

Temporal 的强点不是“它能跑任务”，而是它把长期过程作为可寻址、可交互、可恢复的 durable execution 对象。

对裸金属 buildout，Temporal reference architecture 可自然表达为：

- `cluster-buildout/{cluster-id}` 是 cluster 级 Workflow Execution。
- node、rack、fabric、validation domain 可作为 Child Workflow 分区。
- BMC/Redfish、MAAS/Ironic/Tinkerbell、PXE、OS install、Slurm validation、通知和 agent 调用落在 Activity。
- 供应商回执、人工审批、现场修复、资源追加、跳过/重跑请求通过 Signal 或 Update 进入运行中 Workflow。
- Query 暴露当前过程状态；业务 dashboard 从 Temporal visibility、external inventory 和下层控制面投影。
- Continue-As-New 用作 Event History 截断和 Run 边界状态交接。
- Worker Versioning 管理长运行 Workflow 期间的 worker code routing。

这组对象与裸金属 buildout 的长期、交互式、资源实体导向过程很贴近。尤其是 Workflow ID、Child Workflow、Signal/Query/Update、Timer、Activity、Task Queue 和 Worker Versioning 组合起来，能形成清晰的 process manager spine。

但必须降调：

- Temporal Event History 不是裸金属 inventory。
- Reset 不是物理回滚。
- Continue-As-New 不是任意计划热迁移。
- Worker Versioning 不是业务状态自动迁移。
- Activity retry 不是 exactly-once，也不是硬件操作幂等。
- Signal/Update 不是完整 command gateway。
- Temporal UI 不是业务 operator dashboard。
- Activity heartbeat 可保存进度线索，但不是物理子步骤事务 checkpoint；恢复仍需业务 resume/idempotency 设计。

所以 Temporal 的合理定位是：**最强通用 durable process manager substrate / reference architecture 候选，而不是完整 cluster buildout suite。**

## Azure Durable Functions / Durable Task：与 Temporal 同类但 Azure 产品边界更强

Azure Durable Task 的核心能力不能低估。Durable orchestration 使用 orchestrator function 协调 activity，支持长期实例、event sourcing、execution history、checkpoint/replay、sub-orchestration、durable timer、external event、entity、instance management 和 orchestration versioning。

这意味着 Azure Durable Functions / Durable Task 应作为 Temporal 同批 durable orchestration 强候选，而不是外围 adapter。

真正差异在三层边界：

1. **Durable Functions 产品面。**
   它运行在 Azure Functions runtime 内，获得 Functions triggers、bindings、自动 scale、HTTP management APIs、Azure portal、Application Insights、hosting plans、identity/network integration 等能力。代价是选型必须先确定 Functions hosting plan、cold start、network、container、scale、成本和触发器边界。
2. **Standalone Durable Task SDKs。**
   它们可在 AKS、VM、on-premises 等 compute 上运行 worker/client，不要求 Azure Functions runtime。但 2026-06 的当前 Microsoft Learn Durable Task SDKs 文档显示这些 SDK 连接 Durable Task Scheduler 作为 managed backend。因此“worker 可跑在任意 compute”不等于“durable backend 完全本地自足”。
3. **Storage/backend providers。**
   Durable Functions 支持 Durable Task Scheduler、Azure Storage、MSSQL、Netherite 等 backend。MSSQL provider 文档说明 disconnected environments 可用；但 standalone SDKs 文档指向 Scheduler managed backend。这会直接影响完全离线裸金属控制面的可行性。

Azure Durable 的强项：

- Azure-first 组织的身份、网络、监控、合规和运营整合。
- Durable Task Scheduler managed backend、dashboard、private endpoints。
- Durable Entities 作为小块状态和串行 operation primitive。
- Durable Functions trigger/binding 生态。
- Orchestration versioning 已经是正式能力，不能再写成缺失项。

Azure Durable 的主要待证点：

- resource-derived instance ID 是否会造成热点或负载分布问题。
- external event one-way async 如何补齐 command validation/result。
- standalone SDK + Scheduler 是否满足目标私网、延迟、可用性和合规要求。
- Durable Functions + MSSQL disconnected 是否适合目标 air-gapped buildout，而不是只作为理论路线。
- management APIs 的 terminate/suspend/resume/purge 与真实设备副作用之间如何建立安全边界。

合理定位是：**Azure-connected 或 Azure-first 环境中的强 durable orchestration 候选；若要求完全自托管、完全离线、独立后端，必须把 backend 边界作为 POC blocker。**

## Microsoft Agent Framework Durable Workflow Extension：AI-native layer，而不是第三套底层 engine

MAF Durable Extension 的最大价值在 AI/agent/HITL surface，而不是替代 Temporal 或 Durable Task 的底层 durable runtime。

现有证据显示，它把 Durable Task-backed execution 引入 Agent Framework agents、multi-agent orchestrations 和 graph-based workflows。graph workflow 由 executors、edges、superstep / BSP execution model 表达。Durable Extension 通过 `ConfigureDurableWorkflows` 等路径把 graph workflow 注册到 Durable Task：普通 executor 走 activity，agent executor 走 Durable Entity，subworkflow 走 sub-orchestration，RequestPort/HITL 走 external event。

这带来真实能力：

- agent session / thread 可持久化。
- multi-agent orchestration 更直接。
- RequestPort/HITL 是 framework surface。
- Azure Functions hosting / 已核验源码路径可生成 agent/workflow endpoints；不要把该能力无条件外推到所有语言、workflow surface 或 self-hosted hosting。
- MCP trigger、reliable streaming pattern、DTS dashboard 等产品化体验更接近 AI operator workflow。

但这些能力也带来额外边界：

- Durable Extension 不是新的 durable backend；按当前文档，self-hosted worker 仍连接 Durable Task Scheduler。
- 已确认的 durable workflow 重点是 graph-based workflow；functional workflow surface 与 durable parity 需要按目标语言和版本实测。
- preview / prerelease 包状态必须进入风险模型。
- graph topology、executor name、edge condition、fan-in/fan-out、binding 类型变更可能影响 Durable Task replay command sequence 或后续 routing 语义；该判断主要来自 .NET Durable Extension 源码和 Durable Task replay 机制，目标语言需实测。
- 诊断需要同时理解 MAF graph/superstep、Durable Task orchestration/activity/entity/external event、hosting worker 和 DTS dashboard。
- RequestPort/HITL 是强机制，但 timeout、dead-letter、auth、重复 event、审批审计仍需应用层设计。

因此，MAF Durable 的合理定位是：**如果 AI diagnosis、multi-agent collaboration、operator approval 和 HITL 是 buildout 主控制路径的一手能力，它应作为 AI-native baseline 同批 POC；如果 AI/HITL 只是辅助 adapter，它更适合作为 Temporal/Azure Durable Task 之上的 agent/HITL facade，而不是替代底层 process manager。**

## 三类差异的本质解释

### 1. 过程身份差异

裸金属 buildout 的主 process manager 必须回答：

- 这个 cluster buildout 的长期身份在哪里？
- `node-42`、rack、fabric、switch port、BMC 等局部资源过程如何被寻址？
- 两天后人工修复网线，事件路由到哪个运行中对象？
- 只追平受影响节点还是重跑整批任务？

Temporal 的答案最直接：Workflow ID / Child Workflow ID 是长期过程身份锚点。Azure 的答案是 orchestration instance ID / sub-orchestration / entity，但必须同时考虑 task hub、instance ID 负载分布和 external entity 映射。MAF 的答案需要穿过 graph workflow run、executor、subworkflow、agent entity、RequestPort 和底层 Durable Task instance/entity。

这不是“能不能做”的差异，而是**架构映射的直接程度和诊断成本**差异。

### 2. 运行中事件差异

裸金属 buildout 不是一次性 DAG。它会收到人工批准、供应商回执、BMC event、provisioning result、validation failure、现场修复、追加节点、撤销 override 等事件。

Temporal 把运行中 Workflow 暴露为类似 stateful service 的对象：Signal 改变状态但不返回，Query 同步读取，Update 可校验、可追踪、可返回结果。Azure Durable external event 能把事件送入运行中 orchestration，但官方文档明确它是 one-way async，不适合发送者需要同步 response 的场景。MAF RequestPort/HITL 把人工输入做成 framework surface，但底层仍映射 external event。

因此，差异不是“谁能接事件”，而是**事件进入运行中对象后是否有一手 command/read/update 语义，以及同步业务结果和审计需要补多少外层服务**。

### 3. 恢复与版本差异

三者都绕不开 deterministic replay。差异在恢复/版本运维工具的形态：

- Temporal 的 Reset、Continue-As-New、patching/GetVersion、Worker Versioning、Task Queue/worker routing 更像 workflow platform 的生产运维闭环。
- Azure Durable Task 有 event sourcing/replay、continue-as-new、management APIs、orchestration versioning、worker/client version matching，但与 hosting/backend/provider 选择紧密耦合。
- MAF Durable 继承 Durable Task replay/versioning 基本纪律，还叠加 graph definition、executor binding、superstep、agent entity、RequestPort 和 checkpoint shape 的兼容性。

因此，不能把 Azure 写成“无版本能力”，也不能把 Temporal 写成“任意迁移能力”。正确说法是：**Azure 的版本差距已经缩小；Temporal 的生产 rollout 和 reset/debug 语义更平台化；MAF 的 graph topology 兼容性是额外待证点。**

## 推荐 POC gates

这三个候选不应靠文档表格直接排序。至少要做同一套 POC，并区分共同 gate 与候选特有 gate。

### 共同 gates

- external inventory/resource graph 保存 node、rack、BMC、firmware、OS image、network、validation result、lock、audit projection。
- 所有 device/provisioning/scheduler side effects 都有幂等键、读后校验、补偿和人工确认。
- 业务 command gateway 处理 auth、schema、dedup、ordering、同步/异步 result、audit。
- runtime state 到 operator dashboard 有独立 projection，不依赖 runtime UI 解释业务状态。
- replay/reset/rerun/continue-as-new/terminate 后的后续副作用必须先 reconcile external facts。

### Temporal 特有 gates

- 用 Workflow ID / Child Workflow ID 表达 cluster、node、rack、fabric 的长期身份。
- 验证 Signal/Query/Update 对审批、追加节点、跳过重跑和供应商回执的 command/read/update 语义。
- 验证 Activity heartbeat、timeout、retry 和 idempotency key 对固件、OS install、Slurm validation 的保护。
- 验证 Reset 前后的危险 Activity guard，不允许无条件重放物理副作用。
- 验证 Worker Versioning 的 Pinned vs Auto-Upgrade 策略、Event History 增长、Continue-As-New 边界和 visibility/dashboard projection。

### Azure Durable Task 特有 gates

- 明确最终是 Durable Functions 还是 standalone Durable Task SDK。
- 若是 standalone SDK，验证 Durable Task Scheduler managed backend、private endpoint、on-prem worker connectivity、latency、availability、payload limit、dashboard access。
- 若是 Durable Functions，验证 hosting plan、cold start、network/container support、storage provider、Application Insights、built-in HTTP management API 和 Functions trigger 边界。
- 验证 resource-derived instance ID 与 sub-orchestration 是否造成热点；验证 entities 是否只用于小状态协调而不替代资源图。
- 验证 external event one-way async 如何补齐 command validation/result。
- 验证 orchestration versioning 对在途 buildout 的新旧逻辑并存和 worker compatibility。

### MAF Durable Extension 特有 gates

- 明确目标 workflow 是否实际运行在 Durable Extension-backed graph workflow 上，而不是 standard checkpoint 或 functional workflow surface。
- 验证 graph workflow instance、executor、agent entity、subworkflow、RequestPort 到 Durable Task instance/activity/entity/external event 的资源身份映射。
- 验证 graph topology / executor name / edge / fan-in/fan-out 变更对 replay 和 in-flight instance 的影响。
- 验证 preview package、目标语言、Azure Functions vs self-hosted worker、Durable Task Scheduler backend、generated endpoints、auth/RBAC/network isolation。
- 验证 RequestPort/HITL 的 timeout、重复 event、dead-letter、operator audit、approval cancellation。
- 验证 MAF 中间层的观测与诊断成本是否低于 Temporal/Azure Durable Task + 外部 agent platform。

## 证据索引

以下证据只作为本草稿的线索索引。正式进入 wiki 时应回到 source page 或一手 URL 重新建立 claim-to-evidence 映射。

### 本仓库已有 source projections

- `wiki/sources/temporal/workflows-docs.md`
- `wiki/sources/temporal/message-passing-docs.md`
- `wiki/sources/temporal/activities-docs.md`
- `wiki/sources/temporal/child-workflows-docs.md`
- `wiki/sources/temporal/timers-delays-docs.md`
- `wiki/sources/temporal/reset-docs.md`
- `wiki/sources/temporal/continue-as-new-docs.md`
- `wiki/sources/temporal/workflow-versioning-docs.md`
- `wiki/sources/temporal/worker-versioning-docs.md`
- `wiki/sources/azure-durable-functions/orchestrations-docs.md`
- `wiki/sources/azure-durable-functions/external-events-docs.md`
- `wiki/sources/azure-durable-functions/entities-docs.md`
- `wiki/sources/azure-durable-functions/timers-docs.md`
- `wiki/sources/azure-durable-functions/instance-management-docs.md`
- `wiki/sources/azure-durable-functions/orchestration-versioning-docs.md`
- `wiki/sources/azure-durable-functions/hosting-model-docs.md`
- `wiki/sources/azure-durable-functions/storage-providers-docs.md`
- `wiki/sources/microsoft-durable-task/sdk-overview-docs.md`
- `wiki/sources/microsoft-durable-task/scheduler-docs.md`
- `wiki/sources/microsoft-agent-framework/durable-extension-docs.md`
- `wiki/sources/microsoft-agent-framework/durable-workflow-registration-source.md`
- `wiki/sources/microsoft-agent-framework/durable-executor-dispatcher-source.md`
- `wiki/sources/microsoft-agent-framework/checkpoints-docs.md`
- `wiki/sources/microsoft-agent-framework/state-docs.md`
- `wiki/sources/microsoft-agent-framework/python-workflow-runner-source.md`

### 2026-06-16 轻量复核的一手 URL

- `https://docs.temporal.io/workflows`
- `https://docs.temporal.io/develop/typescript/workflows/message-passing`
- `https://docs.temporal.io/activities`
- `https://docs.temporal.io/task-queue`
- `https://docs.temporal.io/self-hosted-guide`
- `https://docs.temporal.io/cloud`
- `https://docs.temporal.io/web-ui`
- `https://docs.temporal.io/self-hosted-guide/visibility`
- `https://docs.temporal.io/references/cluster-metrics`
- `https://learn.microsoft.com/en-us/azure/durable-task/common/durable-task-orchestrations`
- `https://learn.microsoft.com/en-us/azure/durable-task/common/durable-task-external-events`
- `https://learn.microsoft.com/en-us/azure/durable-task/common/durable-orchestration-versioning`
- `https://learn.microsoft.com/en-us/azure/durable-task/common/choose-orchestration-framework`
- `https://learn.microsoft.com/en-us/azure/durable-task/common/durable-task-storage-providers`
- `https://learn.microsoft.com/en-us/azure/durable-task/common/durable-task-hubs`
- `https://learn.microsoft.com/en-us/azure/durable-task/common/durable-task-sub-orchestrations`
- `https://learn.microsoft.com/en-us/azure/durable-task/sdks/durable-task-overview`
- `https://learn.microsoft.com/en-us/azure/durable-task/scheduler/durable-task-scheduler`
- `https://learn.microsoft.com/en-us/agent-framework/integrations/durable-extension`
- `https://learn.microsoft.com/en-us/agent-framework/workflows/workflows`

## 审查记录

本草稿经过两个独立 GPT-5.5 review subagents 审查。

- **Capability reviewer**：无 blocking issues，结论为 approve。建议补充 Temporal Activity heartbeat 不是物理事务 checkpoint，并继续用 POC 验证 MAF graph topology/versioning 风险。
- **Evidence reviewer**：第一轮结论为 needs-revision，指出 Temporal Task Queue、self-host/cloud、Web UI/Visibility/metrics、workflow versioning 证据索引不足，MAF generated endpoints / RequestPort/HITL 映射需要按 hosting、语言和源码路径限定，且审查记录与 frontmatter 不一致。
- **已处理的修正**：补充 Temporal workflow versioning source page 和 Task Queue、self-hosted guide、Cloud guide、Web UI、Visibility、metrics 一手 URL；把 MAF generated endpoints、RequestPort/HITL 和 graph topology 风险收紧到已核验 hosting/source/language 边界；补充 Activity heartbeat 降调说明；把 standalone SDK 表述限定为 2026-06 当前 Microsoft Learn 文档；更新本审查记录。
- **最终审查状态**：修订后 Evidence reviewer 复审无 blocking issues，结论为 approve；Capability reviewer 复审无 blocking issues，结论为 approve。剩余建议均为进入 wiki 前的证据映射或 POC 事项，不阻断本 raw 草稿交付。
