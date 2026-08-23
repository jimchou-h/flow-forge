## Purpose
将联调页主交互从纯 JSON 编辑升级为画布编排，同时保留可调试的图载荷可见性。

## MODIFIED Requirements

### Requirement: 联调页可提交图并启动运行
联调页 SHALL 允许用户通过画布（主路径）或等价方式得到最小工作流图与 inputs，并触发创建工作流与启动运行。

#### Scenario: 成功跑通最小图
- **WHEN** 用户使用画布上的 start→template→end 示例（或文档示例）并提供模板所需 inputs 后点击运行
- **THEN** 页面 MUST 展示成功的 run 状态与最终 outputs（或等价可读展示）

### Requirement: 页面展示逐步事件
联调页 SHALL 在运行结束后展示该 `run_id` 的事件列表（至少包含节点开始/成功或失败信息）。

#### Scenario: 失败运行也可复盘
- **WHEN** 用户故意缺少模板变量导致运行失败
- **THEN** 页面 MUST 显示 failed 状态，并 MUST 展示含失败信息的事件（或 error 字段）
