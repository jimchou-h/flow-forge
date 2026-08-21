## Why

后端已能创建图、同步跑通并按 `run_id` 查事件，但仍只能靠 curl 演示。需要一块极简 Web，让学习路径上「看得见」工作流联调，并为后续画布留出 Next 工程位。

## What Changes

- 在 `web/` 初始化 Next.js（App Router）学习向控制台雏形
- 提供一页联调 UI：粘贴/编辑最小图 JSON、填写运行 inputs、触发 Run、展示 run 终态与逐步 events
- 通过 HTTP 调用已有 API（`/workflows`、`/runs`）；开发期配置 API 基址（如环境变量）
- 处理 CORS 或同域代理，使浏览器可访问本地 Flask
- **不**做：拖拽画布、账号、SSE、LLM 节点、复杂状态管理

## Capabilities

### New Capabilities

- `web-console`: Next 应用骨架与联调页（图 JSON → Run → 看 events）
- `web-api-bridge`: 浏览器访问后端的基址/代理约定与错误展示

### Modified Capabilities

- （无）

## Impact

- 新增 `web/` Node/Next 依赖与脚本；根 README 补充前后端同时启动说明
- 依赖已归档的 `workflow-http-api` / `workflow-runner`
- 后续画布 change 可在本 Next 工程上扩展，而非另起空壳
