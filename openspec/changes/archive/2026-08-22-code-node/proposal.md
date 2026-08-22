## Why

已有 Start / Template / End 与 Web 联调，但仍缺少「可编程变换」节点。对照 Dify 的 Code 节点补上受控代码执行，才能演示比字符串模板更强的变量加工，并为后续 LLM/工具节点留出同类扩展模式。

## What Changes

- 图模型新增节点类型 `code`（字段仍走 `data.type` 子集约定）
- Runner 执行 code 节点：在受控环境中运行用户提供的短代码，读写工作流变量
- 明确安全边界：禁止任意文件系统/网络（本 slice 用受控命名空间 + 超时/长度限制；不做完整容器沙箱）
- 单测覆盖成功变换与失败（语法错、缺变量、超时等可实现子集）
- 联调页预填示例可带上 code 节点（可选，不强制大改 UI）
- **不**做：LLM 节点、完整 Docker 沙箱、拖拽画布、异步队列

## Capabilities

### New Capabilities

- `workflow-code-node`: code 节点的配置约定、受控执行与错误行为

### Modified Capabilities

- `workflow-graph`: 允许的节点类型增加 `code`
- `workflow-runner`: 调度循环支持执行 code 节点并写入变量/事件

## Impact

- 主要改动在 `api/src/flow_forge/core/workflow/`
- 可能微调 web 示例图；HTTP 契约形状不变（仍 create → run → events）
- 下一刀可考虑 LLM 节点或并行边，本 change 不包含
