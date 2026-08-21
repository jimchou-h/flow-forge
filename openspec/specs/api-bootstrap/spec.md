# api-bootstrap Specification

## Purpose
约定 Flow Forge 后端骨架的可观察行为：API 包可安装、可启动，暴露与 Dify 对齐的分层包名，提供健康检查，并在引入工作流域之前证明 SQLite 可连通。本能力不覆盖工作流图或执行。

## Requirements

### Requirement: 存在分层 API 包
仓库 SHALL 提供 `api/` 下的 Python 包布局，其中 `controllers`、`services`、`core` MUST 可作为可导入模块存在（除包标记外可以为空）。

#### Scenario: 必需包可导入
- **WHEN** 开发者按文档执行 API 包的导入冒烟检查
- **THEN** 导入 `controllers`、`services`、`core` MUST 成功且无错误

### Requirement: 健康检查接口
API SHALL 暴露用于表明进程存活的 HTTP 健康检查接口。

#### Scenario: 健康检查成功
- **WHEN** 客户端发送 `GET /health`
- **THEN** 响应状态码 MUST 为 `200`，且正文 MUST 表明健康状态

### Requirement: SQLite 连通冒烟
API SHALL 能够打开已配置的 SQLite 数据库文件，以支持后续持久化（本能力不要求工作流业务表）。

#### Scenario: 数据库可打开
- **WHEN** 应用按默认本地 SQLite 配置初始化
- **THEN** 连通检查 MUST 成功（例如执行极简查询或完成 engine 连接）

### Requirement: 自动化冒烟测试
API 工程 SHALL 包含覆盖健康检查与包导入冒烟的自动化测试。

#### Scenario: 冒烟测试通过
- **WHEN** 开发者执行文档中的 `api/` 测试命令
- **THEN** 骨架冒烟测试 MUST 全部通过
