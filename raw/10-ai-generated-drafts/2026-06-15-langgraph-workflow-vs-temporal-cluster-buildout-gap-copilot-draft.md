---
source_type: ai-generated-draft
title: "Copilot research report: LangGraph Workflow gaps versus Temporal for physical Cluster Buildout"
origin: "GitHub Copilot CLI research output synthesized from focused research subagents and adversarial review"
generator: "GitHub Copilot CLI"
recorded: 2026-06-15
language: zh-Hans
topic: "Workflow platform selection"
authority: "non-authoritative"
raw_admission_reason: "User requested a new research draft comparing what LangGraph Workflow lacks versus Temporal in the selected physical/bare-metal Cluster Buildout scenario."
preservation_mode: ai-research-report
full_text_preserved: true
cleanup_note: "Generated as raw gap-analysis research only; primary-source claims must be rechecked before wiki synthesis or product decision."
---

> [!WARNING] 非权威 AI 调研草稿
> 本文件是 GitHub Copilot CLI 生成的调研草稿。它用于后续 `wiki/` 整合和选型讨论，不是权威技术事实来源，也不是最终架构结论。复用其中任何产品能力、缺口判断、版本状态或外部链接前，必须回到一手文档、源码或已有 wiki source page 重新核验，并在 `wiki/` 中建立明确的 claim-to-evidence 映射。

# LangGraph Workflow 在裸金属 Cluster Buildout 场景下相对 Temporal 缺少什么

## 调研边界

本报告只讨论用户选定场景：**物理机/裸金属机器集群的 Cluster Buildout**，范围包括物理节点、机架/网络、固件/OS/驱动、物理集群资源管理/作业调度器、基础服务和整体验证。它不是 Kubernetes cluster provisioning、Crossplane/GitOps/Helm/Kustomize，也不是应用部署流水线。[^scenario]

场景要求可压缩为五点：

1. 从面向裸金属集群建设的 Blueprint 启动。
2. 步骤执行者混合：确定性机器代码、确定性流程 AI Agent、AI 驱动人类通知/询问/跟进。
3. 通过早期验证的组件可能在后续集成验证中局部失败；未受影响部分继续，受影响部分等待修复并追赶。
4. 初始流程只是大概设计，运行中仍需调整。
5. 需要整体进度 UI，但可自研适配。[^scenario]

本报告的问题不是“LangGraph 能不能做 workflow”。LangGraph 有 StateGraph、checkpointer、store、interrupt、time travel、node retry/timeout/error handler、Agent Server 等能力。正确问题是：**在这个长期、外部副作用重、部分失败分叉、需要运行中事件与追赶的裸金属 Buildout 场景下，LangGraph Workflow 相对 Temporal 缺少哪些运行时原语，需要团队自己补？**

## 执行摘要

LangGraph 不应被描述为“没有 durability”或“只是 agent library”。它有 thread-scoped checkpoint、persistent store、interrupt/resume、time travel/fork、node-level retry/timeout/error handler，以及 Agent Server 的 run-level queue worker / persistence / deployment 能力。对于复杂 LLM tool graph、agent state、prompt/tool tracing、checkpoint fork 和 interrupt-style HITL，它比 Temporal 更贴近 AI agent 的实现体验。[^langgraph-persistence][^langgraph-interrupts][^langgraph-fault-tolerance][^langgraph-agent-server]

但在裸金属 Cluster Buildout 这个场景，Temporal 仍是更强的默认 process manager。原因不是 Temporal “更像 workflow”这个术语，而是它提供了 LangGraph 缺少或需要应用层重建的一组流程运行时原语：**Activity + Task Queue 的工作放置路由、Signal/Query/Update 的运行中对象交互、durable timer、Child Workflow 的独立生命周期、Activity heartbeat/checkpoint、Continue-As-New / Reset / Worker Versioning / Search Attributes**。这些能力正好对应裸金属 buildout 的长等待、特定机器执行、局部失败隔离、人工/供应商事件注入、运行中计划调整和生产事故恢复。[^temporal-activities][^temporal-taskqueue][^temporal-messages][^temporal-child-workflows][^temporal-heartbeat]

