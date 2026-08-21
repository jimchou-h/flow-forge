# 对照 Dify 搭学习仓：先让后端能跑起来

> 示例仓库：[flow-forge](https://github.com/jimchou-h/flow-forge)
>
> 本篇讲：这个学习项目**现在能做什么**——装依赖、起服务、探活、确认数据库能连上。读者可以几乎不读 Python；重点是每块功能解决什么问题，以及目录为什么那样摆。

---

## 先说结论

Flow Forge 要对齐的是 Dify 一类产品里的 **Workflow（工作流）**：把多步处理画成一张图再执行。  
但「图怎么跑」之前，仓库必须先具备三件很土、却绕不开的能力：

| 能力 | 用户能感知到什么 |
|------|------------------|
| 依赖可安装 | 别人机器上也能装齐同样的库 |
| 服务可启动 | 浏览器或 `curl` 能打到一个地址 |
| 存储可接通 | 以后保存「跑过一次工作流」有地方落 |

> **一句话：本篇只证明「后端壳子活着」；工作流本身下一篇再讲。**

---

## 1. 这个项目要解决什么问题？

对照 Dify 学习，最容易踩的坑是：一上来对着庞大源码找「智能」相关文件，结果卡在——

- 依赖装不上 / 版本对不上  
- 不知道从哪个命令启动  
- 业务代码和「收 HTTP 请求」的代码糊在一起，越改越乱  

所以 Flow Forge 后端先提供一个**最小可用服务**：不跑工作流，只回答「我还活着」，并把以后要用的分层位置留好。

仓库大致分成：

| 目录 | 功能角色 |
|------|----------|
| `api/` | 后端：现在的主角 |
| `web/` | 前端：以后再做，现在只有说明占位 |
| `docs/blog/` | 本系列文章 |

你只需要关心：`api/` 能不能在你电脑上按文档跑通。

---

## 2. 功能一：把「需要哪些库」说清楚，并一键装好

Python 项目常靠一个清单文件声明依赖（本仓是 `api/pyproject.toml`）。里面写明了：

- 语言版本：至少 **Python 3.12**  
- 跑服务用：**Flask**（提供 HTTP 接口）  
- 以后校验请求数据用：**Pydantic**（本篇几乎还没上场）  
- 访问数据库用：**SQLAlchemy**  
- 跑测试用：**pytest**

装依赖我们用 **uv**（一个专门管 Python 项目环境的工具）：

| 命令 | 功能 |
|------|------|
| `uv sync` | 按清单把库装进本项目的独立环境（不污染你电脑全局 Python） |
| `uv run …` | 在这个环境里执行后面的命令 |

跟跑：

```bash
cd api
uv sync
```

装完，你就有了一个「可复现的后端环境」。这和有没有工作流无关，但没有它，后面什么都演示不了。

---

## 3. 功能二：起一个 HTTP 服务，并提供「探活」接口

**探活（health check）**：客户端访问一个固定地址，服务若正常就返回简单成功信息。部署、本地调试都会先打这个口，确认进程真的起来了。

本仓约定：

- 地址：`GET /health`  
- 成功时：HTTP 状态码 `200`，正文大致是 `{"status":"ok"}`

启动（在 `api/` 目录）：

```bash
uv run flask --app flow_forge.app:create_app run --debug
```

然后：

```bash
curl http://127.0.0.1:5000/health
```

看到 `ok`，就说明：**Web 服务进程在、路由挂上了。**

---

## 4. 功能三：为什么目录要分成 controllers / services / core？

这不是为了「目录好看」，而是为了和 Dify 后端常见读法对齐，并限制「改功能时该动哪一层」：

| 层 | 管什么 | 现在有什么 |
|----|--------|------------|
| **controllers** | 对外：收 HTTP、回状态码和 JSON | 已有 `/health` |
| **services** | 编排：把多个步骤串起来 | 先留空位 |
| **core** | 领域：工作流图、节点、执行规则等 | 先留空位 |

可以把它想成流水线：

```text
浏览器 / curl
    → controllers（门口接待）
        → services（前台办事，以后）
            → core（核心业务规则，以后）
                → 数据库
```

今天只有「门口接待」有活干：有人问健康状况，门口直接回答，不必进核心车间。  
等工作流做出来，新逻辑应主要长在 `core` / `services`，而不是把执行器全写进路由文件——否则以后对照 Dify 源码时，两边的「职责地图」对不上。

组装关系（用白话读，不必抠语法）：

1. 有一个叫「创建应用」的入口函数，负责：连一下数据库、挂上路由、交出可运行的服务对象。  
2. `/health` 路由单独放在 controllers 里，由入口挂载上去。  
3. 测试也走同一套入口：在测试里「假启动」一下服务，请求 `/health`，断言返回 `ok`。

对应源码位置（想对照时再点开即可）：

- 组装入口：[`api/src/flow_forge/app.py`](https://github.com/jimchou-h/flow-forge/blob/main/api/src/flow_forge/app.py)  
- 探活接口：[`api/src/flow_forge/controllers/health.py`](https://github.com/jimchou-h/flow-forge/blob/main/api/src/flow_forge/controllers/health.py)

---

## 5. 功能四：数据库先「能连上」，不先建业务表

工作流跑起来之后，至少要存：某次运行的结果、每一步的状态。那需要数据库。

本仓第一阶段用 **SQLite**：一个本地文件型数据库，不必先装 Postgres。  
现在实现的功能只有：

- 默认在约定目录准备好数据库文件路径  
- 启动时执行一次极简查询（相当于问数据库「你在吗」）  
- 若成功，把连接能力挂在应用上，供以后使用  

**还没有**「工作流表」「运行记录表」——那些属于工作流功能本身。  
本篇只保证：存储这条线没有断。

源码：[`api/src/flow_forge/db.py`](https://github.com/jimchou-h/flow-forge/blob/main/api/src/flow_forge/db.py)

---

## 6. 你怎么确认「这些功能都好了」？

不必读测试代码，只要在 `api/` 执行：

```bash
uv run pytest
```

全部通过，通常意味着：

| 检查项 | 对应功能 |
|--------|----------|
| 分层目录可被正确加载 | 项目结构没装错 |
| `/health` 返回成功 | 探活可用 |
| 数据库能执行探测查询 | 存储入口可用 |

根目录 [`README.md`](https://github.com/jimchou-h/flow-forge/blob/main/README.md) 把安装、测试、启动写在一起，按它跟跑即可。

前端 `web/` 目前**没有**可点的页面，这是刻意的：本篇功能边界停在后端壳子，避免「还没懂探活，又要先学一整套前端工程」。

---

## 下一篇会补哪块功能？

有了「能装、能起、能探活、能连库」，下一篇才谈工作流真正的产品能力，例如：

- 用一份图描述「开始 → 模板拼接 → 结束」  
- 触发一次运行，拿到输出  
- 把每一步状态记下来，方便以后回看  

那些才是对照 Dify Workflow 时最该对齐的功能面。

---

## 你可以从这里带走什么？

1. 学习大型项目，可以先对齐「能跑的最小功能面」，再对齐复杂业务。  
2. **探活接口**是后端是否活着的统一信号，和业务聪明与否无关。  
3. **controllers / services / core** 是职责地图，不是装饰；今天空着的层是为明天的工作流留位。  
4. **uv** 解决的是「依赖与命令可复现」，值得当作 Python 项目的默认门牌。  
5. 数据库可以先验证连通，业务表跟功能一起长，不必空建一堆表。

---

## 仓库链接

- **GitHub**：[https://github.com/jimchou-h/flow-forge](https://github.com/jimchou-h/flow-forge)
- **跟跑说明**：[README.md](https://github.com/jimchou-h/flow-forge/blob/main/README.md)
- **探活**：[controllers/health.py](https://github.com/jimchou-h/flow-forge/blob/main/api/src/flow_forge/controllers/health.py)
- **启动组装**：[app.py](https://github.com/jimchou-h/flow-forge/blob/main/api/src/flow_forge/app.py)
- **数据库入口**：[db.py](https://github.com/jimchou-h/flow-forge/blob/main/api/src/flow_forge/db.py)

欢迎 Star、Issue 和 PR。

---

_本文只覆盖 Flow Forge 后端「能装、能起、能探活、能连库」四块功能，不包含工作流执行。_
