## Purpose
扩展图校验：允许并校验 `http-request` 节点。

## MODIFIED Requirements

### Requirement: 本阶段支持的节点类型
系统 SHALL 接受可执行工作流中的节点类型 `start`、`template`、`end`、`code`、`llm`、`if-else`、`http-request`；对此外的未知节点类型 MUST 拒绝执行。`http-request` 节点 MUST 提供合法 `method`（GET/POST）与非空 `url`。

#### Scenario: 未知节点类型被拒绝
- **WHEN** 工作流图中出现上述以外的节点类型
- **THEN** 创建或运行 MUST 失败，并返回明确的客户端错误信息

#### Scenario: 含 code 的合法图可创建
- **WHEN** 客户端提交 start → code → end（或含 template）且 code 字段齐全的图
- **THEN** 系统 MUST 允许创建并持久化

#### Scenario: 含 llm 的合法图可创建
- **WHEN** 客户端提交 start → llm → end（或含 template/code）且 prompt 字段齐全的图
- **THEN** 系统 MUST 允许创建并持久化

#### Scenario: 含 if-else 的合法图可创建
- **WHEN** 客户端提交含 if-else、condition 齐全、且 true/false 出边成对的图
- **THEN** 系统 MUST 允许创建并持久化

#### Scenario: 含 fan-out 的合法图可创建
- **WHEN** 客户端提交 start 后接双出边汇合到 end 的图（无非法 handle）
- **THEN** 系统 MUST 允许创建并持久化

#### Scenario: 含 http-request 的合法图可创建
- **WHEN** 客户端提交 start → http-request → end 且 method/url 齐全的图
- **THEN** 系统 MUST 允许创建并持久化

#### Scenario: http-request 缺 url 被拒绝
- **WHEN** http-request 节点缺少非空 `url` 或 method 非法
- **THEN** 创建或运行 MUST 失败并返回客户端错误
