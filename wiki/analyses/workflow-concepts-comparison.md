---
schema_version: 2
page_type: analysis
title: "工作流概念比较：Temporal、Apache Airflow、Microsoft Agent Framework 与 LangGraph"
status: active
created: 2026-06-12
updated: 2026-06-12
summary: "比较四个多步编排系统在控制抽象、状态/持久化和调度取向上的差异。"
maintenance:
  edit_policy: update
validation:
  body_contract: analysis-answer-memo
tags:
  - workflow
  - orchestration
  - durability
  - ai-agents
---

## 问题

本页边界不是比较品牌生态，也不是比较语言支持，而是比较四个系统作为多步、状态化工作编排底座时的控制抽象、执行单元、状态/持久化、动态适应能力，以及时间/调度取向。
目标是回答：它们哪里重叠，哪里不同，何时可互相替代，何时不应混用。

## 答案

结论是：这四个系统确实重叠在 stateful multi-step orchestration
这一层，但分化点主要在控制抽象和状态/持久化机制，而不是“能不能接
LLM”这种表层能力。

Temporal 的核心是确定性 Workflow 代码 + Event History/replay，Activities
承担外部副作用；它更像 durable execution engine，AI agent
只是可以承载的一种上层模式。
Airflow 的核心仍是 DAG/task graph；Dynamic Task Mapping、asset scheduling，以及
common.ai provider 让它能覆盖更多 agentic workload，但本质仍是
schedule-/task-centric orchestrator，而不是 LangGraph/MAF 这种原生 agent
runtime。
Microsoft Agent Framework 明确区分 agents 与 workflows：graph `WorkflowBuilder`
和 Python functional workflow surface 都是编排入口，Durable Extension 则把
Durable Task-backed durability 引入这些工作流；不过公开文档对 functional
API、安装包和集成层的成熟度信号并不完全一致。
LangGraph 则是面向长期运行、状态化 agent/workflow 的低层 orchestration
runtime；checkpointers、stores、interrupts 与 fault tolerance
让它在配置后具备持久化与恢复能力，但它不是通用 batch scheduler。

### 轴向矩阵

| 系统 | 控制抽象 | 执行单元 | 状态/持久化 | 动态/自适应行为 | 时间/调度取向 |
| --- | --- | --- | --- | --- | --- |
| Temporal | 确定性 Workflow 代码 | Workflow + Activities | Event History + replay；Activities 承担副作用 | 运行时可动态决策，但 Workflow 逻辑必须确定性 | 时间是 replay-safe 的 workflow primitive，具备 schedule/timer 能力，但不是批调度中心 |
| Airflow | DAG / task graph | Task / operator / task instance | XCom、metadata DB、重试；common.ai provider 提供任务层 AI 增强 | dynamic task mapping、branching、asset scheduling、agent operators | schedule-first，资产/时间触发导向明显 |
| Microsoft Agent Framework | `WorkflowBuilder` 图或 functional `@workflow` | executors / steps / agents | checkpoints；Durable Extension + Durable Task | 条件路由、并行、HITL、Python 控制流 | 以业务流程编排为中心，不是 schedule-first |
| LangGraph | 低层 graph runtime | node / graph execution | checkpointers + stores；`interrupt()` 依赖 persistence | 条件边、循环、工具调用、interrupt | runtime-first，面向长寿命状态机，不是批调度器 |

如果要选型，可以按轴判断，而不是按“是不是 AI”判断：

1. 需要强确定性重放、长时间运行、并把外部副作用关进受控边界：优先 Temporal。
2. 需要 DAG 编排、时间表/资产触发、任务级可观测性，并希望把部分 LLM/agent
   工作塞进现有 Airflow 体系：优先 Airflow。
3. 需要明确区分 agent 与 workflow，且希望用 graph/functional 两种 surface
   表达流程：看 Microsoft Agent Framework，但要把 experimental/prerelease
   信号纳入风险评估。
4. 需要面向 long-running stateful agent 的低层 runtime，并愿意自己配置
   persistence/checkpointing：看 LangGraph。

这四者不是同一类产品，但也不是互不相干；它们是在同一个多步状态化编排问题空间里，沿着不同控制抽象和持久化策略分化出来的。

## 影响

- Temporal 更适合“必须稳定重放、且副作用要被显式隔离”的场景。
- Airflow 更适合“DAG 与调度/资产驱动天然重要、同时逐步吸收 agentic 任务”的场景。
- Microsoft Agent Framework 更适合在其 agent 生态里做显式 workflow/agent
  编排，并接受 API surface 成熟度不完全齐整。
- LangGraph 更适合把 agent 运行时做得更细、更状态化，但不把自己包装成调度系统。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| wiki | [Temporal 工作流文档投影](../sources/temporal-workflow-docs.md) | Temporal 官方文档与博客的来源投影。 |
| wiki | [Apache Airflow 工作流文档投影](../sources/apache-airflow-workflow-docs.md) | Airflow 官方文档与博客的来源投影。 |
| wiki | [Microsoft Agent Framework 工作流文档投影](../sources/microsoft-agent-framework-workflow-docs.md) | Microsoft Agent Framework 官方文档的来源投影。 |
| wiki | [LangGraph 工作流与持久化文档投影](../sources/langgraph-workflow-docs.md) | LangGraph 官方文档的来源投影。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| 四者都属于多步状态化工作编排系统，但分化点主要在控制抽象和状态/持久化机制。 | 上方四个 source page。 | 这是综合判断，不是任何单一厂商文档的原话。 |
| Temporal 的工作流层要求确定性，Activities 承担非确定性副作用，并通过 Event History/replay 恢复。 | [Temporal 工作流文档投影](../sources/temporal-workflow-docs.md) | AI agent 只是可承载模式，不等于专用 agent runtime。 |
| Airflow 仍是 DAG/task graph-centric；dynamic task mapping、asset scheduling 与 common.ai 扩展了 agentic 用法。 | [Apache Airflow 工作流文档投影](../sources/apache-airflow-workflow-docs.md) | common.ai provider 是快速演进的增强层，不应当成 Airflow 核心语义已整体转向 agent runtime。 |
| Microsoft Agent Framework 同时暴露 graph 与 functional 两类 workflow surface，且公开文档对成熟度给出混合信号。 | [Microsoft Agent Framework 工作流文档投影](../sources/microsoft-agent-framework-workflow-docs.md) | functional API 明确 experimental，不能按统一 GA 处理。 |
| LangGraph 是低层 orchestration runtime；持久化依赖 checkpointers/stores，无法配置 persistence 时不应假定可恢复。 | [LangGraph 工作流与持久化文档投影](../sources/langgraph-workflow-docs.md) | durability 是配置后的能力，不是无条件默认。 |
