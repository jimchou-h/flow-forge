## Context

`api-bootstrap` 已归档：Flask 应用工厂、SQLite 引擎、分层空包就位。本变更首次引入工作流域。动机见 `proposal.md`。

## Goals / Non-Goals

**目标：**

- 可持久化的最小图（start / template / end）与同步执行器
- 运行记录与事件落库；HTTP 以 `run_id` 作为轮询句柄
- 分层：校验与执行在 `core/workflow`，编排在 `services`，HTTP 在 `controllers`

**非目标：**

- SSE、后台队列、Celery
- Next 页面、画布
- LLM / Code / 并行分支 / 循环
- 账号与多租户

## Decisions

1. **图 JSON 与 Dify draft 字段子集兼容**  
   节点至少包含：`id`、类型字段（实现时钉死一种：`data.type` 或顶层 `type`，并写入 API 示例）、`data` 内的 template 配置；边包含 `source` / `target`（可选 `id`）。不追求能直接导入完整 Dify 导出文件。

2. **执行模型：请求内同步 + 事件先写库**  
   `WorkflowRunner.run(run_id)` 为唯一执行入口；控制器/服务层今天直接调用。日后改为入队时只替换调用方，不替换事件结构。

3. **变量模型：简单字典作用域**  
   start 输入写入变量表；template 读变量并写输出；end 收集输出。不做完整 Dify 变量选择器语法；模板先用简单字符串插值（如 `str.format_map`），并在 README 写明占位符规则。

4. **持久化：SQLAlchemy 模型 + SQLite**  
   表：`workflows`、`workflow_runs`、`workflow_run_events`（名称可微调）。学习向可在启动时 `create_all`；正式迁移可后置。

5. **HTTP 路径（建议）**  
   - `POST /workflows`  
   - `GET /workflows/<id>`  
   - `POST /workflows/<id>/runs`  
   - `GET /runs/<run_id>`  
   - `GET /runs/<run_id>/events`  
   请求与响应用 Pydantic 模型。

6. **错误处理**  
   校验失败 → 4xx；执行失败 → run 标记 failed。启动 run 的 HTTP 是返回 200/201（正文带 failed）还是 422，实现时选定一种并写进测试验收。

## Risks / Trade-offs

- [与 Dify 字段细节漂移] → 只锁定本切片用到的字段，示例图放进测试夹具  
- [模板注入 / 任意代码] → Template 仅做字符串插值，不执行代码  
- [同步阻塞] → 本切片节点极轻；文档标明日后异步升级路径  

## Open Questions

- 无（模板占位符规则在实现首票时用简单插值，并写入 API 示例即可）
