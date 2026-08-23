## Context

当前 `web/app/page.tsx` 是双 JSON textarea + Run。引擎已支持丰富图结构。本 change 用 React Flow（`@xyflow/react`）做学习向最小画布，SSOT 仍是可提交的 graph JSON。

## Goals / Non-Goals

**目标：**

- 画布渲染 nodes/edges；拖拽改位置；拖拽连线增边
- 添加/删除节点（保持恰好一个 start）
- 选中节点侧栏编辑类型相关字段
- if-else：两条出边可标 true/false handle（UI 上选 source handle）
- 「运行」：从画布序列化 → `runGraphOnce` → 展示 status / outputs / events
- 文档更新；`pnpm build` 通过

**非目标：**

- 美化到生产级设计系统、快捷键大全、小地图必做（小地图可选）
- 后端存 position、多人协同
- 替换全部 JSON 调试能力（可保留折叠 JSON）

## Decisions

1. **库：`@xyflow/react`**  
   与业界 workflow 画布常见选型一致，文档全；App Router 下用 client component 包裹。

2. **状态**  
   React state 持有 canvas nodes/edges；序列化函数 `toWorkflowGraph()` 生成 API 载荷（去掉 React Flow 私有字段）。

3. **position**  
   仅前端；不强制写入 API graph。若写入 `node.position`，后端须 ignore extra——优先序列化时剥离，零后端改动。

4. **if-else handles**  
   出边用 React Flow `sourceHandle` id `true`/`false`，映射为 API `source_handle`。

5. **验收**  
   手测：画 start→template→end、跑通；可选一条组件/序列化单测。最低：`pnpm build`。

## Risks / Trade-offs

- [画布状态与 JSON 双份漂移] → 运行前只从画布序列化；JSON 面板只读或「从 JSON 加载」显式动作  
- [包体积] → 可接受，学习向优先体验  

## Open Questions

- 无（默认用 `@xyflow/react`；无后端改动）
