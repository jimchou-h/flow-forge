# docs-scaffold Specification

## Purpose
约定学习向文档与仓库入口说明的落点，使后续博文与读者能找到项目约定；本能力不要求写出机制文正文，只要求目录与说明骨架就位。

## Requirements

### Requirement: 根 README 说明如何运行 API
仓库根目录 SHALL 包含 README，说明项目目的（对照 Dify 的 Workflow 学习向实现），以及安装并访问 API 健康检查的最小命令。

#### Scenario: README 含运行说明
- **WHEN** 新贡献者打开根 README
- **THEN** 其 MUST 能找到足以完成 `GET /health` 的安装/运行命令

### Requirement: Web 仅为占位且无 Next 应用
仓库 SHALL 包含 `web/` 目录及其 README，说明 Next.js 应用将在后续变更中加入；本能力 MUST NOT 交付可运行的 Next.js 应用。

#### Scenario: Web 仅为占位
- **WHEN** 贡献者在本能力完成后查看 `web/`
- **THEN** 其 MUST 看到说明文字，且 MUST NOT 被要求运行 `next` 才能完成骨架验收

### Requirement: 博文目录骨架
仓库 SHALL 提供 `docs/blog/` 骨架，包含本系列的 CSDN catalog 占位文件。

#### Scenario: catalog 占位存在
- **WHEN** 贡献者查找 Flow Forge 博文草稿应存放的位置
- **THEN** 其 MUST 找到 `docs/blog/` 以及可供后续条目填写的 catalog 占位文件
