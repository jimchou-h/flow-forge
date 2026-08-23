## Purpose
扩展同步执行器：支持 fan-out 多支路顺序执行与 join 汇合，同时保持 if-else 互斥语义不变。

## MODIFIED Requirements

### Requirement: 同步运行跑完整张图
系统 SHALL 在启动运行的同一请求内同步执行整张图（可含线性、if-else 互斥、以及无 handle 的 fan-out/join），并 MUST 以终态结束（succeeded 或 failed）。

#### Scenario: start-template-end 成功
- **WHEN** 对一份合法的 start → template → end 图启动运行
- **THEN** 该 run MUST 达到 succeeded

#### Scenario: if-else 真支成功
- **WHEN** 图含 if-else 且条件为真
- **THEN** 仅 true 支中间节点产生成功事件

#### Scenario: fan-out join 成功
- **WHEN** 图含双支 fan-out 并汇合到 end，且两支均可成功
- **THEN** 该 run MUST 达到 succeeded，且 B、C、end 均出现成功事件，end 仅一次
