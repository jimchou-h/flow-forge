# AGENTS.md

Flow Forge 是对照 Dify 结构的学习向 Workflow 项目。规格与任务以 `openspec/` 为唯一 SSOT；开发走 unified-dev-workflow（竖切 issue + TDD）。

## Agent skills

### Issue tracker

Issues 使用 GitHub Issues（`gh` CLI）。See `docs/agents/issue-tracker.md`.

### Triage labels

使用默认五类 triage labels。See `docs/agents/triage-labels.md`.

### Domain docs

Single-context：根目录 `CONTEXT.md` + `docs/adr/`。See `docs/agents/domain.md`.

## Working agreements

- 进行中变更只在 `openspec/changes/<name>/`；不要平行维护第二套需求树
- Blog 草稿：`docs/blog/<slug>.md`；未发 CSDN 前不要编造 article id
- 对照 Dify 时对齐命名与职责边界，不追求功能对等
