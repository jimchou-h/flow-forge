"""工作流图结构（对照 Dify draft 的字段子集）。

约定：
- 节点用 ``id`` + ``data.type`` 区分类型（本阶段仅 start / template / end）
- 边用 ``source`` / ``target`` 指向节点 id
不追求能直接导入完整 Dify 导出文件，只锁本仓用到的字段。
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator

# 本阶段允许的节点类型；扩展 LLM/Code 时在此追加
SupportedNodeType = Literal["start", "template", "end"]


class NodeData(BaseModel):
    """节点业务配置，放在 graph node 的 data 字段里（贴近 Dify 习惯）。"""

    type: SupportedNodeType
    # 仅 template 节点需要；其它类型可省略
    template: str | None = None

    @model_validator(mode="after")
    def template_required_for_template_node(self) -> NodeData:
        if self.type == "template" and not self.template:
            raise ValueError("template node requires data.template")
        return self


class GraphNode(BaseModel):
    """图上的一个节点。"""

    id: str
    data: NodeData


class GraphEdge(BaseModel):
    """连接两个节点的有向边；并行出边本阶段不支持。"""

    id: str | None = None
    source: str
    target: str


class WorkflowGraph(BaseModel):
    """整张可执行图：节点列表 + 边列表。"""

    nodes: list[GraphNode] = Field(min_length=1)
    edges: list[GraphEdge] = Field(default_factory=list)

    @field_validator("nodes")
    @classmethod
    def unique_node_ids(cls, nodes: list[GraphNode]) -> list[GraphNode]:
        ids = [node.id for node in nodes]
        if len(ids) != len(set(ids)):
            raise ValueError("node ids must be unique")
        return nodes

    @model_validator(mode="after")
    def edges_reference_existing_nodes(self) -> WorkflowGraph:
        node_ids = {node.id for node in self.nodes}
        for edge in self.edges:
            if edge.source not in node_ids or edge.target not in node_ids:
                raise ValueError("edge endpoints must reference existing nodes")
        return self


def validate_workflow_graph(payload: dict[str, Any]) -> WorkflowGraph:
    """把原始 dict 校验成 WorkflowGraph；失败时抛出 Pydantic ValidationError。"""

    return WorkflowGraph.model_validate(payload)
