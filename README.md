# Flow Forge

对照 [Dify](https://github.com/langgenius/dify) 分层与 Workflow 概念的学习向项目：由简到繁实现可跑的图编排。北星是 **Workflow 引擎**（不是 REPL Agent）。技术博客落在 `docs/blog/`。

规格与任务以 `openspec/` 为 SSOT，开发走 OpenSpec + GitHub Issues + 竖切 TDD。

## 仓库结构

| 路径 | 说明 |
|------|------|
| `api/` | Python / Flask / uv / SQLite 后端 |
| `web/` | 前端占位；Next.js 在后续 change 初始化 |
| `docs/blog/` | 系列文草稿与 CSDN catalog |
| `openspec/` | 变更提案与 specs |

## 快速开始（API）

需要 Python **3.12+** 与 [uv](https://docs.astral.sh/uv/)。

```bash
cd api
uv sync
uv run pytest
uv run flask --app flow_forge.app:create_app run --debug
```

另开终端：

```bash
curl http://127.0.0.1:5000/health
```

期望响应：`{"status":"ok"}`。

工作流（创建图 → 同步运行 → 查事件）见 [`api/README.md`](api/README.md)。

## 更多

- 领域词汇：`CONTEXT.md`
- Agent / issue 约定：`AGENTS.md`
- 当前变更：`openspec/changes/graph-runner/`
