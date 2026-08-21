# Flow Forge — 领域上下文

学习向项目：对照 [Dify](https://github.com/langgenius/dify) 的分层与 Workflow 概念，由简到繁实现可跑的图编排。技术博文落在 `docs/blog/`。

## 词汇表

| 术语 | 含义 |
|------|------|
| Workflow（工作流） | 由节点与边组成的可执行图；本仓北星 |
| Graph / draft（图定义） | 工作流定义；关键字段与 Dify draft **子集兼容** |
| Node（节点） | 图上的一步；第一阶段含 Start / Template / End |
| Template 节点 | 用上游变量做字符串模板渲染的确定性节点 |
| Run（运行） | 一次工作流执行实例；有 `run_id` |
| Event（事件） | 单次运行内的逐步状态记录（节点开始/成功/失败等），供轮询 |
| Runner（执行器） | `WorkflowRunner`：同步执行入口；日后可迁到后台而不改事件模型 |
| Controller / Service / Core | HTTP 解析 → 编排 → 领域执行（对齐 Dify 命名子集） |

## 近期非目标

- 多租户 / 账号体系
- Celery / 生产级异步队列（先轮询，再 SSE）
- 以 REPL Agent 为主线的另一类产品形态
- 第一阶段拖拽画布与 LLM 节点

## 技术栈（已锁定）

- `api/`：Python、Flask（薄 Blueprint + Pydantic）、uv、SQLite、SQLAlchemy
- `web/`：最终用 Next（bootstrap 已完成占位）；联调变更再初始化
- 流程：OpenSpec + GitHub Issues + 竖切 TDD（unified-dev-workflow）
- 已归档：`openspec/changes/archive/2026-08-21-bootstrap`（API 探活骨架）
- 已归档：`openspec/changes/archive/2026-08-21-graph-runner`（最小图执行 + run/events HTTP）
