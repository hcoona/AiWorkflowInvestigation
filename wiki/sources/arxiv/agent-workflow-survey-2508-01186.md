---
schema_version: 2
page_type: source
title: "arXiv 2508.01186 Agent Workflow Survey"
status: active
created: 2026-06-12
updated: 2026-06-13
summary: "Agent workflow 综述论文的提炼性单来源投影。"
maintenance:
  edit_policy: update
validation:
  body_contract: source
tags:
  - arxiv
  - agent-workflow
  - survey
---

## 来源边界

本页只投影 arXiv:2508.01186 `A Survey on Agent Workflow -- Status and Future`。
原始材料已通过 DeepXiv 保存到
[`raw/arxiv/2025-08-02-2508.01186-a-survey-on-agent-workflow-status-and-future.md`](../../../raw/arxiv/2025-08-02-2508.01186-a-survey-on-agent-workflow-status-and-future.md)；
本页使用该 raw 文件作为主证据。

## 提炼总结

这篇综述的主要价值不是给出一个可直接采用的工程标准，而是把 agent workflow
从零散的 agent 框架、产品和论文中抽象成一组可比较的模式语言。
论文将 agent workflow 放在 LLM agent、传统 workflow
management、多智能体系统和工具调用生态的交叉处：agent 负责规划、推理、
调用工具和适应环境，workflow 则提供任务顺序、依赖、状态流转和协作边界。

论文提出的基础框架可压缩为三层：用户交互层、workflow management 层和 agent
collaboration 层。
其中 workflow management 层负责解释任务流程、
调度执行、触发终止条件并协调工具或参与者；agent collaboration 层则覆盖
planner、executor、parser/interpreter、critic/reviewer、memory manager 和
communicator 等角色分工。

对本 wiki 最有用的分类来自两条轴线。
第一条是能力轴：planning、tool
use、multi-agent、memory、GUI、API/self-reflection/custom tools 等能力是否
存在。
第二条是架构轴：agent roles、flow、representation、language、protocol 和
deployment。
论文还把 workflow modes 拆成 chain、
parallelization、routing、orchestrator-workers 与 evaluator-optimizer，
这些模式更适合作为 agent workflow 的形态标签，而不是某个产品的完整运行语义。

论文对优化、安全和未来方向的贡献是提醒 agent workflow 不只是“把多个 agent
串起来”。
优化层面涉及手工重构、启发式算法、Bayesian optimization 和 generative
optimizer，并把调度、协调结构、工作流表示、token 成本与延迟视作优化对象。
安全层面区分外部风险和内部风险：外部风险包括工具描述投毒、MCP server 风险、LLM
输入污染和隐私泄露；内部风险包括多 agent 协作/竞争、谬误放大、冲突数据和 memory
poisoning。

论文的结论把主要瓶颈归纳为缺少标准化 specification、统一建模语言、
可移植中间表示、互操作执行接口和足够细粒度的 evaluation metrics。
它给出的未来方向包括协议标准化、动态规划、adaptive tool use、domain-specific
customization、多模态集成、多 agent collaboration 和更模块化的部署生态。

## 可复用关键主张

- Agent workflow 可以被理解为把 agent 的自主规划、工具调用、记忆和协作能力
  放入结构化流程中的编排框架；workflow 在这里是 agent 生态的控制骨架，而不只是
  传统业务流程自动化脚本。
- 论文的三层框架把 UI/UX、workflow management 和 agent collaboration 分开，
  适合用来区分“用户交互面”“流程解释/调度面”和“agent 间协作面”。
- 论文的比较矩阵同时覆盖能力轴和架构轴；前者适合回答“系统能做什么”，后者适合
  回答“系统如何表达、连接和部署 workflow”。
- Chain、parallelization、routing、orchestrator-workers 和 evaluator-optimizer
  是 agent workflow 的常见 workflow modes，可作为模式词汇使用，但不能直接等同于
  Temporal、Airflow、LangGraph 或 Microsoft Agent Framework 的运行时语义。
- Agent workflow 的主要开放问题集中在 specification、interoperability、
  workflow optimization、security、evaluation 和 multi-modal / multi-agent
  integration。

## 对本 wiki 的使用方式

本页适合作为 agent workflow 文献语境的来源锚点：当分析页需要说明“agent workflow
研究社区如何给 agent/workflow runtime 分类”时，可引用本页。
当分析具体产品语义时，应继续优先引用产品官方文档或源码 source page；本论文只能
提供研究综述级 taxonomy 和问题清单，不能替代产品级 evidence。

## 限制与冲突

- 该论文是综述，分类粒度服务于 agent workflow 研究，不等价于产品官方 taxonomy。
- 论文包含 2025 年后系统状态；具体项目状态需要回到对应官方文档复核。
- 表格覆盖的系统包含研究原型、开源框架、SaaS/no-code 产品和提示模式，成熟度、
  部署边界和能力定义并不完全可比。
- DeepXiv raw Markdown 保留了论文正文和表格提取结果，但表格为 HTML 行内形式；
  如需严格核对表格单元，应回到 arXiv PDF 或原始 LaTeX。

## 证据与限制

### 证据单元

| 类型 | 引用 | 说明 |
| --- | --- | --- |
| raw | [`raw/arxiv/2025-08-02-2508.01186-a-survey-on-agent-workflow-status-and-future.md`](../../../raw/arxiv/2025-08-02-2508.01186-a-survey-on-agent-workflow-status-and-future.md) | arXiv:2508.01186 的 DeepXiv raw Markdown 提取正文；访问时间 2026-06-13。 |

### 支撑的主张

| 主张 | 证据 | 限制 |
| --- | --- | --- |
| agent workflow 可被视为 agent 能力与结构化流程编排的交叉框架。 | 上方证据单元；论文 Introduction、Background 和 Framework 章节。 | 这是综述论文的研究视角，不是行业统一定义。 |
| agent workflow 框架可按 UI/UX、workflow management、agent collaboration 三层阅读。 | 上方证据单元；论文 Framework 章节。 | 三层框架偏概念化，不能直接映射到每个产品的部署组件。 |
| agent workflow 可按 capabilities 和 architecture 两条轴线分析。 | 上方证据单元；论文 Comparative Analysis 章节及 Table 1、Table 2。 | 表格系统异质性强，不能作为产品成熟度评分。 |
| agent workflow management 涉及 chain、parallelization、routing、orchestrator-workers 和 evaluator-optimizer 等模式。 | 上方证据单元；论文 Workflow Management 小节。 | 这些模式用于解释 agent workflow，不直接替代 Temporal/Airflow 等产品语义。 |
| agent workflow 研究仍存在标准化、互操作、安全、优化和 evaluation 问题。 | 上方证据单元；论文 Optimization、Security、Limitations and Future Directions 章节。 | 具体风险需要结合系统实现、部署环境和官方安全文档评估。 |
