## Context

当前 `POST .../runs` 同步执行完整张图后返回 JSON；events 需再 `GET .../events`。本 change 在**同一同步执行**中用 SSE 边执行边推送，避免引入 Celery。

## Goals / Non-Goals

**目标：**

- 流式端点：执行中推送节点事件，最后推送 `run_finished`（含 status / outputs / error / run_id）
- Runner 支持 `on_event` 回调（或 generator），与落库顺序一致
- 非流式 `POST .../runs` 回归不变
- Web：消费 SSE，高亮当前节点；结束后展示结果
- pytest：流式客户端读到有序事件；失败路径可观测

**非目标：**

- Celery / 多 worker
- LLM 内部 token stream（仅工作流节点级事件）
- EventSource 断线自动续传到任意历史 offset（本 slice 单次连接跟完一次 run）

## Decisions

1. **端点形态**  
   独立 `POST /workflows/<workflow_id>/runs/stream`，响应 `text/event-stream`；body 仍 `{ "inputs": {} }`。避免破坏现有 JSON 客户端。

2. **SSE 载荷**  
   每条 `data:` 为 JSON，至少含 `type`：  
   - 节点事件：与库中 `event_type` / `node_id` / `sequence` / `payload` 对齐  
   - `run_finished`：`status`、`run_id`、`outputs`、`error`

3. **执行模型**  
   仍在请求线程内跑 Runner；每写一条 `WorkflowRunEvent` 就 `yield` 给 SSE。连接断开时可中止后续节点（尽力而为）。

4. **前端**  
   `fetch` + `ReadableStream` 解析 SSE（比 EventSource 更易 POST）；画布节点 CSS 标记 `running` / `succeeded` / `failed`。

## Risks / Trade-offs

- [代理缓冲 SSE] → 文档注明禁用缓冲；dev proxy 已是本地  
- [长请求超时] → 学习向可接受；README 提示  

## Open Questions

- 无（独立 `/runs/stream` 路径；节点级事件 only）
