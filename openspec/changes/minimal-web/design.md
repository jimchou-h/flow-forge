## Context

`graph-runner` 已归档：REST 可创建图、同步 run、查 events。`web/` 目前仅占位 README。动机见 `proposal.md`。

## Goals / Non-Goals

**目标：**

- Next（App Router）最小可跑工程
- 单页联调：图 JSON + inputs → Run → 展示 status/outputs/events
- 浏览器能打到本地 `api/`（CORS 或 rewrite 代理二选一，推荐 **Next rewrites 代理** 减少浏览器 CORS 麻烦）

**非目标：**

- React Flow / 拖拽画布
- 登录、多租户、i18n 全量
- 服务端渲染复杂数据水合；本页以客户端交互为主即可
- 与 Dify Console UI 视觉对等

## Decisions

1. **框架：Next.js + TypeScript（对齐 Dify web 技术方向）**  
   包管理优先 pnpm（若本机无则 npm 亦可，README 写清一种）。

2. **联调页形态：单路由客户端页面**  
   例如 `app/page.tsx`：左侧/上方 JSON textarea（预填示例图），inputs 简单字段或 JSON；按钮「运行」；下方结果区。

3. **调用链**  
   浏览器 →（可选）`/api-proxy/*` rewrite → Flask `http://127.0.0.1:5000`。  
   若用 proxy：前端 fetch 相对路径 `/api-proxy/workflows` 等，避免 CORS。  
   Flask 侧若坚持直连，则加 flask-cors；**优先 proxy，少改后端**。

4. **运行 UX**  
   一次点击内：`POST /workflows` → 取 id → `POST /workflows/:id/runs` → `GET /runs/:id/events`（同步场景足够）。失败时展示 `status=failed` 与事件/error。

5. **测试**  
   优先：关键 fetch 封装或页面逻辑的轻量单测（若成本高，可用 Playwright 一条冒烟或文档手测 + 类型检查）。学习向最低：`pnpm build` 或 `next build` 通过 + README 跟跑。

## Risks / Trade-offs

- [Node 版本与包管理差异] → README 钉 Node LTS 与一种包管理器  
- [示例图与后端校验漂移] → 示例与 `api/README` / 测试夹具保持同构  
- [过早引入 UI 组件库] → 本 change 用原生 HTML/CSS 或极简样式即可  

## Open Questions

- 无（包管理器实现时选 pnpm，不可用再退 npm 并文档注明）
