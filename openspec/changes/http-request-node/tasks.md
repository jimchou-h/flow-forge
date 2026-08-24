## 1. 图与校验

- [ ] 1.1 扩展节点类型支持 `http-request`；校验 method（GET/POST）与非空 url；单测合法/非法图
- [ ] 1.2 更新未知类型拒绝用例（http-request 可通过）

## 2. 传输与执行

- [ ] 2.1 定义 `HttpClient` 协议与 `StubHttpClient`；单测覆盖
- [ ] 2.2 实现 http-request 节点执行 + Runner 接入；写入 `status_code` / `body`
- [ ] 2.3 单测：非 2xx / stub 异常 → run failed + 事件
- [ ] 2.4（可选）`HttpxClient` + SSRF 护栏 + env 文档；无网络时默认 stub

## 3. 画布与文档

- [ ] 3.1 Web：面板可添加 http-request，编辑 method/url/body；codec 往返
- [ ] 3.2 更新 api/web README 与 CONTEXT；`uv run pytest` + `pnpm build` 通过
