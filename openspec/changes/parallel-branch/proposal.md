## Why

If/Else 已支持互斥双出边，但 Runner 对「普通节点多出边」仍一律拒绝，无法表达「同时走多条支路再汇合」。对照 Dify 的并行分支，补上学习向 fan-out / join，才能演示完整控制流谱系（线性 → 互斥 → 并行），并为后续画布提供可跑的图语义。

## What Changes

- 允许**非** if-else 节点有多条无 `source_handle` 的出边（fan-out）
- Runner 同步**顺序**执行各支路（学习向模拟并行，非多线程），每支独立推进直到汇合点
- 多入边节点（join）：仅当全部前驱已成功后才执行一次
- 变量约定：各支路结果保留在 `{node_id}.*`；汇合后 `end` 可读取各支已写入的变量；文档钉死合并规则（本 slice：共享变量空间 + 后写覆盖同名全局键如 `text`，鼓励用节点 scoped 键）
- 任一支失败 → 整次 run failed
- 单测：双支 fan-out → join → end；与 if-else 互斥语义不混淆
- **不**做：真并行线程/进程、复杂 barrier 策略、画布 UI、SSE

## Capabilities

### New Capabilities

- `workflow-parallel-branch`: fan-out / join 调度与校验约定

### Modified Capabilities

- `workflow-graph`: 允许多出边（无 handle）；校验 join 入边完整性（可选）
- `workflow-runner`: 调度从「单后继 / if-else 选一」扩展为「多支顺序执行 + 汇合」

## Impact

- 主要改动：`runner.py` 调度模型（可能引入就绪队列 / 前驱计数）
- if-else 行为保持不变
- HTTP 契约形状不变；Web 可增预填并行示例图
- 下一刀可考虑拖拽画布，本 change 不包含
