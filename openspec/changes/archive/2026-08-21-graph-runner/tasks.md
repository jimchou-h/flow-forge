## 1. 图模型与存储

- [x] 1.1 定义 workflow 图的 Pydantic/校验规则（nodes/edges、start/template/end），并添加拒绝非法图的单测
- [x] 1.2 增加 SQLAlchemy 模型与建表（workflows），实现创建/按 id 读取，并添加持久化测试

## 2. 同步执行器

- [x] 2.1 在 `core/workflow` 实现 WorkflowRunner（按边调度、变量传递），start→end 空转路径单测通过
- [x] 2.2 实现 template 节点字符串插值，单测覆盖成功渲染与缺变量失败
- [x] 2.3 落库 workflow_runs 与逐步 events，单测覆盖成功 run 的事件序列

## 3. HTTP API

- [x] 3.1 实现 `POST/GET /workflows`（或等价路径），HTTP 测试覆盖创建与读取
- [x] 3.2 实现 `POST .../runs`、`GET /runs/<id>`、`GET /runs/<id>/events`，主路径 HTTP 测试：create → run → events 全绿

## 4. 文档与收尾

- [x] 4.1 更新 `api/README.md`（或根 README）补充最小示例图与 curl 流程，并跑全量 `uv run pytest` 确认通过
