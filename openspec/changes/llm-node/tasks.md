## 1. 图与校验

- [ ] 1.1 扩展节点类型支持 `llm`，校验 `data.prompt` 必填与长度上限，单测覆盖合法/非法图
- [ ] 1.2 更新未知类型拒绝用例（tool 等仍失败；llm 可通过）

## 2. Provider 与执行

- [ ] 2.1 定义 `LlmProvider` 协议与 `StubLlmProvider`（确定性输出），单测覆盖
- [ ] 2.2 实现 llm 节点：prompt 渲染 + 调 provider + 写 `text`；Runner 接入
- [ ] 2.3 单测：缺变量 / provider 异常 → run failed + 事件
- [ ] 2.4（可选）`OpenAiCompatibleProvider` + env 文档；无 key 时 app 仍默认 stub

## 3. 联调与文档

- [ ] 3.1 更新 api README / CONTEXT；可选 web 预填 llm 示例图
- [ ] 3.2 全量 `uv run pytest` 通过
