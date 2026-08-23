## Context

Template / Code 均为确定性节点。Dify LLM 节点通过 prompt + 模型调用产生文本。本 change 在同步 Runner 上增加 `llm` 类型，优先保证可测与可联调，不追求完整模型生态。

## Goals / Non-Goals

**目标：**

- `data.type: "llm"` + `data.prompt`（Python `str.format` 风格占位符）
- `LlmProvider.complete(prompt) -> str` 抽象；默认 `StubLlmProvider`（确定性，如 `Echo: {prompt}` 或固定前缀）
- 可选 `OpenAiCompatibleProvider`：读 `FLOW_FORGE_LLM_BASE_URL` / `FLOW_FORGE_LLM_API_KEY` / `FLOW_FORGE_LLM_MODEL`
- 输出写入 `text` 与 `{node_id}.text`，与 template 节点下游约定一致
- 失败进 events / run.error

**非目标：**

- 流式 token、thinking、vision、function calling
- 模型管理后台、计费、重试策略矩阵
- 强制真实 API Key 才能跑测试

## Decisions

1. **Provider 注入**  
   `WorkflowRunner` 构造时接受可选 `llm_provider`；未传则用 stub。Flask app factory 从 env 选择 real provider（若配置齐全）。

2. **Prompt 渲染**  
   与 template 节点相同：对当前 variables 做 `format_map`，缺 key 即失败。

3. **图校验**  
   `llm` 节点 MUST 有非空 `data.prompt`；prompt 长度上限（如 8KB）与 code 类似。

4. **典型路径**  
   `start → llm → end` 或 `start → template → llm → end`。

5. **分层**  
   - `core/workflow/nodes/llm.py` — 渲染 + 调 provider  
   - `core/workflow/providers/` — stub 与 OpenAI 兼容实现（若本 slice 时间够）

## Risks / Trade-offs

- [Stub 与真实模型行为不一致] → README 写明默认 stub；env 配置段单独列出  
- [真实 API 拖慢 CI] → pytest 只用 stub；集成测 optional / 手动  

## Open Questions

- 无（输出键固定为 `text`，与 template/end 一致）
