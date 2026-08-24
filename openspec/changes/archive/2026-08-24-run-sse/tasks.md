## 1. API 流式执行

- [x] 1.1 Runner 增加事件回调/可迭代执行，落库与推送共用序列；非流式路径回归
- [x] 1.2 实现 `POST .../runs/stream` SSE；单测成功流与失败流

## 2. Web 消费

- [x] 2.1 前端解析 SSE（POST+stream）；更新 run/events 列表
- [x] 2.2 画布节点按事件高亮 running/succeeded/failed

## 3. 文档与验收

- [x] 3.1 更新 api/web README；说明与 JSON 运行差异
- [x] 3.2 `uv run pytest` + `pnpm build` 通过
