---
source_type: ai-generated-draft
title: "Copilot research report: Temporal vs Azure Durable Functions selection comparison"
origin: "GitHub Copilot CLI research output synthesized from focused research subagents and adversarial review"
generator: "GitHub Copilot CLI"
recorded: 2026-06-15
language: zh-Hans
topic: "Workflow platform selection"
authority: "non-authoritative"
raw_admission_reason: "User requested a new follow-up research draft because the previous Azure Durable Functions / Dapr Workflow draft did not distinguish Temporal and Azure Durable Functions enough for selection."
preservation_mode: ai-research-report
full_text_preserved: true
cleanup_note: "Generated as raw selection research only; primary-source claims must be rechecked before wiki synthesis or product decision."
---

> [!WARNING] 非权威 AI 调研草稿
> 本文件是 GitHub Copilot CLI 生成的选型调研草稿。它不是最终 wiki 结论，也不是采购、架构或迁移决策依据。复用其中任何产品能力、版本状态、配额、成本模型或建议前，必须回到一手文档、源码、官方价格页或已有 wiki source page 重新核验，并在 `wiki/` 中建立明确的 claim-to-evidence 映射。

# Temporal vs Azure Durable Functions 选型对比调研

## 调研边界与判断方式

本报告专门回答一个问题：**当 Temporal 和 Azure Durable Functions 都能表达 event-history / replay durable workflow 时，工程团队应如何选型？**

上一份草稿已确认二者都属于 history/replay durable execution 模式：workflow/orchestrator 代码在恢复时 replay，副作用放在 activity，代码必须确定性。这个共同点不能继续作为主判断。本报告把 replay 视为共同底座，重点比较真正拉开差距的工程维度：

1. 控制面与运行时所有权。
2. worker / task routing / scale-out 模型。
3. live workflow interaction：Signal / Query / Update vs External Event / status API。
4. 版本演进、部署和 replay safety。
5. 长运行 activity、heartbeat、timeout 和外部副作用控制。
6. history growth、Continue-As-New、reset/debug/recovery。
7. Azure-native 集成、可移植性、成本形态和运维责任。

证据截止时间是 2026-06-15。调研优先使用 Temporal 官方文档、Microsoft Learn Durable Task / Durable Functions 文档，以及官方 CLI/architecture 文档。所有结论仍需正式入 wiki 前复核。

## 执行摘要

Temporal 和 Azure Durable Functions 的共同点很强：二者都提供 code-defined durable workflow、event history replay、activity 作为副作用边界、durable timer、child workflow/sub-orchestration、retry、Continue-As-New 以及确定性约束。**因此“是否能做长期 workflow”不是选型分水岭。**[^temporal-replay][^adf-orchestrations]

真正的选择是：**Temporal 是 portable、worker/task-queue-oriented、workflow-platform-first 的系统；Azure Durable Functions 是 Azure-native、Functions/serverless-first、provider-dependent Durable Task 产品入口。** Temporal 把用户代码运行在自有 worker fleet 中，通过 Task Queue 显式路由；Azure Durable Functions 把代码放入 Azure Functions host，状态交给 Task Hub / storage provider / Durable Task Scheduler，默认获得 Azure Functions 触发器、托管身份、Application Insights、RBAC、scale-to-zero 等生态能力。[^temporal-workers][^temporal-taskqueue][^adf-overview][^adf-storage-providers]

如果团队需要跨云/自托管一致性、显式 worker routing、polyglot worker fleet、Temporal Update、Activity heartbeat、Worker Versioning、Replay Testing、Reset / batch reset 等高级 workflow platform 能力，Temporal 更强。[^temporal-messages][^temporal-heartbeat][^temporal-versioning][^temporal-cli]

如果团队已经 Azure Functions 化，工作流主要围绕 Azure 事件源、PaaS 集成、托管身份、Azure Monitor / Application Insights、消费型/突发型成本、Durable Entities 或 Microsoft 一方 Azure 资源合规边界，Azure Durable Functions 更合适。尤其在 Durable Task Scheduler 成为推荐后端后，ADF 的“只是 Azure Storage polling”印象已经过时；但 provider 选择、payload/retention/throughput、backend migration 不支持等限制必须提前纳入设计。[^adf-scheduler][^adf-billing][^adf-entities]

