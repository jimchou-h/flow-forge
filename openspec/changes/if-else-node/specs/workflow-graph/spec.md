## Purpose
扩展图校验：允许 if-else 节点，并为边增加可选 `source_handle`；校验 if-else 的双出边完整性。

## MODIFIED Requirements

### Requirement: 本阶段支持的节点类型
系统 SHALL 接受可执行工作流中的节点类型 `start`、`template`、`end`、`code`、`llm`、`if-else`；对此外的未知节点类型 MUST 拒绝执行。

#### Scenario: 未知节点类型被拒绝
- **WHEN** 工作流图中出现上述以外的节点类型
- **THEN** 创建或运行 MUST 失败，并返回明确的客户端错误信息

#### Scenario: 含 if-else 的合法图可创建
- **WHEN** 客户端提交含 if-else、condition 齐全、且 true/false 出边成对的图
- **THEN** 系统 MUST 允许创建并持久化

### Requirement: 图字段子集兼容
图中每个节点 MUST 至少包含 `id` 与 `data`；每条边 MUST 包含 `source` 与 `target`；边 MAY 包含 `source_handle`（本子集用于 if-else 分支）。

#### Scenario: 缺少边端点则拒绝
- **WHEN** 客户端提交的某条边缺少 `source` 或 `target`
- **THEN** 系统 MUST 以客户端错误拒绝该请求，且 MUST NOT 创建对应运行
