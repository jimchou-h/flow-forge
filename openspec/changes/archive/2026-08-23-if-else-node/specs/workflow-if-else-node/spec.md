## Purpose
约定工作流 If/Else 节点：按条件互斥选择 true/false 出边，对照 Dify If/Else 的学习向子集。

## ADDED Requirements

### Requirement: If/Else 节点配置
图中 `data.type` 为 `if-else` 的节点 MUST 提供条件源码字段（如 `data.condition`），执行后 MUST 产生布尔结果（约定赋值 `result` 为 `bool`）。

#### Scenario: 缺条件被拒绝
- **WHEN** 创建或校验含 if-else 节点但缺少 condition 的图
- **THEN** 系统 MUST 以客户端错误拒绝

### Requirement: 互斥出边
if-else 节点 MUST 恰好有两条出边，且 `source_handle` 分别为 `true` 与 `false`。

#### Scenario: 缺 false 出边被拒绝
- **WHEN** if-else 只有一条出边或缺少某一 handle
- **THEN** 系统 MUST 以客户端错误拒绝（校验阶段）或运行失败（若图已非法）

### Requirement: 按条件选择分支
Runner SHALL 求值条件，沿对应 `source_handle` 的边继续执行，且 MUST NOT 同时执行两条分支。

#### Scenario: 条件为真走 true 支
- **WHEN** condition 求值为 true，且 true 支接到可产生可观测输出的下游
- **THEN** 运行 MUST 成功，且 outputs 反映 true 支路径结果（false 支节点 MUST NOT 出现在成功事件中）

#### Scenario: 条件为假走 false 支
- **WHEN** condition 求值为 false
- **THEN** 运行 MUST 成功，且沿 false 支出发；true 支节点 MUST NOT 被执行
