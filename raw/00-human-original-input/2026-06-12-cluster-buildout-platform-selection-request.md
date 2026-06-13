---
source_type: human-original-input
title: "Cluster Buildout platform selection request"
origin: "User-provided ChatGPT conversation export; human request portion"
recorded: 2026-06-12
language: zh-Hans
topic: "AI workflow platform selection"
raw_admission_reason: "User requested splitting a conversation export into human input and non-authoritative AI draft."
preservation_mode: sanitized-human-input
full_text_preserved: false
cleanup_note: "Split from the original transcript; generalized the scenario and project name to Cluster Buildout."
---

# 用户原始输入：Cluster Buildout 平台选型问题

## 原始输入

你是一个系统架构师，你的任务是帮助团队进行平台选型。在 AI 和 Workflow 结合的领域，比较 Temporal 和 Apache Airflow。

专业口吻，听众是资深软件工程师

主要业务场景是支持 Cluster Buildout，之前跟你讨论过一些内容

拆解下来，可能涉及到

1. 一开始有个 Blueprint 先开始跑
2. 任务节点有得是确定代码机器执行，有得是确定流程 AI Agent 执行，有得是 AI 去 drive (通知，询问，跟进）人去执行
3. 已经通过验证的组件可能在后续的集成验证中失败，一定程度上需要分叉或者回溯，注意这种失败不是全面失败，而是部分失败，可能只影响一些方面的功能，所以应该分裂，不影响的部分继续往下跑，影响的部分等着追上来
4. 一开始设计的流程只是一个大概的设计，具体的情况可能仍然需要在以及跑的过程中继续调整
5. 一个好的 UI 能够让大家知道整体进度是有必要的，但是没有 UI 的产品我们也能用，自己二次开发适配一个界面听起来并不是很困难