## 第一性能力模型

| 维度 | 真正问题 | Temporal | Azure Durable Functions |
| --- | --- | --- | --- |
| 控制面 | 谁拥有 durable execution 状态与调度？ | Temporal Service：History、Matching、Frontend 等服务；Cloud 或自托管。 | Azure Functions + Durable Task extension；状态在 Task Hub 对应的 provider / Durable Task Scheduler。 |
| 用户代码 | 谁运行 worker？ | 用户运行 worker；Temporal Cloud 也不托管用户 worker。 | Azure Functions host 运行 function code；平台负责 function scale-out。 |
| 工作路由 | 能否按能力、资源、语言、优先级路由任务？ | Task Queue 是显式 routing primitive；worker long-poll。 | Task Hub 不是 Task Queue；路由更多依赖 function app / task hub / app routing / provider。 |
| 运行中交互 | 外部系统如何与一个正在运行的 workflow 对话？ | Signal / Query / Update 三分法；Update 可同步返回结果。 | External Event 是单向异步；status/custom status/entity/status API 是旁路能力。 |
| 长 activity | 长时间副作用如何报告进度和取消？ | Activity heartbeat 可携带 checkpoint，重试时读取 heartbeat details。 | 无 Temporal-style heartbeat；通常用外部存储、分段 activity 或 orchestrator 轮询。 |
| 部署演进 | 长运行实例如何安全穿过代码升级？ | Worker Versioning + patch/GetVersion；Pinned/Auto-Upgrade/ramp/drain。 | Orchestration Versioning + `context.Version`；slot swap、side-by-side、app routing 等策略。 |
| 历史治理 | history 过大如何被提前感知？ | 51,200 events / 50 MB hard limit，warning threshold，CAN discipline。 | 无统一公开 event count hard limit；provider 和 replay memory pressure 是主要边界。 |
| 恢复调试 | 坏部署/坏数据后能否批量修复？ | CLI reset/reset-batch/show history/replay test/stack/trace。 | terminate/suspend/resume/purge/raise event/status；rewind 仍需确认 GA 状态。 |
| 成本形态 | idle 与 burst 如何收费？ | Cloud：plan floor + actions + storage；worker compute 自付。Self-host：常驻 infra。 | Consumption/Flex 可 scale-to-zero；DTS Consumption pay-per-action；Dedicated CU 固定成本。 |
| 可移植性 | 是否要求云无关？ | 强：worker 可任意 compute，self-host 可任意云/本地。 | 自然路径强 Azure 耦合；MSSQL provider / standalone SDK 只部分降低耦合。 |

## Temporal 的选型强项

### 1. 独立 workflow platform 与显式 worker fleet

Temporal Server 不执行用户代码。用户代码在 worker processes 中运行，worker 通过 gRPC long-poll Task Queue。即使使用 Temporal Cloud，团队仍需要部署、扩缩容、监控和版本化自己的 workers。这个模型增加了平台责任，但带来显式控制：不同 worker pool 可以按语言、硬件、网络区域、优先级、数据本地性、成本层级绑定不同 Task Queue。[^temporal-workers][^temporal-taskqueue][^temporal-taskrouting]

选择含义：

- 如果你的 workflow 需要 GPU worker、专线内网 worker、客户私有网络 worker、Python ML worker、Java 业务 worker、Go 高吞吐 worker 分工，Temporal 的 Task Queue routing 是核心优势。
- 如果你的团队不想运营任何 worker 容器/VM/autoscaler，只想把代码交给 Azure Functions host，Temporal 的 worker 所有权会变成负担。

### 2. Signal / Query / Update 的交互语义更强

Temporal 把运行中 workflow 暴露成可交互对象：

- **Signal**：异步 fire-and-forget，写入 history，无返回值。
- **Query**：同步只读，不写 history，不推进 workflow。
- **Update**：同步 mutating request，可选 validator，接受后写 history，并可返回结果。

Azure Durable Functions 的 External Event 更接近 Signal：它适合 approval callback、webhook、人工输入、超时等待，但官方文档明确说 external events 是 one-way asynchronous operations，不适合 sender 需要 orchestrator 同步响应的场景。ADF 可以通过 `GetStatus`、custom status、entity call 或旁路 API 实现一些查询/响应需求，但没有 Temporal-style per-workflow Update handler with validator/result。[^temporal-messages][^adf-external-events]