更正后的推荐框架应是：**Temporal-only 是基线架构；LangGraph 只是某些 AI Activity 的可选实现细节**。AI 诊断、规划、人类通知、审批和追问并不必然需要 LangGraph；它们可以直接用 Temporal Workflow + Activity + Signal/Update 实现，其中 LLM/外部 AI 调用放在 Activity 中，结果由 Temporal 记录并由确定性 workflow 状态机消费。只有当团队确实需要 LangGraph 的 agent graph authoring、interrupt 风格、checkpoint fork、LangSmith/Studio tracing 或 LangChain 生态时，才应把 LangGraph 嵌入某些 Temporal Activity。

## 能力对照总表

| 场景需求 | Temporal | LangGraph | 判断 |
| --- | --- | --- | --- |
| 多周/月长期运行 | Workflow Execution + Event History replay | Checkpointer + thread state | 两者都能做，但恢复模型不同。 |
| 外部物理副作用隔离 | Activity，结果写入 Event History，replay 不重跑已完成 Activity | Node / `@task`，checkpoint 保存 task 结果，普通节点需幂等 | LangGraph 可做但纪律更多靠应用层。 |
| 固件/BMC/PXE 操作必须跑在特定机器 | Task Queue / Worker pool routing | Agent Server 主要是 run-level queue；无公开 per-node placement primitive | Temporal 明显更强。 |
| 外部异步事件注入正在运行对象 | Signal / Update / Query | interrupt/resume、get_state/update_state；缺少 Temporal-style durable Signal/Update handler | Temporal 更强。 |
| 人工审批/HITL | Signal/Update + Activity 通知 | `interrupt()` 是一等能力，体验好 | Temporal 已足够；LangGraph 只是 authoring 体验优势。 |
| 内部持久 timer | Workflow timer / sleep 写入 Event History | 无同等内部 durable timer；需外部 scheduler + resume | Temporal 更强。 |
| 局部失败：未受影响部分继续，受影响部分追赶 | Child Workflow per rack/node/component，独立 history/lifecycle | 多 thread + Store + 外部协调可实现；无父子生命周期原语 | Temporal 更贴合。 |
| 长 activity 进度 checkpoint | Activity heartbeat details，worker crash 后 retry 可读取 | TimeoutPolicy idle heartbeat 重置进度时钟；不是服务端持久 checkpoint | Temporal 更强。 |
| 运行中计划调整 | Signal/Update + workflow 状态机 + versioning | interrupt + Command(resume) / update_state；非等待中图难以注入 | 两者都可做，Temporal 更适合全局控制面事件。 |
| 版本演进 | GetVersion/Patching + Worker Versioning | Graph migrations 有限制；pending/interrupted thread 不能随意改拓扑 | Temporal 更成熟。 |
| Debug / 回溯 | Reset to Event History point、replay testing、CLI | Time travel / fork checkpoints 很强，但外部副作用需谨慎 | 两者都有；语义不同。 |
| 自定义 UI | Search Attributes + Visibility + Queries | get_state/history + LangSmith Studio | 都需要自定义 cluster UI。 |

## 关键差异 1：恢复模型不是同一种 durability

Temporal 的状态真源是 Workflow Execution 的 Event History。Worker 崩溃或重启后，Temporal 重新执行 workflow code，并用 Event History 注入已完成 Activity、Timer、Signal 等结果，恢复 replay-safe 局部状态和控制点。已完成 Activity 不会因为 replay 被重新执行。[^temporal-replay][^temporal-activities]

