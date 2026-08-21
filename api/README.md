# Flow Forge API

对照 Dify 的 Workflow 学习向后端（Flask + Pydantic + SQLite）。

## 环境

需要 Python **3.12+** 与 [uv](https://docs.astral.sh/uv/)。

```bash
cd api
uv sync
uv run pytest
```

## 启动

```bash
cd api
uv run flask --app flow_forge.app:create_app run --debug
```

探活：`GET http://127.0.0.1:5000/health` → `{"status":"ok"}`。

## 最小工作流示例

图约定（与 Dify draft **字段子集**接近）：

- 节点：`id` + `data.type`（`start` / `template` / `end`）
- `template` 节点：`data.template` 使用 Python `str.format` 占位符，如 `{name}`
- 边：`source` / `target`

模板占位符来自运行 `inputs` 以及上游写入的变量（当前 slice 会把模板结果放进 `text`）。

### 1. 创建工作流

```bash
curl -s -X POST http://127.0.0.1:5000/workflows ^
  -H "Content-Type: application/json" ^
  -d "{\"graph\":{\"nodes\":[{\"id\":\"start_1\",\"data\":{\"type\":\"start\"}},{\"id\":\"tpl_1\",\"data\":{\"type\":\"template\",\"template\":\"Hello, {name}!\"}},{\"id\":\"end_1\",\"data\":{\"type\":\"end\"}}],\"edges\":[{\"id\":\"e1\",\"source\":\"start_1\",\"target\":\"tpl_1\"},{\"id\":\"e2\",\"source\":\"tpl_1\",\"target\":\"end_1\"}]}}"
```

记下返回的 `id`（下文记为 `WORKFLOW_ID`）。

### 2. 启动一次运行（同步）

```bash
curl -s -X POST http://127.0.0.1:5000/workflows/WORKFLOW_ID/runs ^
  -H "Content-Type: application/json" ^
  -d "{\"inputs\":{\"name\":\"Forge\"}}"
```

响应含 `id`（`run_id`）、`status`、`outputs`（成功时类似 `{"text":"Hello, Forge!"}`）。

### 3. 查询运行与事件

```bash
curl -s http://127.0.0.1:5000/runs/RUN_ID
curl -s http://127.0.0.1:5000/runs/RUN_ID/events
```

> Windows CMD 使用 `^` 续行；PowerShell 可用 `` ` `` 或改成单行。Git Bash / macOS / Linux 把 `^` 换成 `\`。

## 接口一览

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/health` | 探活 |
| POST | `/workflows` | 创建工作流（body: `{ "graph": ... }`） |
| GET | `/workflows/<id>` | 读取工作流 |
| POST | `/workflows/<id>/runs` | 同步启动运行（body: `{ "inputs": {...} }`） |
| GET | `/runs/<run_id>` | 运行详情 |
| GET | `/runs/<run_id>/events` | 逐步事件（可轮询） |