选择含义：

- 如果业务需要“把这个请求投给正在运行的 workflow，workflow 校验、接受、执行并同步返回结果”，Temporal Update 是决定性差异。
- 如果只是“审批结果/回调到达后继续流程”，ADF External Event 已足够。

### 3. Activity heartbeat 与 timeout taxonomy 更适合长副作用

Temporal Activity 有独立 timeout 语义：Schedule-To-Start、Start-To-Close、Schedule-To-Close、Heartbeat Timeout。长时间 activity 可以 heartbeat，并在 heartbeat payload 中保存进度；worker crash 后下一次 retry 可读取 heartbeat details 继续。取消也依赖 heartbeat 路径送达。[^temporal-heartbeat][^temporal-retry]

ADF activity function 是副作用边界，也支持 retry options，但没有同等的一等 heartbeat/progress checkpoint primitive。长任务通常需要拆成多段 activity、把进度写外部数据库/blob/entity，或由 orchestrator durable timer 轮询外部状态。

选择含义：

- 长文件处理、批量迁移、ML 训练、供应链/设备操作等需要可恢复进度 checkpoint 的 activity，Temporal 更强。
- 如果 activity 都是短事务或天然可幂等重跑，ADF 的 retry model 足够。

### 4. Worker Versioning、patching 与 replay testing 形成更强演进闭环

Temporal 有两层演进工具：

1. `GetVersion` / patching 在 Event History 记录 marker，让新旧代码路径可安全共存。
2. Worker Versioning 让 workflow type 选择 Pinned 或 Auto-Upgrade；Pinned workflow 可保证在单个 Worker Deployment Version 上完成，版本进入 Draining/Drained 生命周期，支持 ramp percentage。[^temporal-versioning]

Temporal SDK 还支持将历史 JSON replay 到当前代码中做 replay testing，从而在 CI 中提前发现非确定性修改。[^temporal-replay-testing]

ADF 的演进能力在 2026 文档中已经明显增强：Orchestration Versioning 可通过 `defaultVersion` 和 `context.Version` 给新 instance 打版本，runtime 防止旧 worker 处理新版本 instance；也支持 name-based versioning、slot swap idle gate、side-by-side deployment、application routing 等策略。[^adf-versioning][^adf-orchestration-versioning]

但两者风格不同：

- Temporal 更偏 **deployment / worker routing / server-assisted draining**。
- ADF 更偏 **orchestration instance version + code branching + Azure deployment topology**。

选择含义：

- 长运行 workflow 很多、无法等全局 idle、需要 canary/ramp/drain 版本治理时，Temporal 更稳。
- Azure Functions 团队若能接受 `context.Version` 分支、slot/app routing 或 task hub isolation，ADF 版本差距已缩小，不应再写成“无版本能力”。

### 5. Reset、batch reset 与 replay-based debugging 更强

Temporal CLI / SDK 提供丰富的 workflow 运维面：show history、query、signal、cancel、terminate、delete、reset to event、reset-batch、stack、trace、describe reset points，并可把 history 导入 SDK replay test。Reset 可以从指定 history event 创建新的 execution，保留 reset point 之前的历史前缀；batch reset 能按 query 批量修复坏部署影响的 workflow。[^temporal-cli][^temporal-reset]

ADF 有 HTTP / SDK management API：get status、raise event、terminate、suspend、resume、purge、list instances；Application Insights + Kusto 是主诊断路径。HTTP API 中出现的 rewind 需特别确认当前 GA 状态，不能默认把它作为与 Temporal reset 等价的生产能力。[^adf-http-api][^adf-diagnostics][^adf-instance-management]

选择含义：

- 如果你预期经常需要对大量在途 workflow 做批量修复、reset、replay test，Temporal 是更强的平台。
- 如果故障处理主要是 terminate / replay from business source / rerun instance，ADF 的管理 API 可能足够。

## Azure Durable Functions 的选型强项

### 1. Azure Functions-native 与触发器生态

