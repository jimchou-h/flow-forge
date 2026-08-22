## 1. 图与校验

- [x] 1.1 扩展节点类型支持 `code`，校验 `data.code` 必填与长度上限，单测覆盖合法/非法图
- [x] 1.2 更新未知类型拒绝用例（llm 等仍失败；code 可通过）

## 2. 受控执行

- [x] 2.1 实现 code 节点执行（受控 globals、`result` 输出约定），单测：成功变换
- [x] 2.2 单测：语法/运行错误 → run failed + 事件或 error 可读
- [x] 2.3 将 code 分支接入 WorkflowRunner 调度循环

## 3. 联调与文档

- [x] 3.1（可选）web 示例增加含 code 的预填图，或仅在 api README 增加 curl 示例
- [x] 3.2 更新 CONTEXT / api README 说明安全边界与 `result` 约定；全量 `uv run pytest` 通过
