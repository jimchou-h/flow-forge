# Flow Forge — 领域上下文

学习向项目：对照 [Dify](https://github.com/langgenius/dify) 的分层与 Workflow 概念，由简到繁实现可跑的图编排。技术博文落在 `docs/blog/`。

## 词汇表

| 术语 | 含义 |
|------|------|
| Workflow（工作流） | 由节点与边组成的可执行图；本仓北星 |
| Graph / draft（图定义） | 工作流定义；关键字段与 Dify draft **子集兼容** |
| Node（节点） | 图上的一步；含 Start / Template / Code / LLM / If-Else / End |
| LLM 节点 | 用 prompt 模板 + LlmProvider 生成文本；默认 stub，可选 OpenAI 兼容 HTTP |
| If/Else 节点 | 按条件互斥选择 true/false 出边（对照 Dify If/Else 学习子集；非并行） |
| Template 节点 | 用上游变量做字符串模板渲染的确定性节点 |
| Run（运行） | 一次工作流执行实例；有 `run_id` |
| Event（事件） | 单次运行内的逐步状态记录（节点开始/成功/失败等），供轮询 |
| Runner（执行器） | `WorkflowRunner`：同步执行入口；日后可迁到后台而不改事件模型 |
| Code 节点 | 在受控环境中执行一小段代码/表达式，读写工作流变量（对照 Dify Code 节点的学习子集） |
| Controller / Service / Core | HTTP 解析 → 编排 → 领域执行（对齐 Dify 命名子集） |

## 近期非目标

- 多租户 / 账号体系
- Celery / 生产级异步队列（先轮询，再 SSE）
- 以 REPL Agent 为主线的另一类产品形态
- 并行 fan-out/join、多租户之外的画布级产品化（If/Else 之后再考虑拖拽画布）

## 技术栈（已锁定）

- `api/`：Python、Flask（薄 Blueprint + Pydantic）、uv、SQLite、SQLAlchemy
- `web/`：Next.js 联调台（App Router；`/api-proxy` rewrite 到本地 Flask）
- 流程：OpenSpec + GitHub Issues + 竖切 TDD（unified-dev-workflow）
- 已归档：`openspec/changes/archive/2026-08-21-bootstrap`（API 探活骨架）
- 已归档：`openspec/changes/archive/2026-08-21-graph-runner`（最小图执行 + run/events HTTP）
- 已归档：`openspec/changes/archive/2026-08-22-minimal-web`（Web 联调页）
- 已归档：`openspec/changes/archive/2026-08-22-code-node`（Code 节点：受控 exec + `result` 约定）
- 已归档：`openspec/changes/archive/2026-08-23-llm-node`（LLM 节点：prompt + Stub/OpenAI Provider）
- 进行中：`openspec/changes/if-else-node`（互斥条件分支）
