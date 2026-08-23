"""工作流图结构（对照 Dify draft 的字段子集）。

约定：
- 节点用 ``id`` + ``data.type`` 区分类型（start / template / code / llm / if-else / end）
- 边用 ``source`` / ``target``；if-else 出边用 ``source_handle``（true/false）
不追求能直接导入完整 Dify 导出文件，只锁本仓用到的字段。
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator

from flow_forge.core.workflow.nodes.code import validate_code_source
from flow_forge.core.workflow.nodes.if_else import validate_condition_source
from flow_forge.core.workflow.nodes.llm import validate_llm_prompt

# 本阶段允许的节点类型
SupportedNodeType = Literal["start", "template", "code", "llm", "if-else", "end"]
SourceHandle = Literal["true", "false"]


class NodeData(BaseModel):
    """节点业务配置，放在 graph node 的 data 字段里（贴近 Dify 习惯）。"""

    type: SupportedNodeType
    template: str | None = None
    code: str | None = None
    prompt: str | None = None
    condition: str | None = None

    @model_validator(mode="after")
    def required_fields_for_node_type(self) -> NodeData:
        if self.type == "template" and not self.template:
            raise ValueError("template node requires data.template")
        if self.type == "code":
            validate_code_source(self.code or "")
        if self.type == "llm":
            validate_llm_prompt(self.prompt)
        if self.type == "if-else":
            validate_condition_source(self.condition)
        return self


class GraphNode(BaseModel):
    """图上的一个节点。"""

    id: str
    data: NodeData


class GraphEdge(BaseModel):
    """有向边；if-else 出边用 source_handle 区分真/假支。"""

    id: str | None = None
    source: str
    target: str
    source_handle: SourceHandle | None = None


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

    @model_validator(mode="after")
    def if_else_out_edges_are_paired(self) -> WorkflowGraph:
        for node in self.nodes:
            if node.data.type != "if-else":
                continue
            outs = [edge for edge in self.edges if edge.source == node.id]
            handles = {edge.source_handle for edge in outs}
            if len(outs) != 2 or handles != {"true", "false"}:
                raise ValueError(
                    f"if-else node {node.id} must have exactly true and false out-edges"
                )
        return self

    @model_validator(mode="after")
    def source_handle_only_on_if_else(self) -> WorkflowGraph:
        node_type = {node.id: node.data.type for node in self.nodes}
        for edge in self.edges:
            if edge.source_handle is None:
                continue
            if node_type.get(edge.source) != "if-else":
                raise ValueError("source_handle is only allowed on if-else out-edges")
        return self


def validate_workflow_graph(payload: dict[str, Any]) -> WorkflowGraph:
    """把原始 dict 校验成 WorkflowGraph；失败时抛出 Pydantic ValidationError。"""

    return WorkflowGraph.model_validate(payload)
