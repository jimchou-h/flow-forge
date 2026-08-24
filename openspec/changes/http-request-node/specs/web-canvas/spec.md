## Purpose
画布支持添加与编辑 http-request 节点。

## MODIFIED Requirements

### Requirement: 添加与配置节点
用户 SHALL 能从面板添加受支持的节点类型（至少 template / code / llm / if-else / http-request / end），并 MUST 能编辑选中节点的关键 `data` 字段（http-request 至少含 method 与 url）。

#### Scenario: 添加 template 并编辑模板
- **WHEN** 用户添加 template 节点并填写 `data.template`
- **THEN** 导出的图 JSON MUST 包含该节点且 `data.type` 为 `template`

#### Scenario: 添加 http-request 并编辑 url
- **WHEN** 用户添加 http-request 节点并填写 `data.method` 与 `data.url`
- **THEN** 导出的图 JSON MUST 包含该节点且 `data.type` 为 `http-request`
