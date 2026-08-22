## Context

Template 节点只能做字符串插值。Dify 有 Code 节点做任意（受控）逻辑。本 change 在现有 Runner 上增加 `code` 类型。动机见 `proposal.md`。

## Goals / Non-Goals

**目标：**

- `data.type: "code"` + `data.code` 校验与执行
- 输入：当前变量 dict；输出：约定写入 `result`（并同步到 `text` 若为 str，便于接现有 end）
- 失败进 events / run.error
- 测试：unit + 一条 HTTP 主路径（可选）

**非目标：**

- Docker / gVisor 级沙箱
- 多语言（只 Python）
- 长时间任务、异步 code
- Web 大改（可只更新示例 JSON）

## Decisions

1. **执行模型：`exec` + 受控 globals/locals**  
   提供有限 builtins（如 `len`、`str`、`int`、基本运算）；默认不开放 `open`、`__import__`、网络库。  
   代码约定：用户赋值 `result = ...`（文档与示例写清）。

2. **限制**  
   - 源码最大长度（如 4KB）  
   - 简单超时（线程 + join timeout，学习向可接受；注明非强隔离）  
   - 禁止的名字在静态检查中拒绝（可选增强）

3. **图位置**  
   典型路径：`start → code → end` 或 `start → template → code → end`。

4. **分层**  
   执行逻辑放 `core/workflow/nodes/code.py`（或 `runner` 内分支先实现，再抽模块）；校验扩展 `graph.py` 的 `SupportedNodeType`。

## Risks / Trade-offs

- [误以为已有真沙箱] → README/注释写明「学习向受控命名空间，非生产隔离」  
- [超时实现脆弱] → 本 slice 可先做长度限制 + 禁用 import，超时作后续增强  

## Open Questions

- 无（输出键名固定为 `result`，字符串时兼写 `text`）
