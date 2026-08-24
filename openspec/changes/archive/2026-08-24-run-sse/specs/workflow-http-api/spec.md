## Purpose
扩展 HTTP API：增加工作流流式运行端点，与既有同步 JSON 运行并存。

## ADDED Requirements

### Requirement: 流式运行端点
系统 SHALL 暴露流式运行 HTTP 入口（如 `POST /workflows/<id>/runs/stream`），成功建立后响应 Content-Type MUST 为 `text/event-stream`（或等价 SSE）。

#### Scenario: 流式端点可调用
- **WHEN** 客户端对存在的 workflow 调用流式运行并提供合法 inputs
- **THEN** 响应 MUST 为 SSE 流，且包含至少一条节点事件与一条终态事件
