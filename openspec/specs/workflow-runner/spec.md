# workflow-runner Specification

## Purpose
约定同步工作流执行：节点间变量传递、模板渲染，以及可持久化的 run 与逐步事件，便于日后升级为按 run_id 轮询而不改事件模型。

## Requirements

### Requirement: 同步运行跑完整张图
系统 SHALL 在启动运行的同一请求内同步执行整张图，按边的顺序从 start 走到 end，并 MUST 以终态结束（succeeded 或 failed）。

#### Scenario: start-template-end 成功
- **WHEN** 对一份合法的 start → template → end 图，在提供所需输入后启动运行
- **THEN** 该 run MUST 达到 succeeded，并暴露沿 end 路径得到的最终输出

### Requirement: Template 节点按变量渲染
template 节点 MUST 使用上游输出 / 运行输入中的变量，渲染其配置的模板字符串，并将结果写入运行变量空间供下游节点使用。

#### Scenario: 模板引用 start 输入
- **WHEN** start 提供某个输入字段，且模板引用该字段
- **THEN** template 节点输出 MUST 包含插值后的字符串

### Requirement: 按节点持久化运行事件
每次运行 MUST 持久化有序事件，至少记录节点开始与节点成功或失败；同步运行返回后，客户端 MUST 能按 `run_id` 查询这些事件。

#### Scenario: 运行结束后可拉取事件
- **WHEN** 一次运行成功结束
- **THEN** 按 `run_id` 拉取事件 MUST 返回覆盖每个已执行节点的记录

### Requirement: 失败可记录且进程保持健康
若某节点失败（例如模板引用了不存在的变量），该 run MUST 标记为 failed，失败事件 MUST 落库，且 HTTP API 进程 MUST 保持可用。

#### Scenario: 失败运行仍可查询
- **WHEN** 执行在 template 节点失败
- **THEN** 按 id 查询 run MUST 显示 failed，且事件列表 MUST 包含失败记录
