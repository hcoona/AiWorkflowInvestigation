---
source_type: ai-generated-draft
title: "ChatGPT draft: Cluster Buildout platform selection"
origin: "User-provided ChatGPT conversation export; assistant response portion"
generator: "ChatGPT"
recorded: 2026-06-12
language: zh-Hans
topic: "AI workflow platform selection"
authority: "non-authoritative"
raw_admission_reason: "User requested preserving the AI-generated draft separately with an explicit warning that it must not be directly adopted."
preservation_mode: sanitized-ai-draft
full_text_preserved: false
cleanup_note: "Split from the original transcript; generalized the scenario and project name to Cluster Buildout."
---

> [!WARNING] 非权威 AI 初稿
> 本文件是 ChatGPT 生成的、未经系统性批评和补证的初稿。不要直接把其中的产品能力、平台比较、选型结论或外部链接作为 wiki 结论证据；如需复用，必须重新核验一手来源，并在 `wiki/` 中建立明确的 claim-to-evidence 映射。

# AI 初稿：Cluster Buildout 平台选型

我会按“平台选型结论 → 关键能力对照 → 映射到 Cluster Buildout 场景 → 推荐架构”的顺序展开；同时核对一下 Temporal / Airflow 当前官方能力，避免把旧印象当成事实。

先把结论提前说：这个场景更像“长生命周期、有状态、事件驱动的 buildout process manager”，不是传统 batch DAG。Airflow 可以跑，但会逼你把很多核心语义搬到外部状态机里。

## 结论

针对你描述的 **Cluster Buildout**，我会选 **Temporal 作为核心 orchestration runtime**，而不是 Apache Airflow。

