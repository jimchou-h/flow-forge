## Purpose
联调台消费运行 SSE，在画布上反馈当前执行节点。

## ADDED Requirements

### Requirement: 画布运行可走 SSE
联调页 SHALL 支持通过 SSE 流式运行当前画布图，并 MUST 根据事件更新节点可视化状态（至少区分运行中 / 成功 / 失败）。

#### Scenario: 运行中高亮节点
- **WHEN** 用户从画布发起流式运行
- **THEN** 在收到某节点 `node_started`（或等价）时，该节点 MUST 呈现可区分的运行中样式，直至成功或失败事件
