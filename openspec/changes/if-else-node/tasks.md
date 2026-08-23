## 1. 图与校验

- [x] 1.1 扩展节点类型 `if-else`，校验 `data.condition`；边支持可选 `source_handle`
- [x] 1.2 校验 if-else 恰好 true/false 两条出边；单测覆盖合法/非法图

## 2. 条件求值与调度

- [x] 2.1 实现条件求值（受控命名空间，`result` 为 bool），单测真/假
- [x] 2.2 Runner：if-else 按 handle 选后继；非 if-else 仍拒绝多出边
- [x] 2.3 单测：真支 / 假支端到端；条件非 bool 或求值失败 → failed + 事件

## 3. 联调与文档

- [x] 3.1 更新 api README / CONTEXT；可选 web 预填 if-else 示例图
- [x] 3.2 全量 `uv run pytest` 通过
