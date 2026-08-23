## Purpose
扩展同步执行器：在 if-else 节点按条件选择唯一后继，其它节点仍禁止多出边。

## MODIFIED Requirements

### Requirement: 同步运行跑完整张图
系统 SHALL 在启动运行的同一请求内同步执行整张图，按边从 start 走到 end（路径上可含 template、code、llm、if-else），并 MUST 以终态结束（succeeded 或 failed）。

#### Scenario: start-template-end 成功
- **WHEN** 对一份合法的 start → template → end 图，在提供所需输入后启动运行
- **THEN** 该 run MUST 达到 succeeded，并暴露沿 end 路径得到的最终输出

#### Scenario: start-code-end 成功
- **WHEN** 对一份合法的 start → code → end 图提供所需输入并启动运行
- **THEN** 该 run MUST 达到 succeeded，并暴露反映 code 输出的最终结果

#### Scenario: start-llm-end 成功
- **WHEN** 对一份合法的 start → llm → end 图提供所需输入并启动运行
- **THEN** 该 run MUST 达到 succeeded，并暴露 llm 生成的 `text`

#### Scenario: if-else 真支成功
- **WHEN** 图含 if-else，条件为真，true 支可执行到 end
- **THEN** 该 run MUST 达到 succeeded，且仅 true 支上的中间节点产生成功事件
