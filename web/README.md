# web/ — Flow Forge 联调前端

Next.js（App Router + TypeScript）极简控制台：编辑图 JSON → 运行 → 看 events。  
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

## 联调页用法

1. 左侧默认已预填 `start → template → end` 示例图（与 `api` 测试夹具同构）
2. 右侧 `inputs` 默认 `{"name":"Forge"}`
3. 点「运行」：内部依次 `POST /workflows` → `POST .../runs` → `GET .../events`
4. 下方查看 `status` / `outputs` / 事件列表；故意删掉 `name` 可观察失败路径

## 构建检查

```bash
cd web
pnpm build
```

## 目录要点

| 路径 | 作用 |
|------|------|
| `app/page.tsx` | 联调页（客户端组件） |
| `lib/api.ts` | `/api-proxy` fetch 封装 |
| `lib/sample.ts` | 示例图与 inputs |
| `next.config.ts` | rewrite 代理到 Flask |
