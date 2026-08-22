## Purpose
扩展同步执行器：在按边调度时执行 code 节点，保持既有 run/events 模型与终态语义。

## MODIFIED Requirements

### Requirement: 同步运行跑完整张图
系统 SHALL 在启动运行的同一请求内同步执行整张图，按边的顺序从 start 走到 end（路径上可含 template 与 code），并 MUST 以终态结束（succeeded 或 failed）。

#### Scenario: start-template-end 成功
- **WHEN** 对一份合法的 start → template → end 图，在提供所需输入后启动运行
- **THEN** 该 run MUST 达到 succeeded，并暴露沿 end 路径得到的最终输出

#### Scenario: start-code-end 成功
- **WHEN** 对一份合法的 start → code → end 图提供所需输入并启动运行
- **THEN** 该 run MUST 达到 succeeded，并暴露反映 code 输出的最终结果
