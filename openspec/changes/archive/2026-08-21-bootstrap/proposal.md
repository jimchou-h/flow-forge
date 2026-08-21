## Why

空仓无法按「对照 Dify 分层 + OpenSpec/uw」推进后续 Workflow 竖切；需要先落下可复现的 monorepo 骨架与工程约定，才能在下一 change 实现图执行而不混入脚手架噪音。

## What Changes

- 建立 `api/`：uv 管理的 Flask 应用（薄 Blueprint + Pydantic）、`controllers` / `services` / `core` 目录子集、SQLite 可连接、健康检查 HTTP 接口
- 建立 `web/` 占位（仅 README，不初始化 Next）
- 建立根 README、基础忽略规则、pytest smoke（可 import / 可起 app）
- 预留 `docs/blog/` 与本仓 CSDN catalog 骨架（不写正式机制文正文）
- **不**实现 Workflow 图模型、Runner、run/events API（留给 `graph-runner`）

## Capabilities

### New Capabilities

- `api-bootstrap`: 后端可安装、可启动、分层目录就位、健康检查与 SQLite 连通 smoke
- `docs-scaffold`: 学习向文档落点（blog/catalog 骨架）与根 README 指向

### Modified Capabilities

- （无；仓库尚无主 specs）

## Impact

- 新增 Python 工具链（uv）与 Flask/Pydantic/SQLAlchemy 依赖；本地需 Python 3.12+（与常见学习环境对齐，实现时在 README 钉死版本）
- GitHub Issues + triage labels 已配置；本 change 的实现将拆为竖切 issue
- 后续 `graph-runner` / `minimal-web` 依赖本骨架
