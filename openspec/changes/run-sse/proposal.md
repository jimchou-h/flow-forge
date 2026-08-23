## Why

画布与引擎已闭环，但运行仍是「请求结束才一次性吐出全部 events」。对照 Dify 的运行流式反馈，补上 **SSE**：在同步执行过程中边跑边推送节点事件，前端才能高亮当前节点、改善可观测性，而不必先上 Celery。

## What Changes

- API：新增流式运行入口（如 `POST /workflows/<id>/runs/stream` 或同路径 `Accept: text/event-stream`），在执行中推送 `node_started` / `node_succeeded` / `node_failed` 与终态 `run_finished`
- Runner：抽出可回调/可迭代的执行路径，写库与推送共用同一事件序列；既有 JSON 同步 `POST .../runs` 行为保持不变
- Web：画布运行可选走 SSE，按事件高亮当前 `node_id`，结束后仍展示 outputs / 完整 events
- 单测：流式响应含有序事件；失败时仍推送失败事件与终态
- **不**做：真异步队列、多订阅者 fan-out、断线续传复杂协议、LLM token 级流式

## Capabilities

### New Capabilities

- `workflow-run-sse`: 运行过程 SSE 事件契约与推送行为

### Modified Capabilities

- `workflow-http-api`: 增加流式运行端点（或协商）
- `web-console` / `web-canvas`: 运行时可消费 SSE 并反馈到画布

## Impact

- 主要改动：`runner.py`（回调钩子）、`controllers/runs.py`、`web` 运行客户端
- 既有轮询/一次返回路径保留，便于 curl 与旧联调
- 下一刀可考虑后台异步 run，本 change 仍在同步请求内流式写出
