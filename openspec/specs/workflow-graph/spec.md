# workflow-graph Specification

## Purpose
约定 Flow Forge 如何校验并持久化一份最小工作流图：关键字段与 Dify draft 子集兼容，本阶段支持 start、template、code、llm、if-else、end。

## Requirements

### Requirement: 工作流图可持久化
系统 SHALL 允许按 id 创建并读取工作流定义；图载荷 MUST 包含 `nodes` 与 `edges` 集合。

#### Scenario: 创建并回读工作流
- **WHEN** 客户端提交一份合法图（含由边连接的 start、template、code、llm、if-else、end 节点）以创建工作流
- **THEN** 系统 MUST 持久化该定义，并在按 id 读取时返回相同图内容

### Requirement: 图字段子集兼容
图中每个节点 MUST 至少包含 `id` 与 `data`（或等价嵌套结构），并以与 Dify 风格兼容的 `type` 区分节点类型（本子集范围内）；每条边 MUST 包含 `source` 与 `target` 节点 id；边 MAY 包含 `source_handle`（用于 if-else 分支）。

#### Scenario: 缺少边端点则拒绝
- **WHEN** 客户端提交的某条边缺少 `source` 或 `target`
- **THEN** 系统 MUST 以客户端错误拒绝该请求，且 MUST NOT 创建对应运行

### Requirement: 本阶段支持的节点类型
系统 SHALL 接受可执行工作流中的节点类型 `start`、`template`、`end`、`code`、`llm`、`if-else`；对此外的未知节点类型 MUST 拒绝执行。

#### Scenario: 未知节点类型被拒绝
- **WHEN** 工作流图中出现上述以外的节点类型
- **THEN** 创建或运行 MUST 失败，并返回明确的客户端错误信息

#### Scenario: 含 code 的合法图可创建
- **WHEN** 客户端提交 start → code → end（或含 template）且 code 字段齐全的图
- **THEN** 系统 MUST 允许创建并持久化

#### Scenario: 含 llm 的合法图可创建
- **WHEN** 客户端提交 start → llm → end（或含 template/code）且 prompt 字段齐全的图
- **THEN** 系统 MUST 允许创建并持久化

#### Scenario: 含 if-else 的合法图可创建
- **WHEN** 客户端提交含 if-else、condition 齐全、且 true/false 出边成对的图
- **THEN** 系统 MUST 允许创建并持久化
