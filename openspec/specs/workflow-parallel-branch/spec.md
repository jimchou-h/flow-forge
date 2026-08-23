# workflow-parallel-branch Specification

## Purpose
约定工作流并行分支（学习向）：fan-out 多出边与 join 汇合，对照 Dify 并行分支的简化子集；本 slice 用同步顺序执行模拟并行。

## Requirements

### Requirement: Fan-out 多出边
非 if-else 节点 MAY 拥有多条不带 `source_handle` 的出边；Runner SHALL 在该节点成功后调度其全部后继支路（本 slice 为同步顺序执行）。

#### Scenario: 双支出边均被执行
- **WHEN** 图中某节点有两条无 handle 出边分别接到 B 与 C，再汇合到 end
- **THEN** 成功运行的事件 MUST 同时包含 B 与 C 的成功记录

### Requirement: Join 汇合
入度大于 1 的节点 MUST 在全部前驱成功之后才执行一次。

#### Scenario: 汇合点只执行一次
- **WHEN** B 与 C 均指向同一 end
- **THEN** end 的 `node_succeeded` 事件 MUST 恰好出现一次，且发生在 B、C 均成功之后

### Requirement: 支路失败使 run 失败
任一支路上的节点失败时，run MUST 标记 failed，且 MUST 记录失败事件。

#### Scenario: 一支失败
- **WHEN** fan-out 后某一支 template/code 失败
- **THEN** 按 run_id 查询 MUST 看到 failed，且能读到失败原因
