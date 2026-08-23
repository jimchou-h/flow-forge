## Context

Runner 当前对任意节点拒绝 `len(next_ids) > 1`。Dify If/Else 用条件选择 true/false 出边。本 change 引入互斥分支（一次只走一条），不做并行。

## Goals / Non-Goals

**目标：**

- `data.type: "if-else"` + `data.condition`（非空；长度上限如 1KB）
- 条件求值：受控命名空间（与 code 类似的 builtins 子集），表达式结果 MUST 为 `bool`；也可约定用户写 `result = ...` 布尔
- 边：`source_handle` 可选；对 if-else 出边 MUST 分别为 `true` 与 `false`
- Runner：求值后选对应 target；事件仍记 node_started/succeeded/failed
- 单测覆盖真/假支与校验失败

**非目标：**

- 并行 fan-out / join
- 多条件 elif 链（本 slice 仅 true/false 两路）
- 可视化画布上的分支编辑器

## Decisions

1. **条件语义**  
   与 code 节点对齐：在受控 locals 中 `exec`/`eval` 用户片段，要求最终 `result` 为 `bool`（文档写清）。比自造 DSL 更贴本仓已有 Code 模式。

2. **边句柄**  
   `GraphEdge.source_handle: Literal["true","false"] | None`。非 if-else 出边应省略；if-else 两条出边必须成对。

3. **调度**  
   普通节点：仍最多一条出边。  
   if-else：恰好两条，按 handle 选一；找不到对应边 → failed。

4. **典型图**  
   `start → if-else ─┬─(true)→ template_a → end`  
   `                └─(false)→ template_b → end`  
   （两端可汇合到同一 end，或各接不同 end；本 slice 允许汇合。）

## Risks / Trade-offs

- [与「并行边」混淆] → README 写明互斥，非同时执行  
- [条件注入风险] → 复用 code 静态禁止项 + 受控 builtins  

## Open Questions

- 无（`result` 必须为 bool；`source_handle` 取值固定 true/false）
