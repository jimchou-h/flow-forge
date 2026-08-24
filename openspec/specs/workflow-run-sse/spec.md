# workflow-run-sse Specification

## Purpose
TBD - created by archiving change run-sse. Update Purpose after archive.
## Requirements
### Requirement: 流式运行推送节点事件
系统 SHALL 提供流式运行入口；在执行每个节点开始/成功/失败时 MUST 向客户端推送对应 SSE 事件，顺序 MUST 与持久化事件一致。

#### Scenario: 线性图流式成功
- **WHEN** 客户端对流式入口提交合法 start→template→end 与所需 inputs
- **THEN** 流中 MUST 依次出现各节点的 started/succeeded（或等价），并以成功终态事件结束

### Requirement: 流式失败可观测
节点失败时，流 MUST 推送失败相关事件，并以 failed 终态结束；API 进程 MUST 保持可用。

#### Scenario: 缺变量导致流式失败
- **WHEN** template 引用不存在的变量且走流式运行
- **THEN** 客户端 MUST 能从流中读到失败信息与 failed 终态

### Requirement: 非流式路径保持兼容
既有同步 JSON `POST .../runs` MUST 继续返回完整终态，行为与本 change 前一致。

#### Scenario: JSON 运行仍成功
- **WHEN** 客户端使用原 JSON 运行接口跑通最小图
- **THEN** 响应 MUST 含 succeeded 与 outputs，且可不依赖 SSE

