# workflow-http-api Specification

## Purpose
约定工作流相关 HTTP 接口：创建工作流、启动运行，以及用 `run_id` 作为稳定句柄查询运行状态与事件（支持轮询，不依赖推送流）。

## Requirements

### Requirement: 创建工作流接口
API SHALL 提供 HTTP 接口，接收 JSON 图正文以创建工作流，并返回其 id。

#### Scenario: 创建成功返回 id
- **WHEN** 客户端提交一份合法工作流图
- **THEN** 响应 MUST 表示成功，且 MUST 包含工作流 id

### Requirement: 启动运行接口返回 run_id
API SHALL 提供 HTTP 接口，按工作流 id 启动一次运行（可附带输入）。响应 MUST 包含 `run_id`；在同步执行已结束时，响应 MAY 附带最终输出。

#### Scenario: 启动运行返回 run_id
- **WHEN** 客户端对已存在的工作流启动一次运行
- **THEN** 响应 MUST 包含可用于后续查询的 `run_id`

### Requirement: 查询运行与事件接口
API SHALL 提供按 `run_id` 查询单次运行、以及查询该运行事件列表的 HTTP 接口，使客户端无需依赖推送流即可轮询。

#### Scenario: 轮询运行与事件
- **WHEN** 同步运行结束后，客户端按 `run_id` 分别请求运行详情与事件列表
- **THEN** 两个接口 MUST 返回已持久化的终态状态与事件列表
