## Context

Runner 已支持 template / code / llm / if-else 与 fan-out；Web 可画布编排并以 SSE 高亮。缺少对照 Dify 的「HTTP 请求」节点。LLM 侧已有 Provider 注入先例，本 change 用同样模式接入出站 HTTP。

## Goals / Non-Goals

**Goals:**

- 节点类型 `http-request`：method + url（必填），可选 headers / body；变量插值与现有模板规则一致
- 可注入传输：`StubHttpClient`（测试默认）与真实 `HttpxClient`（短超时 + 基础 SSRF 拒绝）
- 成功时写入 `status_code`、`body`（及 `{node_id}.*`）；HTTP 异常或非 2xx → 节点失败 → run failed
- 画布可添加/编辑；pytest 与 README 覆盖 stub / 真实切换

**Non-Goals:**

- 完整 Dify HTTP 节点 UI/鉴权/文件/分页
- 跟随重定向到任意内网、自定义证书、mTLS
- 把响应拆成 token/SSE 事件流
- Celery / 后台异步

## Decisions

1. **类型名 `http-request`**  
   对照 Dify 命名；图 JSON 用 `data.type: "http-request"`。

2. **传输抽象（对齐 LlmProvider）**  
   `HttpClient.request(method, url, headers, body) -> HttpResponse`。  
   应用工厂注入；测试注入 stub；生产/联调可用 httpx。避免 Runner 直接依赖网络。

3. **SSRF 学习向护栏**  
   仅允许 `http`/`https`；拒绝 `localhost`/`127.0.0.1`/`::1`、链路本地、明显云元数据主机（如 `169.254.169.254`）、非解析或私网段（RFC1918）——真实客户端默认开启；测试 stub 不校验。  
   可用环境变量 `FLOW_FORGE_HTTP_ALLOW_PRIVATE=1` 放宽（仅本地实验，文档警告）。

4. **失败语义**  
   网络错误、超时、SSRF 拒绝、状态码不在 200–299 → 节点失败（与 llm provider 异常一致）。本切片不做「把 4xx 当成功写 body」。

5. **方法白名单**  
   首期仅 `GET` / `POST`（大小写不敏感，规范化为大写）。

## Risks / Trade-offs

- [真实 HTTP 不稳定] → 默认测试走 stub；README 标明可选真实调用  
- [SSRF 护栏误伤内网演示] → 文档提供 `FLOW_FORGE_HTTP_ALLOW_PRIVATE`；默认安全  
- [响应过大] → 截断 body 至合理上限（如 64KiB），超出失败或截断并记日志（实现时钉死一种）

## Open Questions

- 无（方法仅 GET/POST；非 2xx 即失败；默认禁私网）
