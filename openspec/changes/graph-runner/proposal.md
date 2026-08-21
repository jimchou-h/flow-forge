## Why

后端骨架已可探活、可连库，但仍不能执行任何工作流。需要最小可运行的图执行能力（Start → Template → End），才能对照 Dify Workflow 的核心功能面，并为后续轮询/异步升级留下 `run_id` 与事件模型。

## What Changes

- 引入与 Dify draft **字段子集兼容**的图模型（nodes / edges / 关键 id·type·data）
- 支持节点类型：`start`、`template`、`end`
- 同步执行：`WorkflowRunner` 在请求内跑完整图，写入 run 与逐步 events，响应可含最终输出，但客户端以 `run_id` 拉取详情/事件为准
- HTTP：创建/获取 workflow 定义、触发 run、按 `run_id` 查询 run 与 events（为日后轮询预留，本 change 不实现 SSE/队列）
- SQLite 持久化 workflow / run / event（无账号、无多租户）
- 自动化测试：`core/workflow` 单测 + 主路径 HTTP（create → run → events）
- **不**做：Next 联调页、LLM/Code 节点、Celery、SSE、画布 UI

## Capabilities

### New Capabilities

- `workflow-graph`: 图定义的校验与存储（子集兼容字段、Start/Template/End）
- `workflow-runner`: 同步执行、变量传递、Template 渲染、run/event 落库
- `workflow-http-api`: 创建 workflow、触发 run、查询 run 与 events 的 HTTP 契约

### Modified Capabilities

- （无）

## Impact

- 扩展 `api/`：`core/workflow`、services、controllers、SQLAlchemy 模型/迁移或建表
- 依赖现有 `api-bootstrap`（Flask app factory、SQLite engine）
- 下一 change（`minimal-web`）将消费本 API
