# web-canvas Specification

## Purpose
约定 Flow Forge 最小拖拽画布：可视化编辑工作流图并导出为现有 API 图载荷后运行，对照 Dify 画布的学习向子集。

## Requirements

### Requirement: 画布展示与拖拽
联调页 SHALL 提供基于节点-边的可视化画布；用户 MUST 能拖拽移动节点，并 MUST 能通过拖拽创建边。

#### Scenario: 加载示例后可见节点
- **WHEN** 用户打开联调页（或加载预置示例）
- **THEN** 画布 MUST 显示至少一个 start 节点及示例路径上的其它节点

### Requirement: 添加与配置节点
用户 SHALL 能从面板添加受支持的节点类型（至少 template / code / llm / if-else / end），并 MUST 能编辑选中节点的关键 `data` 字段。

#### Scenario: 添加 template 并编辑模板
- **WHEN** 用户添加 template 节点并填写 `data.template`
- **THEN** 导出的图 JSON MUST 包含该节点且 `data.type` 为 `template`

### Requirement: 从画布运行
用户 SHALL 能在不手写完整 JSON 的情况下，从当前画布触发运行并看到 run 状态与事件。

#### Scenario: 画布编排后跑通
- **WHEN** 用户在画布上保留合法 start→template→end（或等价合法图）并提供所需 inputs 后点击运行
- **THEN** 页面 MUST 展示成功的 run 状态与 outputs（或失败时的 error / 失败事件）