ADF 是 Azure Functions 的 Durable extension。它天然结合 HTTP、Timer、Queue、Service Bus、Event Grid、Blob、Cosmos DB 等触发器和 bindings；团队可以直接把 Azure event source 接成 workflow starter、activity 或 client function。Temporal 也能接这些事件，但需要自己写 trigger / bridge / worker 集成层。[^adf-overview]

选择含义：

- 如果系统主体已经是 Azure Functions + Event Grid / Service Bus / Storage Queue / Cosmos DB，ADF 的 glue code 最少。
- 如果系统主体是 Kubernetes 微服务，Temporal 的 worker model 可能更贴近当前架构。

### 2. Serverless / scale-to-zero 与低运维入口

ADF 运行在 Azure Functions hosting plan 上。Flex Consumption / Consumption 场景可在空闲时 scale-to-zero；Durable Task Scheduler Consumption SKU 也按 action 计费。对突发、低占空比 workflow，ADF 能做到非常低的 idle cost。[^adf-functions-scale][^adf-billing][^adf-scheduler-billing]

Temporal Cloud 消除了 server 运维，但仍有 plan floor、action/storage 计费，并且 worker compute 仍由团队运行；self-host Temporal 则需要常驻 service + database。[^temporal-cloud-pricing]

选择含义：

- 小团队、低频、突发、Azure-native 工作流，ADF 的成本/运维入口明显更低。
- 常态高负载、复杂 worker fleet、多语言系统，Temporal 的固定平台成本更容易被能力收益摊薄。

### 3. Azure RBAC、Managed Identity、Private Link、Application Insights 是一等公民

Durable Task Scheduler 使用 Managed Identity 认证，提供 `Durable Task Worker`、`Durable Task Data Contributor`、`Durable Task Data Reader` 等 RBAC 角色，可按 task hub 或 scheduler scope 授权；也支持 Private Endpoint / Azure Private Link。ADF 还自然进入 Azure Monitor、Application Insights、Key Vault、Azure Policy、ARM/Bicep/Terraform 等 Azure 运维体系。[^adf-scheduler-identity][^adf-private-endpoint][^adf-diagnostics]

Temporal Cloud/Self-host 也有 mTLS、API keys、Cloud IAM、metrics、audit 等能力，但会引入另一个控制面和合规边界；Temporal Cloud 当前区域与 Azure 原生区域并不等价，正式选型需重新核验最新 region list。[^temporal-cloud-security][^temporal-cloud-regions]

选择含义：

- 单一 Azure 合规/采购/身份边界是硬约束时，ADF 更自然。
- 如果团队已经接受第三方 SaaS 控制面或自托管控制面，Temporal 的独立性反而是优点。

### 4. Durable Entities 是原生 actor-like stateful primitive

ADF 除 orchestrator/activity 外，还有 Durable Entities：小型、命名、持久、串行 operation 的 stateful entity。它适合 counter、lock、aggregator、approval vote、shopping cart、resource state accumulator 等模式。Temporal 可用 workflow-per-entity / Signal / Continue-As-New 模式实现类似效果，但没有内置 Entity 类型。[^adf-entities]

选择含义：

- 如果工作流旁边需要大量轻量 actor-like 状态对象，ADF 的 Durable Entities 是真实差异点。
- 如果核心是长业务流程与 worker routing，而 entity-like 状态只是少数模式，Temporal 的 workflow-per-entity 足够。

### 5. Provider 选择给 ADF 多种运行形态

ADF 不只是 Azure Storage backend：

- Durable Task Scheduler：推荐托管后端，gRPC work-item delivery，高吞吐，Dashboard/RBAC/Private Link 等能力。
- Azure Storage：默认/原始后端，低门槛，但吞吐和 consistency 受 storage/queues/tables 形态影响。
- MSSQL：支持 disconnected / on-prem / air-gapped 环境，强一致、SQL backup/restore。
- Netherite：高吞吐但已有停止支持时间线。[^adf-storage-providers][^adf-scheduler]

关键限制是：**跨 provider 迁移不支持**。选错 provider 不是简单配置变更，而是创建新 app / 新 provider / 迁移业务层状态的问题。[^adf-storage-providers]

选择含义：

- Azure-native 托管：DTS。
- 最低门槛/存量：Azure Storage。
- 离线/本地：MSSQL。
- 不建议新项目依赖 Netherite 作为长期战略。

