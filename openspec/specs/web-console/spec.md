# web-console Specification

## Purpose
约定 Flow Forge Web 控制台：用 Next.js 提供可跟跑的联调页，以画布编排为主、JSON 调试为辅，完成「编辑图 → 启动运行 → 查看终态与逐步事件」。

## Requirements

### Requirement: Next 应用可启动
仓库 `web/` SHALL 提供可安装、可启动的 Next.js 应用（App Router），开发命令 MUST 在文档中说明。

#### Scenario: 本地启动成功
- **WHEN** 开发者按文档在 `web/` 执行安装与开发启动命令
- **THEN** 应用 MUST 能在浏览器打开联调页（或明确的首页入口）

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
