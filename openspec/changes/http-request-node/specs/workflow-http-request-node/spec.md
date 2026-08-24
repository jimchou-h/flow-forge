## Purpose
约定 http-request 节点：按配置向外部发起 HTTP，并将状态码与响应体写入工作流变量（对照 Dify HTTP 请求节点的学习向子集）。

## ADDED Requirements

### Requirement: http-request 节点可配置并执行
系统 SHALL 支持节点类型 `http-request`；`data.method` MUST 为 `GET` 或 `POST`（大小写不敏感）；`data.url` MUST 为非空字符串且支持变量插值；MAY 提供 `headers` 对象与 `body` 字符串（同样支持插值）。

#### Scenario: GET 成功写入变量
- **WHEN** 图中含 start → http-request → end，传输返回 200 与正文，且 url/method 合法
- **THEN** run MUST 成功，且上下文 MUST 含 `status_code` 与 `body`（或节点 scoped 等价字段）供 end / 下游使用

### Requirement: 失败可观测
网络错误、超时、被 SSRF 策略拒绝、或响应状态码非 2xx 时，该节点 MUST 失败；run MUST 记为 failed 并产生失败事件；API 进程 MUST 保持可用。

#### Scenario: 非 2xx 导致 run 失败
- **WHEN** 传输返回状态码 500
- **THEN** run status MUST 为 failed，且 MUST 有对应节点失败事件

### Requirement: 可注入传输便于测试
系统 SHALL 通过可注入的 HTTP 传输执行实际请求；测试 MUST 能在不访问真实网络的情况下用确定性 stub 覆盖成功与失败路径。

#### Scenario: stub 成功路径
- **WHEN** 注入返回固定 200/`ok` 的 stub 并运行最小 http-request 图
- **THEN** run MUST succeeded，且 outputs 反映 stub 正文