## 决策矩阵

| 场景 | 更推荐 | 原因 |
| --- | --- | --- |
| Azure Functions 存量系统，工作流由 Service Bus/Event Grid/HTTP/Timer 触发 | Azure Durable Functions | 原生触发器、bindings、Managed Identity、Application Insights、deployment slot。 |
| Kubernetes-first 平台，worker 已经容器化，跨 AWS/GCP/Azure/on-prem | Temporal | Worker/Task Queue 模型贴近容器平台；可自托管或 Temporal Cloud。 |
| 需要 GPU/ML/专线/客户私有网络 worker 分池 | Temporal | Task Queue routing 是一等能力。 |
| 简单审批、回调、定时器、fan-out/fan-in，Azure 内部应用 | Azure Durable Functions | External Event + durable timer + activity 已足够，运维成本低。 |
| 需要同步向运行中 workflow 发命令并拿到结果 | Temporal | Update 是一等同步变更请求；ADF External Event 是单向异步。 |
| 长 activity 需要进度 checkpoint、取消送达和 crash 后续跑 | Temporal | Activity heartbeat/details 是一等能力。 |
| 需要 actor-like 小型状态对象 | Azure Durable Functions | Durable Entities 原生支持；Temporal 需 pattern 实现。 |
| 长运行 workflow 需要 canary、ramp、drain、Pinned deployment | Temporal | Worker Versioning 更完整。 |
| 团队严格 Azure 单一供应商/合规边界 | Azure Durable Functions | Azure first-party resource、RBAC、Private Link、Azure support。 |
| 多云产品/不接受 Azure runtime 耦合 | Temporal | ADF 自然路径强 Azure 耦合；MSSQL/SDK 只是部分 escape hatch。 |
| 空闲时间长、请求量低、成本必须趋近零 | Azure Durable Functions | Consumption/Flex + DTS Consumption 可 scale-to-zero / pay-per-action。 |
| 坏部署后需要批量 reset 在途 workflow | Temporal | reset/reset-batch/replay test 更强。 |
| 完全 air-gapped 且已有 SQL Server 能力 | 二者都可 | Temporal self-host 可行；ADF + MSSQL provider 也可行，但要复核 SDK/Functions/provider 限制。 |

## 反直觉点与常见误判

### 误判 1：Temporal 比 ADF “更 durable”

不准确。ADF 同样使用 event sourcing + replay，同样可以等待天/月/年，同样有 durable timers、activities、external events、Continue-As-New。Temporal 更强的是 Task Queue routing、Update、heartbeat、Worker Versioning、history limits、reset/replay testing 等 platform surface，不是基本 durable execution 存不存在。[^adf-orchestrations][^temporal-replay]

### 误判 2：ADF 只是 Azure Storage queue polling

过时。Azure Storage 是原始/默认 provider，但当前 Microsoft 文档把 Durable Task Scheduler 描述为推荐后端，DTS 是 Azure resource、gRPC、Managed Identity、Dashboard、billing SKU、Private Endpoint 等独立产品面。选型必须先选 provider。[^adf-scheduler][^adf-storage-providers]

### 误判 3：ADF 没有版本能力

过时或过强。ADF 当前有 Orchestration Versioning、`defaultVersion`、`context.Version` 和 minimum package / extension bundle 要求；但它与 Temporal Worker Versioning 的语义不同。Temporal 更偏 worker deployment routing，ADF 更偏 instance version + code branch。[^adf-orchestration-versioning][^temporal-versioning]

### 误判 4：Temporal Cloud 后就没有运维了

不准确。Temporal Cloud 不运行用户 worker；worker compute、worker autoscaling、worker deployment、networking、mTLS/API key、payload encryption/data converter 仍由团队负责。Temporal Cloud 省掉的是 Temporal Server / DB / Matching / History 控制面运维。[^temporal-cloud-security][^temporal-workers]

### 误判 5：ADF 更简单，所以一定更弱

不准确。ADF 简化的是 Azure-native operational path，而不是底层 durable execution 能力。Durable Entities、Azure triggers、Managed Identity、Application Insights、scale-to-zero、DTS Dashboard 都是实用能力。真正风险是 provider lock-in、cross-provider migration 不支持、复杂 worker routing / Update / heartbeat / reset 工具不如 Temporal。[^adf-entities][^adf-storage-providers]

