## Context

空仓；OpenSpec / Matt / `CONTEXT.md` 已就位。本 change 只搭可跑骨架。动机见 `proposal.md`；行为见 `specs/`。

## Goals / Non-Goals

**Goals:**

- `api/` 用 uv 可安装；Flask app factory + `/health`；SQLite engine 可 connect
- 目录名对齐 Dify 子集：`controllers` / `services` / `core`
- `web/` 与 `docs/blog/` 占位；根 README 可跟跑

**Non-Goals:**

- Workflow 图、Runner、run/events、ORM 业务表
- flask-restx、Celery、Docker Compose、Next 初始化
- 正式 blog 正文（可在 tasks 末可选草稿，默认不做）

## Decisions

1. **包管理：uv + `api/pyproject.toml`**  
   与 Dify `api/` 习惯一致。备选 poetry/pip-tools — 不如 uv 贴近对照路径。

2. **HTTP：Flask Blueprint，不用 flask-restx**  
   与已锁定「先薄后可迁」一致；本 change 仅 `/health`。

3. **SQLite 文件默认 `api/data/flow_forge.db`（gitignore）**  
   单文件本地库；业务 migration 留到 `graph-runner`。本 change 只证明 `engine.connect()`。

4. **App 入口：`api/app.py` 或 `api/app_factory.py` + `flask --app` 文档化**  
   保持简单；不要过早引入完整 Dify extensions 丛林。

5. **测试：pytest + Flask test client**  
   覆盖 `/health` 与包 import；不引入 e2e。

6. **Python 版本：在 `requires-python` 钉 `>=3.12`**  
   学习向足够新；若本机更旧，README 写明。

## Risks / Trade-offs

- [空目录过多] → 只建本 change 用到的包路径，避免「目录博物馆」
- [过早引入 SQLAlchemy 模型] → bootstrap 只留 engine/session 工厂钩子，表结构下个 change
- [web 占位被误当成可跑前端] → README 明确「稍后 change」

## Migration Plan

- 全新仓库：合并本 change 后即可本地 `uv sync` + 测 `/health`
- 无生产数据需迁移
