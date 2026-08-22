## Purpose
约定工作流 LLM 节点：用 prompt 模板 + 模型 provider 生成文本，对照 Dify LLM 节点的学习向子集。

## ADDED Requirements

### Requirement: LLM 节点配置
图中 `data.type` 为 `llm` 的节点 MUST 提供 prompt 模板字段（如 `data.prompt`），并 MAY 携带模型名等扩展字段（本 slice 可忽略或仅透传给 provider）。

#### Scenario: 缺 prompt 被拒绝
- **WHEN** 创建或校验含 llm 节点但缺少 prompt 的图
- **THEN** 系统 MUST 以客户端错误拒绝

### Requirement: Prompt 渲染与生成成功
Runner SHALL 用当前变量渲染 llm 节点的 prompt，调用配置的 LlmProvider，并将生成文本写入运行变量空间（至少 `text`）。

#### Scenario: stub provider 生成文本
- **WHEN** 图含 start → llm → end，inputs 满足 prompt 占位符，且使用默认 stub provider
- **THEN** 运行 MUST 成功，且 outputs 含非空 `text`

### Requirement: Provider 失败可观测
Provider 调用失败或 prompt 渲染失败时，run MUST 标记 failed，并 MUST 写入含失败信息的事件或 error 字段。

#### Scenario: 缺变量导致失败
- **WHEN** llm prompt 引用运行变量中不存在的键
- **THEN** 按 run_id 查询 MUST 看到 failed，且能读到失败原因
