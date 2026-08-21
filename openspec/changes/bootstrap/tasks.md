## 1. API 工程骨架

- [x] 1.1 用 uv 初始化 `api/`（`pyproject.toml`、`requires-python >=3.12`、Flask/Pydantic/SQLAlchemy/pytest 依赖），并确认 `uv sync` 成功
- [x] 1.2 创建可 import 的 `controllers` / `services` / `core` 包布局与 app factory 入口，并确认 import smoke 测试通过

## 2. 健康检查与 SQLite

- [x] 2.1 实现 `GET /health`（Blueprint）并用 Flask test client 测试返回 200 与健康状态
- [x] 2.2 配置默认 SQLite 引擎连通检查（无业务表），加入自动化测试并确认通过

## 3. 文档与占位

- [x] 3.1 编写根 README（项目目的 + 安装/启动/`GET /health` 步骤）并目视确认可跟跑
- [x] 3.2 添加 `web/README.md` 占位（明确 Next 延后）与 `docs/blog/csdn-catalog.md` 骨架，确认路径存在

## 4. 收尾验证

- [ ] 4.1 按 README 本地跑通：`uv sync`、测试套件、手动或脚本请求 `/health`，确认与 specs 场景一致
