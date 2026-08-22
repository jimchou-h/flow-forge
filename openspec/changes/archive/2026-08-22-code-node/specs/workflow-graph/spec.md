## Purpose
扩展图校验：在既有 start / template / end 之外，允许并校验 code 节点类型及其必需字段。

## MODIFIED Requirements

### Requirement: 本阶段支持的节点类型
系统 SHALL 接受可执行工作流中的节点类型 `start`、`template`、`end`、`code`；对此外的未知节点类型 MUST 拒绝执行（含创建或运行路径上的校验失败）。

#### Scenario: 未知节点类型被拒绝
- **WHEN** 工作流图中出现 start / template / end / code 以外的节点类型
- **THEN** 创建或运行 MUST 失败，并返回明确的客户端错误信息

#### Scenario: 含 code 的合法图可创建
- **WHEN** 客户端提交 start → code → end（或含 template）且 code 字段齐全的图
- **THEN** 系统 MUST 允许创建并持久化