原因不是“Temporal 更现代”，而是你的问题本质上不是一个定时批处理 DAG，而是一个 **长期运行、可被事件打断、可被人和 AI Agent 修改、可局部回滚/分叉/追赶的 buildout state machine**。Airflow 官方也明确把自己定位为 **finite, batch-oriented workflows**，并说明它不适合 continuously running、event-driven 或 streaming workload。这个边界和你这个场景的核心需求是冲突的。[![](https://www.google.com/s2/favicons?domain=https://airflow.apache.org&sz=128)Apache Airflow](https://airflow.apache.org/docs/apache-airflow/stable/index.html)

我的推荐是：

> **Temporal 管控制平面；Blueprint / Run Graph / UI Projection 自己建模；Airflow 最多作为某些批量验证、报表或已有 DAG 的执行子系统，不应作为主 workflow brain。**

---

## 一句话对比

| 维度 | Temporal | Airflow |
| --- | --- | --- |
| 核心模型 | Durable workflow / long-running process | Scheduled / manually triggered finite DAG run |
| 最适合 | 有状态业务流程、human-in-loop、外部事件、失败恢复、长生命周期任务 | 数据管道、批处理、定时任务、静态或半动态 DAG |
| AI Agent 适配 | 更自然：Agent 调用、工具调用、人类审批都可建成 workflow/event | 可以跑 Agent task，但 Agent 改流程、等待人、局部修复都要外部状态机 |
| 运行中改图 | 适合做“data-driven run graph + signals/updates”，但 workflow 代码要 deterministic | 动态 task mapping 可以运行时扩展数量，但不适合任意 run-time DAG mutation |
| 局部失败/回溯 | 可以用 child workflow / component workflow 建模局部状态和修复分支 | 可以通过 trigger rules、branching、clear/retry 绕，但语义会变重 |
| UI | Temporal UI 偏执行历史和调试；业务图通常要自建 | Airflow DAG/Grid UI 开箱更成熟 |
| 我的判断 | 主 orchestrator | 辅助系统或不推荐作为主系统 |

---

## 为什么这个场景更偏 Temporal

你描述的流程有几个关键特征：

1. Blueprint 先启动，但只是初始计划。
2. 节点类型混合：确定性代码执行、确定性 AI Agent 执行、AI drive human 执行。
3. 组件先通过、后续集成验证又部分失败，需要局部分叉或回溯。
4. 流程设计在运行过程中会继续调整。
5. UI 重要，但不是平台选择的第一优先级。

这些需求更接近 **durable process manager**，而不是传统 DAG scheduler。

Temporal 的 Workflow 可以通过 Signals、Updates、Queries 与外部系统交互：Signals 适合异步事件，Updates 适合同步修改 workflow 状态并拿到结果，Queries 适合读取 workflow 状态。这个模型很适合 human-in-loop、Agent 提交 patch、外部验证结果回写等场景。[![](https://www.google.com/s2/favicons?domain=https://docs.temporal.io&sz=128)Temporal 文档](https://docs.temporal.io/sending-messages)

Temporal 还支持 Child Workflow；官方文档明确说 child workflow 可以由 parent workflow spawn，也可以用来 partition large workloads，或者一对一表示一个 resource，例如每台 host 一个 workflow，用 workflow ID 保证串行化。这个点非常贴合 Cluster Buildout：cluster、rack、VMSS、head node、compute pool、network fabric、scheduler integration 都可以成为不同粒度的 workflow entity。[![](https://www.google.com/s2/favicons?domain=https://docs.temporal.io&sz=128)Temporal 文档](https://docs.temporal.io/child-workflows)

---

## Airflow 能不能做？

能做，但会别扭。

Airflow 的 DAG 表示 task dependency，task 可以是 fetch data、run analysis、trigger other systems，Airflow 本身也确实可以通过 operator、shell、Python 去编排各种外部动作。[![](https://www.google.com/s2/favicons?domain=https://airflow.apache.org&sz=128)Apache Airflow](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/overview.html) 但它的强项仍然是：一个 DAG Run 被创建，然后 DAG 内 task 依赖执行，最后根据 task terminal states 算出 DAG Run status。[![](https://www.google.com/s2/favicons?domain=https://airflow.apache.org&sz=128)Apache Airflow](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dag-run.html)

这和你的需求差异在于：你不是只需要“这个 run 成功/失败”，而是需要表达：

* Node A 的 provisioning 通过了，但 later integration 的 scheduler-binding 失败；
* Node A 的 networking aspect 需要 repair branch；
* Node B/C 不受影响，可以继续；
* Agent 发现 dependency 需要插入新验证节点；
* 人类 owner 需要确认某个变更；
* repair branch 追上后重新 join 主线。

Airflow 可以用 branching、trigger rules、dynamic task mapping、deferrable operators 拼出来一部分。Airflow dynamic task mapping 支持根据上游输出在运行时创建多个 task instance；deferrable operator 可以在等待外部事件时释放 worker slot。[![](https://www.google.com/s2/favicons?domain=https://airflow.apache.org&sz=128)Apache Airflow](https://airflow.apache.org/docs/apache-airflow/stable/authoring-and-scheduling/dynamic-task-mapping.html) [![](https://www.google.com/s2/favicons?domain=https://airflow.apache.org&sz=128)Apache Airflow](https://airflow.apache.org/docs/apache-airflow/stable/authoring-and-scheduling/deferring.html) 但这仍然不是“可演化 run graph”的一等模型。Airflow 的 dynamic DAG generation 文档还特别区分：动态生成 DAG 结构时，DAG 内 task 数量在 DAG Run 之间应保持一致；真正运行时数量变化要靠 dynamic task mapping。[![](https://www.google.com/s2/favicons?domain=https://airflow.apache.org&sz=128)Apache Airflow](https://airflow.apache.org/docs/apache-airflow/stable/howto/dynamic-dag-generation.html)

也就是说，Airflow 的 dynamic 能力主要解决 **fan-out 数量未知**，不是解决 **运行中由 Agent / human / validation result 重写业务流程图**。

---

## 对你五个需求逐项判断

### 1. “一开始有个 Blueprint 先开始跑”

两者都可以。

Airflow 的自然模型是把 Blueprint 编译成 DAG。这个在最初看起来很舒服，尤其 UI 会直接显示 DAG 结构。

Temporal 的自然模型是把 Blueprint 作为 input，启动一个 `ClusterBuildoutWorkflow`。Workflow 内部把 Blueprint materialize 成 run graph，并为关键资源启动 child workflows。这里需要你自己维护 run graph projection，但换来的是更强的运行时控制。

我的建议是：**Blueprint 不要等同于 workflow code，也不要等同于 Airflow DAG file。**  
更好的模型是：

```
Blueprint Template vN
        ↓
Buildout Run Graph
        ↓
Temporal Parent Workflow
        ↓
Component / Capability Child Workflows
```

Blueprint 是初始计划；Run Graph 是运行时事实；Temporal workflow 是执行与状态迁移引擎。

---

### 2. “节点有确定代码执行、AI Agent 执行、AI drive human 执行”

Temporal 更合适。

确定性代码执行，例如 cloud CLI、IaC 工具、脚本、telemetry 查询、health check，可以建成 Temporal Activity。Activity 负责和外部世界交互；workflow 负责决定何时调用、如何 retry、如何记录状态。Temporal 对 activity failure、timeout、retry policy、heartbeat 有明确模型。[![](https://www.google.com/s2/favicons?domain=https://docs.temporal.io&sz=128)Temporal 文档](https://docs.temporal.io/encyclopedia/detecting-activity-failures?utm_source=chatgpt.com)

AI Agent 执行也更适合放在 Activity 或 Child Workflow 里，而不是直接塞进 workflow deterministic code。Temporal 官方已有 OpenAI Agents SDK integration 示例，把 Temporal Activities 暴露为 agent tools，并让 agent execution 获得 durable execution 和 observability。[![](https://www.google.com/s2/favicons?domain=https://docs.temporal.io&sz=128)Temporal 文档](https://docs.temporal.io/ai-cookbook/openai-agents-sdk-python)

AI drive human 的部分，Temporal 的 Signals / Updates 很自然：

```
Agent proposes change
      ↓
Workflow creates human task
      ↓
Human approves / rejects / edits
      ↓
Signal or Update sent back to workflow
      ↓
Workflow continues
```

Airflow 也可以用 deferrable operator 等人，但一旦 human interaction 不只是“批准/拒绝”，而是会修改 plan、补充信息、触发局部 repair branch，Airflow task 本身就不再是合适的状态边界。

---

### 3. “已验证组件在后续集成验证中部分失败，需要分叉或回溯，不影响的部分继续”

这是最关键的分水岭。Temporal 明显更适合。

不要把节点状态建模成单个 `Succeeded / Failed`。应该建成 capability/aspect 维度的状态向量，例如：

```
Component: Compute Pool A

Provisioning:      Passed
Image Validation:  Passed
Network Reach:     Passed
Scheduler Join:    Failed
Perf Baseline:     Not Started
Compliance:        Passed
Owner Ack:         Pending
```

这样 later integration failure 不会把整个组件打回 failed，而是产生一个 scoped repair branch：

```
Compute Pool A
  ├─ unaffected aspects continue
  └─ Scheduler Join Repair Workflow
          ├─ diagnose
          ├─ patch config
          ├─ revalidate scheduler join
          └─ catch up / rejoin
```

Temporal 的 parent-child workflow、signals、event history 更适合表达这种局部状态迁移。Child Workflow 也可以在 parent 取消后按 Parent Close Policy 决定是否继续，适合做独立 repair track 或 resource-level execution。[![](https://www.google.com/s2/favicons?domain=https://docs.temporal.io&sz=128)Temporal 文档](https://docs.temporal.io/child-workflows)

Airflow 在这个场景会遇到两个问题：

第一，Airflow task instance 的状态更像一次执行记录，而不是一个长期存在的 resource state。你可以 clear task、retry task、trigger new DAG run，但“已成功组件后来部分 aspect 失效”不是 Airflow 的自然语义。

第二，Airflow DAG Run status 由 leaf nodes 的 terminal states 推导；官方文档还提醒，某些 trigger rule 可能导致中间失败但 leaf 成功，从而整个 DAG Run 仍然显示 success。这个模型对 buildout 的真实状态表达不够精确。[![](https://www.google.com/s2/favicons?domain=https://airflow.apache.org&sz=128)Apache Airflow](https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dag-run.html)

---

### 4. “一开始设计的流程只是大概设计，运行中还要继续调整”

Temporal 更适合，但要注意边界。

Temporal workflow code 必须 deterministic：replay 时，在相同输入下必须产生相同的 workflow API call sequence。[![](https://www.google.com/s2/favicons?domain=https://docs.temporal.io&sz=128)Temporal 文档](https://docs.temporal.io/workflow-definition) 这意味着你不能把“LLM 随机决定下一步”直接写进 workflow code。正确做法是：

```
Workflow deterministic shell
  ├─ call Agent Activity
  ├─ receive proposed GraphPatch
  ├─ validate patch deterministically
  ├─ maybe request human approval
  ├─ apply patch to Run Graph state
  └─ schedule next Activities / Child Workflows
```

也就是说，**AI 可以提出 patch，但 workflow runtime 负责审计、验证、应用 patch**。

这和你之前提到的“template graph vs run graph separation / Graph Patch Proposal / append-only audit log / checkpoint-resume-rollback-fork”是一致的。Temporal 不应该被当成 graph database 或 visual editor；它应该是 durable execution kernel。

Airflow 如果要支持运行中改图，通常会变成：

```
Airflow DAG task
  ↓
call external planner / state service
  ↓
external service decides next graph
  ↓
trigger another DAG run or mapped task set
```

这时 Airflow 实际上只是 worker scheduler，真正的 orchestration brain 已经在外部了。

---

### 5. “UI 有必要，但可以二次开发”

这点不能只看开箱 UI。

Airflow 的 UI 确实更像你想要的 DAG 进度视图。Graph View 可以显示 DAG 逻辑结构、branching、retry 配置和 run-specific task states。[![](https://www.google.com/s2/favicons?domain=https://airflow.apache.org&sz=128)Apache Airflow](https://airflow.apache.org/docs/apache-airflow/stable/ui.html) 如果你的流程是稳定 DAG，Airflow UI 很有吸引力。

Temporal 的 Web UI 更偏 workflow execution state、metadata、event history、pending activities、queries、search attributes 等调试和运维视角。[![](https://www.google.com/s2/favicons?domain=https://docs.temporal.io&sz=128)Temporal 文档](https://docs.temporal.io/web-ui) Temporal Visibility 也支持基于 Search Attributes 的 list/filter/search workflow executions。[![](https://www.google.com/s2/favicons?domain=https://docs.temporal.io&sz=128)Temporal 文档](https://docs.temporal.io/visibility) 但它不会天然给你一个“Blueprint run graph + repair branch + human task inbox + graph diff approval”的业务 UI。

不过你已经判断“没有 UI 的产品也能用，二次开发不困难”。在这个前提下，不应该为了 Airflow UI 牺牲核心执行语义。

我建议 UI 自己做：

```
Temporal Event History / Workflow Query / Search Attributes
        ↓
Run Graph Projection Service
        ↓
Postgres / document DB / analytical store
        ↓
React Flow / xyflow based UI
```

UI 展示的是你自己的 **Run Graph Projection**，不是直接展示 Temporal event history。Temporal 负责可靠执行，UI 负责业务可视化。

---

## 推荐架构

我会这样设计：

```
                 ┌──────────────────────┐
                 │ Blueprint Repository  │
                 │ versioned templates   │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ Buildout API          │
                 │ validate / start run  │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌────────────────────────────┐
                 │ Temporal Parent Workflow    │
                 │ ClusterBuildoutWorkflow     │
                 └──────────┬─────────────────┘
                            │
       ┌────────────────────┼────────────────────┐
       ▼                    ▼                    ▼
┌──────────────┐     ┌──────────────┐     ┌────────────────┐
│ Component WF │     │ Agent WF/Act │     │ Human Task Svc │
│ pool / node  │     │ planner/triage│     │ approval/input │
└──────┬───────┘     └──────┬───────┘     └───────┬────────┘
       │                    │                     │
       ▼                    ▼                     ▼
┌──────────────┐     ┌──────────────┐     ┌────────────────┐
│ Cloud Ops    │     │ Graph Patch  │     │ Signal/Update  │
│ CLI/API/etc. │     │ Proposal     │     │ back to WF     │
└──────────────┘     └──────────────┘     └────────────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ Run Graph Projection  │
                 │ status / audit / UI   │
                 └──────────────────────┘
```

关键设计点：

1. **Parent Workflow 管全局状态，不直接执行重活。**  
    它决定依赖、join condition、repair branch、approval gate。
2. **Component Workflow 管资源级生命周期。**  
    例如 compute pool、scheduler integration、network validation、storage mount、image rollout 都可以有自己的 workflow。
3. **Activity 只做外部副作用。**  
    cloud CLI、脚本、REST call、telemetry query、GitHub/Jira、notification、LLM call 都放 Activity。
4. **Agent 只提出计划，不直接改全局事实。**  
    Agent 输出 `GraphPatchProposal`，由 deterministic validator + policy + human approval 决定是否应用。
5. **状态不是单值，而是 capability vector。**  
    这样才支持“部分失败、局部回溯、不影响分支继续”。
6. **UI 读 projection，不直接读 workflow internals。**  
    Temporal event history 是审计和 debug source；业务 UI 应该读一个专门为展示优化的 run graph projection。

---

## Airflow 适合放在哪里

我不会完全排除 Airflow。它可以作为辅助系统：

1. **周期性验证任务**  
    例如 nightly cluster health sweep、quota check、capacity report、image drift detection。
2. **数据管道 / 报表**  
    例如从 logs、telemetry、resource inventory 抽取 buildout metrics，生成 dashboard 输入。
3. **已有 DAG 资产复用**  
    如果团队已有 Airflow DAG，比如标准化 validation suite，可以让 Temporal Activity 触发 Airflow DAG Run，然后等待结果。

但边界要清楚：

```
Temporal owns buildout state.
Airflow owns batch jobs.
```

不要让 Temporal 和 Airflow 同时拥有 buildout run 的主状态，否则会出现“双控制平面”：谁判断失败？谁决定重试？谁决定 rollback？谁决定 human approval 后继续？这些问题会变得非常难 debug。

---

## 最终选型建议

我的平台选型建议是：

> **选择 Temporal 作为 Cluster Buildout 的主 workflow runtime。**  
> **不要选择 Airflow 作为主 orchestrator，除非你把需求收缩成稳定 DAG + 有限批处理 + 少量人工 gate。**

更具体一点：

| 场景 | 推荐 |
| --- | --- |
| Blueprint 启动 buildout | Temporal Parent Workflow |
| pool / node / scheduler / network / storage 子流程 | Temporal Child Workflow |
| 确定性基础设施操作 | Temporal Activity |
| AI Agent 诊断 / 计划 / follow-up | Activity 或 Child Workflow |
| 人工审批 / 补充输入 | Human Task Service + Temporal Signal/Update |
| 局部 repair branch | 新 Child Workflow / branch state |
| 运行中改图 | GraphPatchProposal + deterministic validator |
| 业务 UI | 自建 Run Graph Projection UI |
| 周期性 batch validation / reporting | 可用 Airflow |

一句话总结：

**Airflow 是优秀的 DAG scheduler；Temporal 更像可靠的 distributed process runtime。你的 Cluster Buildout 需求需要后者。**
