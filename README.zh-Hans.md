# AI Workflow Investigation

[English](README.md)

本仓库用于调研 AI 增强 Workflow 的机会：也就是让 AI
系统帮助人与团队规划、执行、验证或协调工作流程。

本项目关注实用的软件工程 Workflow 以及相邻的知识工作流程。
研究重点包括 AI 如何在 Workflow
生命周期中与人协作，例如生成计划、根据人的反馈修改计划、执行部分节点、设置人机协同检查点，以及确认由人手动负责的步骤已经完成。

## 研究范围

本调研包括但不限于：

- AI 根据人的输入、约束和反馈生成或修改 Workflow 计划。
- AI 在安全、有用且可审计的边界内执行部分 Workflow 节点。
- AI 与人的交互模式，用于确认人工完成的 Workflow 节点。
- 混合人类/AI 执行过程中的 Workflow 状态跟踪、交接设计和证据捕获。
- 包含自主或半自主 AI 步骤的 Workflow 所需的可靠性、可审查性和控制机制。

## 目标读者

本仓库面向正在评估 AI 如何增强真实 Workflow 的软件工程师。
项目材料旨在帮助工程师思考架构、运行模式、自治边界，以及哪些地方必须明确保留人的判断，而不是把
Workflow 执行变成不透明的自动化系统。

## 知识组织

本仓库已初始化为 LLM-Wiki。
持久化综合结论存放在 `wiki/`，经过筛选的证据存放在 `raw/`，Agent 操作规则存放在
`AGENTS.md`。

在修改持久化 wiki 内容后，请运行仓库声明的验证任务：

```bash
mise run wiki-check
```

## Git Hooks

本仓库通过 mise 使用 [hk](https://hk.jdx.dev/)。
hk 的 `pre-commit`、`check` 和 `fix` hooks 运行同一组校验步骤，其中包括执行现有
`mise run wiki-check` 校验任务的 `check-wiki` 步骤。
`.gitattributes` 由 `gitattributes.pkl` 生成；hooks 还会检查 Git index
中的文件是否都被其中显式的文本或二进制规则覆盖。

安装项目工具：

```bash
mise install
```

安装或更新 git hooks：

```bash
mise exec -- hk install --mise
```

手动运行 pre-commit checks：

```bash
mise exec -- hk run pre-commit
```

对全部文件运行 check-only hook：

```bash
mise exec -- hk check --all
```

对全部文件运行 checks 并应用已配置的 fixes：

```bash
mise exec -- hk fix --all
```

修改 `gitattributes.pkl` 后，使用以下命令重新生成 `.gitattributes`：

```bash
mise run gitattributes-generate
```

## 许可证

本仓库采用 Creative Commons Attribution-NonCommercial-ShareAlike 4.0
International License 授权。 详见 [LICENSE](LICENSE)
和官方许可证文本：<https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode>。
