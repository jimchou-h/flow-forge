## Why

引擎侧已具备线性 / 互斥 / 并行语义，但 Web 仍靠手改 JSON 联调，学习成本高且难对照 Dify「画布上编排」的体验。补上一块**最小拖拽画布**，把已有节点类型可视化编辑并仍走现有 create→run→events API，才能闭环「看得见的工作流」。

## What Changes

- `web/` 引入画布库（推荐 `@xyflow/react`）：展示节点与边、拖拽移动、连线
- 节点面板：可添加 `template` / `code` / `llm` / `if-else` / `end`（`start` 默认已有且唯一）
- 选中节点可编辑 `data` 字段（template / code / prompt / condition）；if-else 连线可选 `source_handle`
- 画布状态可导出为现有 `WorkflowGraph` JSON，一键运行；保留简易 JSON 预览或折叠编辑作调试
- 布局：节点可带前端 `position`（仅 UI；提交 API 时剥离或后端忽略 extra）
- **不**做：完整 Dify 画布对等、协作、版本历史、自动布局算法、SSE 流式

## Capabilities

### New Capabilities

- `web-canvas`: 最小拖拽画布的编排与导出运行行为

### Modified Capabilities

- `web-console`: 联调页从「纯 JSON」升级为「画布为主、JSON 为辅」

## Impact

- 主要改动在 `web/`；`api/` 图校验契约不变（理想零后端改动）
- 依赖增加 `@xyflow/react`（及样式）
- 下一刀可考虑节点配置表单精修或 SSE，本 change 不包含