LangGraph 的状态真源是 checkpointer 保存的 thread-scoped graph state checkpoint。它通常在 super-step 边界保存 `StateSnapshot`，恢复时从 checkpoint 的 state 继续图执行。`@task` 可缓存任务结果，pending writes 可避免同一 super-step 中已成功节点重复，但普通 node / interrupt 前代码仍可能在 resume 或 replay 时从节点开头重新执行。[^langgraph-persistence][^langgraph-interrupts][^langgraph-functional-api]

这不是“LangGraph 不 durable”，而是 durability 类型不同：

- Temporal 适合把外部副作用封进 Activity，并由 Event History 保证 replay 不重复已经完成的 Activity。
- LangGraph 适合把 agent graph 的状态检查点保存下来，并通过幂等 node / `@task` / external state 管理重复执行风险。

对裸金属场景的影响：固件刷写、BIOS 设置、PXE 安装、驱动安装、Slurm partition 配置这类操作一旦重复执行可能有物理风险。Temporal 的 Activity 边界更适合做“已完成结果不重跑”的流程壳；LangGraph 需要每个 node 更严格地实现 check-before-act、外部 idempotency key 和状态读回。

## 关键差异 2：LangGraph 缺少 Temporal Task Queue 式 per-work placement

裸金属 Cluster Buildout 的很多步骤不是“任意 worker 都能跑”：

- BMC/IPMI/Redfish 命令可能只有管理网段里的机器能发。
- PXE/iPXE/镜像服务只能由特定 provisioning 网络中的 worker 操作。
- 某些驱动/firmware 工具只能在目标节点或 rack-local jump host 上运行。
- 网络验证可能必须从特定 fabric / VLAN / switch 侧执行。
- AI Agent、人类通知、硬件控制、OS 安装可能需要不同安全域和凭据。

Temporal 的 Task Queue 是一等 worker routing primitive。Workflow 可以把不同 Activity 指派到不同 Task Queue，worker pool 通过 long-poll 拉取自己能执行的任务。对 buildout，可自然建模为 `bmc-workers`、`imaging-workers`、`network-validation-workers`、`human-loop-workers`、`ai-agent-workers`、`rack-05-local-workers`。[^temporal-taskqueue][^temporal-taskrouting]

LangGraph Agent Server 有 queue workers 和 run-level 分发；distributed runtime 还可分离 orchestration / execution process。但现有公开证据不支持把每个 graph node 当成 Temporal Activity 那样的一等 per-node placement unit。也就是说，LangGraph 可以把不同 run 分配到不同 worker，但没有公开的“这个 node 必须发到这个 worker pool / 这台机器”的稳定语义。[^langgraph-agent-server][^wiki-workflow-comparison]

团队若用 LangGraph 直接做 buildout，需要自行实现：

1. 远程执行 agent / daemon 部署到每个管理域或目标节点。
2. 节点代码里调用这些 agent 的 API。
3. 自己维护任务路由、排队、worker 健康、超时、重试、权限和审计。

这等于把 Temporal Task Queue / Activity dispatch 的一大块平台能力移到应用层。

## 关键差异 3：运行中对象交互，Temporal 的 Signal/Query/Update 更适合 Buildout 控制面

Buildout 运行中会不断收到外部事件：

- 人类批准、拒绝、补充信息。
- 供应商回复或现场人员确认。
- BMC / provisioning / scheduler / monitoring 系统回调。
- 后续集成验证发现某个已通过组件局部失效。
- 操作员决定临时加入新验证步骤或改 Blueprint 参数。

Temporal 对运行中 workflow 提供三类消息：

- Signal：异步、持久、fire-and-forget，适合外部事件通知。
- Query：同步只读，不写 Event History，适合 UI 查询当前内部状态。
- Update：同步、可验证、可返回结果，接受后写 Event History，适合“请求运行中 workflow 修改状态并得到确认”。[^temporal-messages]

LangGraph 的交互中心是 `interrupt()` / `Command(resume=...)`，它非常适合 HITL：图主动暂停，暴露问题，等待人类/系统恢复。`get_state()` 和 `get_state_history()` 可读 checkpoint；`update_state()` 可修改 checkpoint / fork 状态。[^langgraph-interrupts][^langgraph-time-travel]

