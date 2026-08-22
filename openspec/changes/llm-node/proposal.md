## Why

Code 节点解决了「可编程变换」，但 Workflow 北星仍缺「模型生成」一步。对照 Dify 的 LLM 节点，在现有 Runner 上增加 `llm` 类型，才能演示 start → template → llm → end 这类典型链路，并复用 Code 节点已验证的「新类型接入」模式。

## What Changes

- 图模型新增节点类型 `llm`（`data.prompt` 必填，支持变量插值）
- 引入可注入的 `LlmProvider` 抽象：测试用确定性 stub；可选通过环境变量接 OpenAI 兼容 HTTP API
- Runner 执行 llm 节点：渲染 prompt → 调用 provider → 将文本写入 `text`（及节点 scoped 变量）供下游 / end 使用
- 失败路径：provider 错误、缺变量、空 prompt → run failed + 事件
- 单测覆盖 stub 成功与失败；文档说明 env 与 stub 默认行为
- **不**做：流式 SSE、多模态、工具调用、模型路由 UI、拖拽画布

## Capabilities

### New Capabilities

- `workflow-llm-node`: llm 节点配置、provider 抽象与执行行为

### Modified Capabilities

- `workflow-graph`: 允许的节点类型增加 `llm`
- `workflow-runner`: 调度循环支持执行 llm 节点

## Impact

- 主要改动在 `api/src/flow_forge/core/workflow/`（新增 `nodes/llm.py` 或 `providers/`）
- HTTP 契约形状不变；Web 可增预填 llm 示例图（可选）
- 下一刀可考虑并行边、条件分支或画布，本 change 不包含
