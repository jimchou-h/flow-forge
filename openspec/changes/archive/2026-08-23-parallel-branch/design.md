## Context

当前 Runner：普通节点最多一条出边；if-else 按 handle 互斥选一。本 change 放开「无 handle 的多出边」并实现汇合，用同步顺序执行模拟并行。

## Goals / Non-Goals

**目标：**

- 合法图：某节点可有 ≥2 条出边，且均无 `source_handle`（与 if-else 的成对 handle 区分）
- 执行：fan-out 后按稳定顺序（如边声明顺序）依次跑完各支，直到进入共同后继
- Join：入度 >1 的节点，等所有前驱 `node_succeeded` 后再执行
- 失败：任一支失败则 run failed，已记录的事件保留
- 单测覆盖双支汇合成功与一支失败

**非目标：**

- 多线程真并行、超时取消 sibling
- 动态分支数、嵌套并行与 if-else 的复杂组合矩阵（允许简单嵌套但不单独开任务）
- 画布

## Decisions

1. **执行模型：同步顺序 fan-out**  
   用「按出边顺序逐支 DFS/BFS 到 join 边界」实现；文档写明「学习向顺序模拟，非并发」。事件时间戳仍反映实际执行顺序。

2. **Join 判定**  
   维护 `pending_predecessors[node_id]`；每条入边前驱成功则减一；归零后入队执行。start 入度为 0。

3. **与 if-else 边界**  
   - if-else：必须恰好 true/false 两条带 handle 的出边，仍互斥  
   - 其它节点：多出边时 **禁止** 带 `source_handle`；有 handle 则校验失败或仅允许 if-else

4. **变量**  
   共享 `variables` dict；支路写 `{node_id}.text` / `{node_id}.result`。全局 `text` 可能被后执行支路覆盖——README 提醒用 scoped 键做汇合展示。

5. **典型图**  
   `start → A ─┬→ B →┐`  
   `           └→ C →┴→ end`  
   （B、C 均为 template/code 等；end 入度 2。）

## Risks / Trade-offs

- [误以为已真并行] → README 明确顺序模拟  
- [全局 `text` 覆盖] → 文档 + 示例用 scoped 键  

## Open Questions

- 无（顺序 = 边在 `edges` 数组中的出现顺序）
