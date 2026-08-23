## Purpose
扩展图校验：允许多出边 fan-out（无 source_handle）；与 if-else 的带 handle 双出边规则并存。

## MODIFIED Requirements

### Requirement: 图字段子集兼容
图中每个节点 MUST 至少包含 `id` 与 `data`；每条边 MUST 包含 `source` 与 `target`；边 MAY 包含 `source_handle`（仅 if-else 出边使用）。

#### Scenario: 缺少边端点则拒绝
- **WHEN** 客户端提交的某条边缺少 `source` 或 `target`
- **THEN** 系统 MUST 以客户端错误拒绝该请求

#### Scenario: 非 if-else 多出边不得带 handle
- **WHEN** 非 if-else 节点的某条出边带有 `source_handle`
- **THEN** 系统 MUST 以客户端错误拒绝

### Requirement: 本阶段支持的节点类型
系统 SHALL 继续接受 `start`、`template`、`end`、`code`、`llm`、`if-else`；未知类型 MUST 拒绝。

#### Scenario: 含 fan-out 的合法图可创建
- **WHEN** 客户端提交 start 后接双出边汇合到 end 的图（无非法 handle）
- **THEN** 系统 MUST 允许创建并持久化