缺口在于：LangGraph 没有 Temporal-style “向正在运行且未 interrupt 的 graph 注入 durable Signal / Update handler”的一等语义。若 graph 没有提前停在 interrupt 点，外部事件通常需要通过外部 DB、polling、另一个 run、手工 resume 或应用层消息队列接入。

这对 buildout 很关键，因为很多事件不是流程主动提问后才发生，而是在物理世界任意时间发生。Temporal 把这些事件建模为 running Workflow Execution 的消息；LangGraph 更自然地把它们建模为外部状态变化或 interrupt resume。

## 关键差异 4：LangGraph 缺少内部 durable timer 原语

Buildout 充满内部持久等待：

- 刷固件后等待 BMC 重启 10 分钟。
- OS install 后等待节点第一次上报 30 分钟。
- 网络变更后延迟验证。
- 人工审批超时后升级通知。
- 每隔一段时间轮询供应商/现场任务状态。

Temporal timer / sleep 是 workflow 内部持久原语：timer 写入 Event History，不占 Activity worker；worker 重启后由 Temporal Service 继续管理。[^temporal-timers]

LangGraph 有 interrupt、cron jobs、timeout policy 和外部 Agent Server run scheduling，但它们不是同一语义：

- Cron job 是按时间创建/触发 run，不是在一个 run 内部等待并自动继续。
- TimeoutPolicy 是检测 node 执行超时，不是“睡眠到某个时间继续”。
- interrupt 可以暂停等待，但需要外部可靠 scheduler 在 N 分钟后调用 resume。

所以这不是完全不能做，而是需要额外外部定时器服务，并处理 resume idempotency、丢失触发、重复触发和审计。

## 关键差异 5：局部失败 fork/split 是 LangGraph 的高工程量区

用户场景最核心的一点是：已经通过验证的组件可能在后续集成验证中局部失败；这不是全面失败。未受影响部分应继续，受影响部分等待修复后追赶。[^scenario]

Temporal 的自然建模是：

```text
ClusterBuildWorkflow
  ├─ RackBuildWorkflow(rack-01)
  │   ├─ NodeBuildWorkflow(node-001)
  │   └─ NodeBuildWorkflow(node-002)
  ├─ RackBuildWorkflow(rack-02)
  └─ ClusterValidationWorkflow
```

每个 rack/node/component 都可以是 Child Workflow，拥有独立 Workflow ID、Event History、Signal/Query/Update、retry、timer 和生命周期。局部失败只会阻塞相关 Child；未受影响 Child 继续。父 workflow 可通过 Parent Close Policy、Signals、Search Attributes、Queries 等协调整体状态。[^temporal-child-workflows][^temporal-search-attributes]

LangGraph 可用三种方式近似：

1. 一个 thread 内用并行分支 / `Send` fan-out。问题是共享 state 和 super-step checkpoint 使局部失败隔离较难；失败分支和成功分支的追赶逻辑要谨慎设计。
2. 每个 rack/node/component 创建独立 thread / Agent Server run。问题是父子生命周期、等待子完成、取消传播、追赶、状态聚合都需要应用层实现。
3. 用 subgraph + 独立 checkpointer。问题是 subgraph 更多是图结构复用/嵌套，不等价于独立 Child Workflow execution。

结论：LangGraph 可以做，但这里的工程量很高，而且实现出来更像“在 LangGraph 周围自建一个 resource workflow control plane”。Temporal 的 Child Workflow 模型更直接贴合“资源实体长期生命周期”。

## 关键差异 6：长 Activity heartbeat / worker crash 接管

Temporal Activity heartbeat 可以把进度 payload 发送给 Temporal Service。若 activity 因 worker crash 或 heartbeat timeout 重试，下一次 attempt 可以读取 heartbeat details，从上次进度继续。Activity 还有 Schedule-To-Start、Start-To-Close、Schedule-To-Close、Heartbeat Timeout 等独立超时语义。[^temporal-heartbeat]

