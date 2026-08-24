## Purpose
扩展 Runner：调度循环可执行 http-request 节点。

## MODIFIED Requirements

### Requirement: 同步运行跑完整张图
系统 SHALL 在启动运行的同一请求内同步执行整张图（可含线性、if-else 互斥、无 handle 的 fan-out/join，以及 http-request），并 MUST 以终态结束（succeeded 或 failed）。

#### Scenario: start-template-end 成功
- **WHEN** 对一份合法的 start → template → end 图，在提供所需输入后启动运行
- **THEN** 该 run MUST 达到 succeeded，并暴露沿 end 路径得到的最终输出

#### Scenario: start-code-end 成功
- **WHEN** 对一份合法的 start → code → end 图提供所需输入并启动运行
- **THEN** 该 run MUST 达到 succeeded，并暴露反映 code 输出的最终结果

#### Scenario: start-llm-end 成功
- **WHEN** 对一份合法的 start → llm → end 图提供所需输入并启动运行（使用 stub 或已配置 provider）
- **THEN** 该 run MUST 达到 succeeded，并暴露 llm 生成的 `text` 作为最终输出

#### Scenario: if-else 真支成功
- **WHEN** 图含 if-else，条件为真，true 支可执行到 end
- **THEN** 该 run MUST 达到 succeeded，且仅 true 支上的中间节点产生成功事件

#### Scenario: fan-out join 成功
- **WHEN** 图含双支 fan-out 并汇合到 end，且两支均可成功
- **THEN** 该 run MUST 达到 succeeded，且 B、C、end 均出现成功事件，end 仅一次

#### Scenario: start-http-request-end 成功
- **WHEN** 对一份合法的 start → http-request → end 图启动运行（使用 stub 或已配置传输）
- **THEN** 该 run MUST 达到 succeeded，并暴露 http-request 写入的 `body`（或等价）作为最终输出可用字段
