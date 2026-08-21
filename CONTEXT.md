# Flow Forge — Domain Context

学习向项目：对照 [Dify](https://github.com/langgenius/dify) 的分层与 Workflow 概念，由简到繁实现可跑的图编排。技术博客落在 `docs/blog/`（与 Claude Code / harness 系列错开）。

## Glossary

| Term | Meaning |
|------|---------|
| Workflow | 由 nodes 与 edges 组成的可执行图；本仓北星 |
| Graph (draft) | 工作流定义；关键字段与 Dify draft **子集兼容** |
| Node | 图上的一步；第一阶段含 Start / Template / End |
| Template node | 用上游变量做字符串模板渲染的确定性节点 |
| Run | 一次工作流执行实例；有 `run_id` |
| Event | Run 内逐步状态记录（node started/succeeded/failed 等），供轮询 |
| Runner | `WorkflowRunner`：同步执行入口；日后可迁到后台而不改事件模型 |
| Controller / Service / Core | HTTP 解析 → 编排 → 领域执行（对齐 Dify 命名子集） |

## Non-goals (near term)

- 多租户 / 账号体系
- Celery / 生产级异步队列（先轮询，再 SSE）
- 与 react-agent-mini harness 系列重复的 REPL Agent 主线
- 第一阶段拖拽画布与 LLM 节点

## Stack (locked)

- `api/`: Python, Flask (薄 Blueprint + Pydantic), uv, SQLite, SQLAlchemy
- `web/`: 最终 Next（bootstrap 仅占位）；联调 change 再初始化
- 流程: OpenSpec + GitHub Issues + 竖切 TDD（unified-dev-workflow）