LangGraph node-level fault tolerance 已经比早期印象强很多：RetryPolicy、TimeoutPolicy、idle timeout、`runtime.heartbeat()`、error_handler 都能表达 retry、退避、超时和补偿。[^langgraph-fault-tolerance]

但差异仍在：

- LangGraph heartbeat 更像 node runtime 的 idle timeout 续约，不是服务端持久的 progress checkpoint。
- worker crash 后，LangGraph 通常从 checkpoint / node 重新执行；想从中间步骤续跑，需要 node 自己把 progress 写外部 store。
- Temporal heartbeat details 是 Activity 语义的一部分，更适合长固件刷写、OS 镜像、烧机测试、数据迁移这类可分段副作用。

因此，LangGraph 在 retry/timeout 维度不是“缺失”，但在长物理副作用的 crash recovery 维度弱于 Temporal。

## 关键差异 7：版本演进与运行中拓扑调整

用户场景要求“初始流程只是大概设计，运行中仍需调整”。这需要分成两类：

1. **调整 state / 参数 / 下一步策略**：例如把某些节点加入额外验证，改变重试策略，等待人工确认后走新分支。
2. **调整 workflow topology / code path**：例如新增/删除/重命名将要执行的步骤，改变长期运行实例的执行代码。

Temporal 通过 Signal/Update 改 state，通过 deterministic workflow code 决策后续路径；通过 `GetVersion` / patching 和 Worker Versioning 处理 replay-safe code evolution；必要时用 Continue-As-New 作为 run 边界切换状态和代码版本。[^temporal-versioning][^temporal-continue-as-new]

LangGraph 可通过 interrupt + resume、`update_state()`、time travel/fork 修改 state 或从 checkpoint 分叉。Graph migrations 支持一定程度的图演进，但对 interrupted/pending thread 有限制：不能随意 rename/remove 可能即将进入的 node。[^langgraph-time-travel][^langgraph-migrations]

所以：

- 如果“运行中调整”主要是向状态里写新指令/新参数，LangGraph 做得不错。
- 如果“运行中调整”意味着长期在途 thread 要安全穿过 graph topology / node name / code path 变更，Temporal 的版本工具更成熟。

## LangGraph 的条件性价值

为了避免过度贬低 LangGraph，也要避免把它写成必要层。它在本场景中的价值主要是 **AI 节点实现体验**，不是 Temporal 缺失的流程能力：

1. **复杂 LLM agent graph 的 authoring 更自然**：StateGraph / agent node / tool calls / conditional routing 更适合表达多步 LLM 决策链。
2. **interrupt-style HITL 更贴近 agent 对话体验**：`interrupt()` 把“图暂停、暴露问题、等待补充输入”作为一等控制流；但审批、通知、追问本身也可用 Temporal Signal/Update + Activity 实现。
3. **Time travel / fork 适合 AI 分析与调试**：可从 checkpoint fork 新分支探索不同 prompt、tool result 或决策，不覆盖原始历史。
4. **Checkpoint state 更贴近 agent 状态**：对 messages、memory、tool results 的保存与恢复比在普通 workflow state 中手写结构更方便。
5. **LangSmith/Studio 生态**：对 agent tracing、prompt/tool 调试、人工介入有现成产品面。

因此，LangGraph 不是“不可用”，但也不是裸金属 Buildout 的必选层。更准确的定位是：**如果某个 Temporal Activity 内部确实需要复杂 agent graph、agent memory、prompt/tool tracing 或 checkpoint fork，LangGraph 可以作为该 Activity 的实现库；否则 Temporal-only 足以覆盖流程、AI 调用和 HITL。**

## 推荐架构

### 基线：Temporal-only