## 选型建议

### 默认选 Temporal，当以下条件成立

1. 系统需要跨云或长期避免 Azure runtime / storage lock-in。
2. workflow 是核心平台能力，不只是 Azure 应用里的一个后台流程。
3. 需要显式 task routing：不同语言、硬件、网络或安全域 worker。
4. 需要运行中 workflow 的同步命令语义：Update / Update-With-Start。
5. 长 activity 需要 heartbeat checkpoint 和可恢复进度。
6. 长运行实例很多，部署演进需要 Pinned/Auto-Upgrade/ramp/drain。
7. 生产事故处理依赖 reset、batch reset、replay test、history-level 调试。
8. 团队愿意运营 worker fleet，并接受 Temporal Cloud 或 self-host 控制面的成本。

### 默认选 Azure Durable Functions，当以下条件成立

1. 系统已深度 Azure Functions / Azure PaaS 化。
2. 触发源主要是 Azure-native event source，目标是最少 glue code。
3. 团队希望最小化 orchestration control plane 运维。
4. 工作负载突发、低频或高度 serverless，scale-to-zero / consumption 经济性很重要。
5. Azure Entra ID、Managed Identity、RBAC、Private Link、Application Insights 是硬性组织约束。
6. Simple-to-moderate workflow、approval、fan-out/fan-in、human callback 已满足业务需要。
7. Durable Entities 对 actor-like stateful aggregate 有显著价值。
8. 团队能在项目前期明确 provider 选择，并接受 backend 不可迁移约束。

### 真正需要 POC 的灰区

1. **高吞吐但 Azure-only**：DTS Dedicated CU 的 action/sec、payload limit、retention、task hub 配额与 Temporal Cloud / self-host throughput 需要按目标 workload 压测。
2. **长历史 / 大 fan-out**：Temporal 有硬 limit 和 CAN discipline；ADF provider 侧无统一 event count hard limit但会有 memory/storage pressure。需要用真实 workflow 形状验证。
3. **离线/监管环境**：Temporal self-host 与 ADF + MSSQL provider 都可行。差异取决于团队是否已有 Temporal/Kubernetes 还是 SQL Server/Azure Functions tooling。
4. **多语言团队**：Temporal polyglot worker routing 更强；ADF 多语言支持存在，但单个 function app 通常单语言，跨语言协作需要额外 topology。
5. **版本治理成熟度**：ADF Orchestration Versioning 是新近增强能力；如果项目严重依赖它，应验证目标语言包、extension bundle、Functions plan 和 storage provider 组合。

## 可验证的后续问题

1. 目标 workload 的 action/sec、history size、activity duration、signal/update/event frequency 是多少？
2. 是否需要外部 caller 向运行中 workflow 发同步命令并拿结果？
3. worker 是否需要按硬件、语言、客户环境或安全域隔离？
4. workflow 是否会运行数周/月，并跨多个部署版本？
5. 是否必须支持生产批量 reset/replay test？
6. 成本模型是低频突发还是常态高吞吐？
7. 是否允许第三方 SaaS 控制面，或必须保持 Azure first-party resource？
8. 是否能接受 ADF provider 选择不可迁移？

## 信心评估

| 结论 | 信心 | 说明 |
| --- | --- | --- |
| 二者 replay/durable execution 能力同属一个机制层级 | 高 | Temporal 与 ADF 官方文档均明确 event history/replay。 |
| Temporal Task Queue routing 是 ADF 难以等价替代的差异 | 高 | Temporal Task Queue 是 worker routing primitive；ADF Task Hub 不是同一语义。 |
| Temporal Update 明显强于 ADF External Event | 高 | Update 是同步、有 validator/result 的 workflow message；External Event 是 one-way async。 |
| Temporal Activity heartbeat 是长副作用场景关键差异 | 高 | Temporal docs 明确 heartbeat/details/cancellation；ADF 未发现等价一等 primitive。 |
| ADF Orchestration Versioning 已缩小版本能力差距 | 中高 | 官方文档已描述；具体语言/包/provider 组合需正式复核。 |
| Durable Task Scheduler 改变 ADF 吞吐和运维画像 | 中高 | 官方文档描述推荐后端和 CU/action billing；真实吞吐需 workload 压测。 |
| ADF 更适合 Azure-native low-ops/serverless 场景 | 高 | Azure Functions / DTS / Managed Identity / Application Insights / Consumption 模型直接支持。 |
| Temporal 更适合跨云/polyglot/deep workflow platform | 高 | Worker/Task Queue/Cloud/self-host/SDK/CLI 能力支撑。 |

