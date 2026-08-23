# web/ — Flow Forge 联调前端

Next.js（App Router + TypeScript）联调台：**拖拽画布**编排工作流 → 运行 → 看 events。  
浏览器请求走同源 `/api-proxy/*`，由 Next rewrite 转发到本地 Flask，避免 CORS。

## 要求

- Node.js 20+（推荐与本机已装的 LTS 一致）
- 包管理：`pnpm`（本仓 `packageManager` 已钉版本）

## 安装与启动

先起后端（另开终端）：

```bash
cd api
uv sync
uv run flask --app flow_forge.app:create_app run --debug
```

默认 API：`http://127.0.0.1:5000`。

再起前端：

```bash
cd web
pnpm install
pnpm dev
```

浏览器打开：http://localhost:3000

若 Flask 不在 5000 端口，启动 Next 前设置：

```bash
# PowerShell
$env:FLOW_FORGE_API_ORIGIN="http://127.0.0.1:5000"
pnpm dev
```

## 联调页用法（画布）

1. 中间画布默认加载 `start → template → end` 示例（可拖拽节点、从锚点拉线）
2. 左侧「添加节点」可加 `template` / `code` / `llm` / `if-else` / `end`
3. 选中节点后在右侧编辑 `data`（template / code / prompt / condition）
4. `if-else` 请从右侧 **true / false** 锚点分别连出两条边
5. 左侧编辑 `inputs` JSON，点「从画布运行（SSE）」：`POST /workflows` → `POST .../runs/stream`，边收节点事件边高亮画布（running / succeeded / failed）
6. 同步 JSON 路径 `POST .../runs` 仍可用（见 `lib/api.ts` 的 `runGraphOnce`），联调页默认走 SSE
7. 可选「显示 JSON」查看/粘贴图载荷，并用「从 JSON 加载到画布」显式同步

## 构建检查

```bash
cd web
pnpm build
pnpm exec tsx lib/graph-codec.smoke.ts
```

## 目录要点

| 路径 | 作用 |
|------|------|
| `app/page.tsx` | 联调页入口 |
| `components/workflow-editor.tsx` | 画布 + 面板 + 运行 |
| `components/workflow-node.tsx` | 自定义节点（含 if-else handles） |
| `lib/graph-codec.ts` | 画布 ↔ `WorkflowGraph` 编解码 |
| `lib/api.ts` | `/api-proxy` fetch 封装 |
| `lib/sample.ts` | 示例图与 inputs |
| `next.config.ts` | rewrite 代理到 Flask |
