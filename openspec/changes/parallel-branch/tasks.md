## 1. 图与校验

- [ ] 1.1 允许非 if-else 多出边；禁止其出边带 `source_handle`；单测合法/非法图
- [ ] 1.2 保持 if-else 成对 handle 规则不变

## 2. 调度

- [ ] 2.1 实现 fan-out 后同步顺序执行各支 + join 前驱计数；单测双支汇合
- [ ] 2.2 单测：一支失败 → run failed；if-else 回归仍绿
- [ ] 2.3（如需要）重构 Runner 调度循环，避免破坏既有线性路径

## 3. 联调与文档

- [ ] 3.1 更新 api README / CONTEXT（顺序模拟并行、变量 scoped 键）；可选 web 示例图
- [ ] 3.2 全量 `uv run pytest` 通过