## Footnotes

[^temporal-replay]: `https://docs.temporal.io/workflows#how-workflow-replay-works`; `https://docs.temporal.io/workflow-definition#workflow-versioning`.
[^temporal-workers]: `https://docs.temporal.io/workers`.
[^temporal-taskqueue]: `https://docs.temporal.io/task-queue`.
[^temporal-taskrouting]: `https://docs.temporal.io/task-routing`.
[^temporal-messages]: `https://docs.temporal.io/sending-messages`; `https://docs.temporal.io/handling-messages`.
[^temporal-heartbeat]: `https://docs.temporal.io/encyclopedia/detecting-activity-failures#activity-heartbeat`.
[^temporal-retry]: `https://docs.temporal.io/encyclopedia/retry-policies`; `https://docs.temporal.io/activity-definition#idempotency`.
[^temporal-versioning]: `https://docs.temporal.io/worker-versioning`; `https://docs.temporal.io/develop/go/workflows/versioning`.
[^temporal-replay-testing]: `https://docs.temporal.io/workflow-execution#replay`; `https://docs.temporal.io/develop/go/workflows/versioning`.
[^temporal-cli]: `https://docs.temporal.io/cli/command-reference/workflow`.
[^temporal-reset]: `https://docs.temporal.io/workflow-execution/event#reset`.
[^temporal-cloud-pricing]: `https://docs.temporal.io/cloud/pricing`; `https://docs.temporal.io/cloud/actions`.
[^temporal-cloud-security]: `https://docs.temporal.io/cloud/security`.
[^temporal-cloud-regions]: `https://docs.temporal.io/cloud/regions`.

[^adf-overview]: `https://learn.microsoft.com/en-us/azure/durable-task/durable-functions/durable-functions-overview`.
[^adf-orchestrations]: `https://learn.microsoft.com/en-us/azure/durable-task/common/durable-task-orchestrations`.
[^adf-storage-providers]: `https://learn.microsoft.com/en-us/azure/durable-task/common/durable-task-storage-providers`.
[^adf-scheduler]: `https://learn.microsoft.com/en-us/azure/durable-task/scheduler/durable-task-scheduler`.
[^adf-scheduler-billing]: `https://learn.microsoft.com/en-us/azure/durable-task/scheduler/durable-task-scheduler-billing`.
[^adf-scheduler-identity]: `https://learn.microsoft.com/en-us/azure/durable-task/scheduler/durable-task-scheduler-identity`.
[^adf-private-endpoint]: `https://learn.microsoft.com/en-us/azure/durable-task/scheduler/durable-task-scheduler-private-endpoints`.
[^adf-billing]: `https://learn.microsoft.com/en-us/azure/durable-task/durable-functions/durable-functions-billing`.
[^adf-functions-scale]: `https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale`; `https://learn.microsoft.com/en-us/azure/azure-functions/flex-consumption-plan`.
[^adf-entities]: `https://learn.microsoft.com/en-us/azure/durable-task/common/durable-task-entities`.
[^adf-external-events]: `https://learn.microsoft.com/en-us/azure/durable-task/common/durable-task-external-events`.
[^adf-versioning]: `https://learn.microsoft.com/en-us/azure/durable-task/durable-functions/durable-functions-versioning`.
[^adf-orchestration-versioning]: `https://learn.microsoft.com/en-us/azure/durable-task/common/durable-orchestration-versioning`.
[^adf-http-api]: `https://learn.microsoft.com/en-us/azure/durable-task/durable-functions/durable-functions-http-api`.
[^adf-instance-management]: `https://learn.microsoft.com/en-us/azure/durable-task/common/durable-task-instance-management`.
[^adf-diagnostics]: `https://learn.microsoft.com/en-us/azure/durable-task/durable-functions/durable-functions-diagnostics`.
