# Flow Forge

对照 [Dify](https://github.com/langgenius/dify) 分层与 Workflow 概念的学习向项目：由简到繁实现可跑的图编排。北星是 **Workflow 引擎**。技术博客落在 `docs/blog/`。

规格与任务以 `openspec/` 为 SSOT，开发走 OpenSpec + GitHub Issues + 竖切 TDD。

## 仓库结构

| 路径 | 说明 |
|------|------|
| `api/` | Python / Flask / uv / SQLite 后端 |
| `web/` | Next.js 联调台（图 JSON → Run → events） |
| `docs/blog/` | 系列文草稿与 CSDN catalog |
| `openspec/` | 变更提案与 specs |

## 快速开始

需要 **Python 3.12+**、[uv](https://docs.astral.sh/uv/)、**Node 20+**、[pnpm](https://pnpm.io/)。

### 一键起前后端（推荐，Windows）

> 你当前是 Windows：**请用 `dev.ps1` / `dev.cmd`，不要用 `dev.sh`**（`.sh` 是给 macOS/Linux 的）。

在仓库根目录 `D:\Learn\Github\flow-forge` 打开 **PowerShell**，执行：

```powershell
# 首次（装依赖）
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\dev.ps1 -Install

# 日常
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\dev.ps1
```

成功时会**新弹出两个黑色窗口**（API / Web），本窗口只打印两行提示。  
浏览器打开：http://localhost:3000  

也可在资源管理器中双击 `scripts\dev.cmd`（首次建议先在终端跑一遍带 `-Install` 的命令）。

若提示无法运行脚本，多半是执行策略；上面的 `ExecutionPolicy Bypass -File ...` 已绕过，无需改系统策略。

### 1. 后端 API（手动）

```bash
cd api
uv sync
uv run pytest
uv run flask --app flow_forge.app:create_app run --debug
```

探活：`http://127.0.0.1:5000/health`  
工作流 curl 示例见 [`api/README.md`](api/README.md)。

### 2. 前端联调台（手动）

另开终端：

```bash
cd web
pnpm install
pnpm dev
```

打开：http://localhost:3000  

前端经 `/api-proxy` 转发到 Flask（见 [`web/README.md`](web/README.md)）。

## 更多

- 领域词汇：`CONTEXT.md`
- Agent / issue 约定：`AGENTS.md`
- 当前变更：`openspec/changes/parallel-branch/`
