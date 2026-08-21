"""Workflow graph schema (Dify draft field subset)."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator

SupportedNodeType = Literal["start", "template", "end"]


class NodeData(BaseModel):
    type: SupportedNodeType
    template: str | None = None

    @model_validator(mode="after")
    def template_required_for_template_node(self) -> NodeData:
        if self.type == "template" and not self.template:
            raise ValueError("template node requires data.template")
        return self


class GraphNode(BaseModel):
    id: str
    data: NodeData


class GraphEdge(BaseModel):
    id: str | None = None
    source: str
    target: str


class WorkflowGraph(BaseModel):
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
    return WorkflowGraph.model_validate(payload)
