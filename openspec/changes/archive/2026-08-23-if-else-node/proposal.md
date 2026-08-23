## Why

线性图（单后继）已跑通 start / template / code / llm / end，但仍无法表达「按条件走不同路径」。对照 Dify 的 If/Else 节点，补上互斥分支，才能演示真实工作流的控制流，并打破 Runner「每个节点最多一条出边」的限制（仅对 if-else 放开）。

## What Changes

- 图模型新增节点类型 `if-else`：`data.condition` 为在当前变量上求值的布尔表达式（受控求值，复用 code 节点类似安全边界）
- 边扩展可选 `source_handle`：`true` / `false`；if-else 节点 MUST 恰好有两条出边且各带一个 handle
- Runner：求值条件后沿对应 handle 的出边继续；非 if-else 节点仍禁止多出边
- 单测：真支 / 假支成功路径；缺 handle / 非法表达式失败
- 文档与可选 web 示例图
- **不**做：并行（同时执行多分支）、elif 多路、画布 UI、异步队列

## Capabilities

### New Capabilities

- `workflow-if-else-node`: if-else 配置、条件求值与分支选择

### Modified Capabilities

- `workflow-graph`: 允许 `if-else`；边可带 `source_handle`
- `workflow-runner`: 调度支持互斥双出边

## Impact

- 主要改动：`graph.py`（边字段）、`nodes/if_else.py`、`runner.py` 调度循环
- HTTP 契约形状不变；Web 可增预填分支示例
- 下一刀可考虑并行边或拖拽画布，本 change 不包含
