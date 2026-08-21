## Purpose
约定浏览器如何访问 Flow Forge API：基址配置、开发期跨域或代理，以及调用失败时的可读错误，保证联调页不依赖手写 curl。

## ADDED Requirements

### Requirement: API 基址可配置
Web 应用 SHALL 通过环境变量或等价配置指定后端 API 基址，且文档 MUST 给出本地默认示例。

#### Scenario: 配置缺失有明确提示
- **WHEN** 未配置可用的 API 基址且页面尝试调用后端
- **THEN** 用户 MUST 看到明确的配置/连接错误提示（而非空白失败）

### Requirement: 浏览器可成功调用本地 API
开发环境下，浏览器 MUST 能对本地 Flask API 完成创建工作流与启动运行（通过 CORS 或 Next 反向代理等任一方案）。

#### Scenario: 健康或业务调用可达
- **WHEN** 后端已启动且 Web 配置正确
- **THEN** 联调页发起的工作流相关请求 MUST 能到达后端并返回 JSON 结果或后端错误体
