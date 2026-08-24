## Why

引擎已覆盖变换（Template/Code）、生成（LLM）、控制流与画布可观测性，但仍缺「调用外部 HTTP」这一步。对照 Dify 的 HTTP 请求节点，补上学习向子集后，才能演示 start → http-request → end，并把变量插值接到真实（或可 stub）的出站调用上。

## What Changes

- 图模型新增节点类型 `http-request`（必填 `data.method` + `data.url`；可选 `headers` / `body`，支持变量插值）
- 引入可注入的 HTTP 传输抽象：测试用确定性 stub；默认可用真实 `httpx`（短超时），并做基础 SSRF 防护（禁非 http(s)、禁明显内网/元数据地址；学习向 allowlist 可配）
- Runner 执行该节点：渲染 URL/body → 发请求 → 将 `status_code`、`body`（文本）及节点 scoped 变量写入上下文；非 2xx 默认记为节点失败（可配置后续再扩）
- 画布：面板可添加并编辑 http-request；导出图后仍走现有 create → SSE/JSON 运行
- 单测：stub 成功/失败、非法 URL、图校验；文档说明 stub 与真实调用开关
- **不**做：完整 Dify HTTP 节点对等（鉴权面板、文件上传、二进制、重试策略 UI）、OAuth、异步队列、把响应体当 SSE 再推一层

## Capabilities

### New Capabilities

- `workflow-http-request-node`: http-request 节点配置、传输抽象与执行行为

### Modified Capabilities

- `workflow-graph`: 允许的节点类型增加 `http-request`
- `workflow-runner`: 调度循环支持执行 http-request 节点
- `web-canvas`: 画布可添加/编辑 http-request 节点

## Impact

- 主要改动：`api/.../nodes/`、`providers` 或 `http/` 传输、`runner.py`、图校验；`web` 节点面板与 codec
- HTTP 运行契约形状不变；新增依赖 `httpx`（若尚未引入）
- 下一刀可考虑草稿更新（PUT workflow）或 Iteration；本 change 不包含
