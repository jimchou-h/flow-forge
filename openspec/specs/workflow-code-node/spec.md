# workflow-code-node Specification

## Purpose
约定工作流 Code 节点：在受控环境中执行短代码以变换变量，对照 Dify Code 节点的学习向子集，不提供完整操作系统沙箱。

## Requirements

### Requirement: Code 节点配置
图中 `data.type` 为 `code` 的节点 MUST 提供可执行源码字段（如 `data.code`），并 MAY 声明输出变量名（默认写入约定键如 `result` / `text`，实现时钉死一种并写进文档）。

#### Scenario: 缺代码被拒绝
- **WHEN** 创建或校验含 code 节点但缺少源码字段的图
- **THEN** 系统 MUST 以客户端错误拒绝

### Requirement: 受控执行成功
Runner SHALL 在 code 节点用当前变量作为输入命名空间执行源码，并将约定输出写回变量空间供下游使用。

#### Scenario: 代码加工上游文本
- **WHEN** 上游产生字符串变量，code 节点将其转换（例如大写或拼接）后接到 end
- **THEN** 运行 MUST 成功，且最终 outputs 反映代码结果

### Requirement: 执行失败可观测
代码语法错误、运行期错误或违反安全限制时，run MUST 标记 failed，并 MUST 写入含失败信息的事件或 error 字段；API 进程 MUST 保持可用。

#### Scenario: 非法代码导致失败
- **WHEN** code 源码无法执行（语法错误或受控策略拒绝的操作）
- **THEN** 按 run_id 查询 MUST 看到 failed，且能读到失败原因