```text
Temporal ClusterBuildWorkflow
  ├─ ParseBlueprintActivity
  ├─ RackBuildWorkflow(rack-01)
  │   ├─ NodeBuildWorkflow(node-001)
  │   │   ├─ Temporal Activity: FlashFirmware
  │   │   ├─ Temporal Activity: InstallOS
  │   │   ├─ Temporal Activity: RunAIDiagnosisOrPlanner
  │   │   └─ Temporal Update: InjectAdditionalValidationStep
  │   └─ NodeBuildWorkflow(node-002)
  ├─ HumanApprovalWorkflow
  │   ├─ Temporal Activity: NotifyOrAskHuman
  │   └─ Temporal Signal/Update: ReceiveHumanDecision
  └─ ClusterValidationWorkflow
```

在基线架构中：

- Temporal 负责长期流程、Task Queue 路由、resource entity child workflow、timer、external messages、human decision、reset、versioning。
- LLM/外部 AI 调用是普通 Temporal Activity；Activity 返回候选诊断、计划建议或待确认问题，Temporal workflow 只消费结果并推进确定性状态机。
- 外部 inventory/resource graph 仍是物理事实真源；Temporal 和 LangGraph 都不能替代它。
- LangGraph 只在 `RunAIDiagnosisOrPlanner` 这类 Activity 内部需要复杂 agent graph / checkpoint fork / LangSmith tracing 时才引入；它不拥有最终流程状态、审批结果、计划版本、事件注入或物理副作用控制权。

### 如果坚持 LangGraph 作为主控，需要补的系统

1. 可靠外部 timer/scheduler：负责 run 内延迟后 resume。
2. per-resource execution agents：部署到管理网、rack-local host、目标节点或具备硬件访问权限的机器。
3. 应用级 routing layer：把 graph node 的执行请求发到正确 agent。
4. resource lock / lease / idempotency key：避免同一节点被多个 thread 并发操作。
5. child-thread coordinator：管理每个 rack/node/component thread 的父子关系、等待、取消、追赶。
6. durable event inbox：接收来自 BMC、PXE、供应商、人类、监控系统的异步事件并路由到正确 thread。
7. version migration discipline：管理 interrupted/pending thread 的 topology 迁移。
8. progress UI：聚合 checkpointer / store / external inventory / agent status。

这并非不可做，但工程量接近围绕 LangGraph 自建一层 Temporal-like process runtime。

## 结论

在裸金属 Cluster Buildout 场景下，LangGraph 相对 Temporal 缺少的不是“AI workflow 表达能力”，而是“长期物理流程控制面”的一组基础原语：

1. Task Queue 式 per-worker/per-machine 工作放置。
2. Signal/Query/Update 式运行中对象交互。
3. workflow 内部 durable timer。
4. Child Workflow 独立生命周期与父子协调。
5. Activity heartbeat details 与 crash 后续跑。
6. Continue-As-New / Reset / Worker Versioning 等长运行生产运维工具。
7. Search Attributes / Visibility / Task Queue worker health 等 workflow platform 可观测性。

因此，**如果目标是可靠地驱动物理节点、机架、网络、固件、OS、驱动和集成验证的长期 buildout process，Temporal 应作为默认且充分的主 process manager。LangGraph 不应作为默认推荐；只有当复杂 LLM agent graph、agent memory、interrupt-style 对话、checkpoint fork 或 LangSmith/Studio tracing 能显著降低 AI Activity 的实现成本时，才作为 Temporal Activity 内部的可选实现库引入。**

## 信心评估

