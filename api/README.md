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

- 节点：`id` + `data.type`（`start` / `template` / `code` / `llm` / `if-else` / `end`）
- `template` 节点：`data.template` 使用 Python `str.format` 占位符，如 `{name}`
- `code` 节点：`data.code` 为 Python 片段，**必须**赋值 `result = ...`；字符串结果会同步写入 `text` 供 `end` 输出
- `llm` 节点：`data.prompt` 同样支持 `{name}` 占位符；默认 **Stub** provider（`Echo: ...`），无需 API Key
- `if-else` 节点：`data.condition` 必须赋值 `result = <bool>`；出边带 `source_handle`: `true` / `false`（**互斥**选一支）
- **并行 fan-out**：非 if-else 节点可有多条**不带** `source_handle` 的出边；Runner **按边声明顺序同步执行**各支（学习向模拟，非多线程），入度 >1 的节点 join 后只跑一次
- 边：`source` / `target`；仅 if-else 出边使用 `source_handle`

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

### Code 节点示例（start → code → end）

> **安全说明**：本 slice 使用受控 `exec` 命名空间（禁用 `import` / `open` 等），仅供学习，**不是**生产级沙箱。

```bash
curl -s -X POST http://127.0.0.1:5000/workflows ^
  -H "Content-Type: application/json" ^
  -d "{\"graph\":{\"nodes\":[{\"id\":\"start_1\",\"data\":{\"type\":\"start\"}},{\"id\":\"code_1\",\"data\":{\"type\":\"code\",\"code\":\"result = name.upper()\"}},{\"id\":\"end_1\",\"data\":{\"type\":\"end\"}}],\"edges\":[{\"id\":\"e1\",\"source\":\"start_1\",\"target\":\"code_1\"},{\"id\":\"e2\",\"source\":\"code_1\",\"target\":\"end_1\"}]}}"
```

运行：`POST /workflows/<id>/runs`，body `{"inputs":{"name":"forge"}}` → 成功时 `outputs` 含 `{"text":"FORGE","result":"FORGE"}`。

源码上限 4KB；静态拒绝 `import`、`open(`、`__import__` 等模式。

### LLM 节点示例（start → llm → end）

> **默认行为**：未配置环境变量时使用 `StubLlmProvider`，输出形如 `Echo: <渲染后的 prompt>`。  
> 接真实模型时设置（三者缺一不可）：
> - `FLOW_FORGE_LLM_BASE_URL`（如 `https://api.openai.com/v1`）
> - `FLOW_FORGE_LLM_API_KEY`
> - `FLOW_FORGE_LLM_MODEL`

```bash
curl -s -X POST http://127.0.0.1:5000/workflows ^
  -H "Content-Type: application/json" ^
  -d "{\"graph\":{\"nodes\":[{\"id\":\"start_1\",\"data\":{\"type\":\"start\"}},{\"id\":\"llm_1\",\"data\":{\"type\":\"llm\",\"prompt\":\"Say hello to {name}\"}},{\"id\":\"end_1\",\"data\":{\"type\":\"end\"}}],\"edges\":[{\"id\":\"e1\",\"source\":\"start_1\",\"target\":\"llm_1\"},{\"id\":\"e2\",\"source\":\"llm_1\",\"target\":\"end_1\"}]}}"
```

运行：`POST /workflows/<id>/runs`，body `{"inputs":{"name":"Forge"}}` → stub 成功时 `outputs` 含 `{"text":"Echo: Say hello to Forge"}`。

### If/Else 节点示例（互斥分支）

> **不是并行**：条件为真只走 `source_handle: true` 的出边，为假只走 `false`；另一支上的节点不会执行。

条件写法与 Code 类似（受控命名空间），**必须** `result = <bool>`，例如 `result = score >= 60`。

典型结构：`start → if-else ─┬─(true)→ … → end`  
`                      └─(false)→ … → end`

运行：`{"inputs":{"score":80}}` → 走 true 支；`{"score":40}` → 走 false 支。

### 并行 fan-out / join（顺序模拟）

> **不是真并行**：多出边按 `edges` 数组顺序依次执行；汇合点等全部前驱成功后再跑一次。  
> 全局 `text` 可能被后执行的支路覆盖；汇合后请读 `{node_id}.text`（成功时 `outputs.branches` 会汇总）。

典型：`start ─┬→ tpl_a →┐`  
`        └→ tpl_b →┴→ end`

## 接口一览

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/health` | 探活 |
| POST | `/workflows` | 创建工作流（body: `{ "graph": ... }`） |
| GET | `/workflows/<id>` | 读取工作流 |
| POST | `/workflows/<id>/runs` | 同步启动运行（body: `{ "inputs": {...} }`），JSON 终态 |
| POST | `/workflows/<id>/runs/stream` | 同上，但以 **SSE**（`text/event-stream`）边跑边推节点事件，最后 `run_finished` |
| GET | `/runs/<run_id>` | 运行详情 |
| GET | `/runs/<run_id>/events` | 逐步事件（可轮询；与 SSE 落库同一套） |

### SSE 与 JSON 运行的差异

- **JSON** `POST .../runs`：等整图跑完再返回一次 `WorkflowRun`；可用 `GET .../events` 拉全量事件。
- **SSE** `POST .../runs/stream`：同一执行路径，但每落库一条节点事件就 `data: {...}\n\n` 推送；流末尾一条 `type: run_finished`（含 `run_id` / `status` / `outputs` / `error`）。
- 客户端须用 `fetch` + `ReadableStream`（POST body 带 `inputs`）；浏览器 `EventSource` 只支持 GET，不适用。
- 代理（nginx / Next rewrite）应对该路径关闭缓冲（响应头已带 `Cache-Control: no-cache`、`X-Accel-Buffering: no`）。
