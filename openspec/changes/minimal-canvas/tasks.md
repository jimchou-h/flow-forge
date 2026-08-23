## 1. 画布骨架

- [ ] 1.1 引入 `@xyflow/react`，client 画布组件渲染示例图；拖拽移动节点
- [ ] 1.2 支持连线增边；序列化 `toWorkflowGraph`（含 if-else `source_handle`）

## 2. 编辑与运行

- [ ] 2.1 节点面板：添加类型；选中侧栏编辑 data；删除节点（保护唯一 start）
- [ ] 2.2 从画布一键运行 + 展示 run/events；inputs 编辑保留
- [ ] 2.3（可选）只读/可加载 JSON 面板防漂移

## 3. 文档与构建

- [ ] 3.1 更新 web README / CONTEXT；说明画布用法
- [ ] 3.2 `pnpm build` 通过；必要的序列化单测或手测清单写进 tasks 备注