| 结论 | 信心 | 说明 |
| --- | --- | --- |
| LangGraph 有 checkpoint、interrupt、time travel、retry/timeout，不能说无 durability | 高 | LangGraph docs 和既有 wiki source pages 均支持。 |
| LangGraph 与 Temporal 的恢复模型本质不同：checkpoint resume vs Event History replay | 高 | 既有 wiki 已有 durable conclusion。 |
| Task Queue / per-machine placement 是本场景最关键差距之一 | 高 | 裸金属任务强依赖网络/机器/凭据放置；Temporal 原语直接支持。 |
| LangGraph 缺少 Temporal-style non-blocking Signal/Update | 中高 | 当前证据显示主要交互是 interrupt/resume、state API、external store；需正式复核最新 Agent Server API。 |
| LangGraph 无 workflow-internal durable timer | 中高 | Cron/timeout/interrupt 可组合模拟，但不是等价原语。 |
| LangGraph partial failure fork/split 可实现但工程量高 | 高 | 多 thread + Store + coordinator 可行，但缺少 Child Workflow 生命周期语义。 |
| Temporal 仍需外部 resource graph、idempotent Activities、reconcile/compensation | 高 | Temporal 不回滚物理世界，这是必须保留的边界。 |
| Temporal-only 足以覆盖本场景的 AI 调用和 HITL 基线需求；LangGraph 只是条件性 AI Activity 实现层 | 高 | AI 调用可放在 Temporal Activity，审批/追问可由 Signal/Update + Activity 通知实现；LangGraph 的差异主要是 agent authoring/debugging 体验。 |

## Footnotes

[^scenario]: `raw/00-human-original-input/2026-06-12-cluster-buildout-platform-selection-request.md:18-31`.
[^wiki-workflow-comparison]: `wiki/analyses/workflow-concepts-comparison.md:67-77,94-116,118-143`.

[^langgraph-persistence]: `https://docs.langchain.com/oss/python/langgraph/checkpointers`; repository source projection: `wiki/sources/langgraph/persistence-docs.md:25-35`.
[^langgraph-interrupts]: `https://docs.langchain.com/oss/python/langgraph/interrupts`; repository source projection: `wiki/sources/langgraph/interrupts-docs.md:25-34`.
[^langgraph-fault-tolerance]: `https://docs.langchain.com/oss/python/langgraph/fault-tolerance`; repository source projection: `wiki/sources/langgraph/fault-tolerance-docs.md:26-36`.
[^langgraph-agent-server]: `https://docs.langchain.com/langsmith/agent-server`; repository source projection: `wiki/sources/langgraph/agent-server-docs.md:28-47`.
[^langgraph-time-travel]: `https://docs.langchain.com/oss/python/langgraph/use-time-travel`.
[^langgraph-functional-api]: `https://docs.langchain.com/oss/python/langgraph/functional-api`.
[^langgraph-migrations]: `wiki/sources/langgraph/graph-migrations-docs.md:27-31`.

[^temporal-replay]: `https://docs.temporal.io/workflows#how-workflow-replay-works`; repository source projection: `wiki/sources/temporal/workflows-docs.md:26-50`.
[^temporal-activities]: `https://docs.temporal.io/activities`; repository source projection: `wiki/sources/temporal/activities-docs.md:26-36`.
[^temporal-taskqueue]: `https://docs.temporal.io/task-queue`.
[^temporal-taskrouting]: `https://docs.temporal.io/task-routing`.
[^temporal-messages]: `https://docs.temporal.io/sending-messages`; repository source projection: `wiki/sources/temporal/message-passing-docs.md:25-53`.
[^temporal-child-workflows]: `https://docs.temporal.io/child-workflows`.
[^temporal-timers]: `https://docs.temporal.io/workflows`; repository source projection: `wiki/sources/temporal/timers-delays-docs.md:27-40`.
[^temporal-heartbeat]: `https://docs.temporal.io/encyclopedia/detecting-activity-failures#activity-heartbeat`.
[^temporal-continue-as-new]: `https://docs.temporal.io/workflow-execution/continue-as-new`; repository source projection: `wiki/sources/temporal/continue-as-new-docs.md:26-43`.
[^temporal-versioning]: `https://docs.temporal.io/worker-versioning`; repository source projection: `wiki/sources/temporal/worker-versioning-docs.md:26-38`.
[^temporal-search-attributes]: `https://docs.temporal.io/search-attribute`.
