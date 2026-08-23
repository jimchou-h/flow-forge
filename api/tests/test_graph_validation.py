"""Graph validation behaviour."""

import pytest
from pydantic import ValidationError

from flow_forge.core.workflow.graph import validate_workflow_graph
from flow_forge.core.workflow.nodes.code import MAX_CODE_LENGTH
from flow_forge.core.workflow.nodes.if_else import MAX_CONDITION_LENGTH
from flow_forge.core.workflow.nodes.llm import MAX_PROMPT_LENGTH
from sample_data import (
    sample_code_graph,
    sample_graph,
    sample_if_else_graph,
    sample_llm_graph,
    sample_parallel_graph,
)


def test_valid_start_template_end_graph_parses() -> None:
    graph = validate_workflow_graph(sample_graph())
    assert len(graph.nodes) == 3
    assert len(graph.edges) == 2


def test_valid_code_graph_parses() -> None:
    graph = validate_workflow_graph(sample_code_graph())
    assert len(graph.nodes) == 3
    assert graph.nodes[1].data.type == "code"


def test_valid_llm_graph_parses() -> None:
    graph = validate_workflow_graph(sample_llm_graph())
    assert len(graph.nodes) == 3
    assert graph.nodes[1].data.type == "llm"


def test_valid_if_else_graph_parses() -> None:
    graph = validate_workflow_graph(sample_if_else_graph())
    assert any(node.data.type == "if-else" for node in graph.nodes)
    handles = {
        edge.source_handle
        for edge in graph.edges
        if edge.source == "if_1"
    }
    assert handles == {"true", "false"}


def test_if_else_missing_condition_is_rejected() -> None:
    payload = sample_if_else_graph()
    del payload["nodes"][1]["data"]["condition"]
    with pytest.raises(ValidationError):
        validate_workflow_graph(payload)


def test_if_else_condition_too_long_is_rejected() -> None:
    payload = sample_if_else_graph(condition="result = True\n" + ("# x\n" * MAX_CONDITION_LENGTH))
    with pytest.raises(ValidationError):
        validate_workflow_graph(payload)


def test_if_else_missing_false_edge_is_rejected() -> None:
    payload = sample_if_else_graph()
    payload["edges"] = [
        edge for edge in payload["edges"] if edge.get("source_handle") != "false"
    ]
    with pytest.raises(ValidationError):
        validate_workflow_graph(payload)


def test_llm_node_missing_prompt_is_rejected() -> None:
    payload = sample_llm_graph()
    del payload["nodes"][1]["data"]["prompt"]
    with pytest.raises(ValidationError):
        validate_workflow_graph(payload)


def test_llm_node_too_long_is_rejected() -> None:
    payload = sample_llm_graph(prompt="x" * (MAX_PROMPT_LENGTH + 1))
    with pytest.raises(ValidationError):
        validate_workflow_graph(payload)


def test_code_node_missing_code_is_rejected() -> None:
    payload = sample_code_graph()
    del payload["nodes"][1]["data"]["code"]
    with pytest.raises(ValidationError):
        validate_workflow_graph(payload)


def test_code_node_too_long_is_rejected() -> None:
    payload = sample_code_graph(code="result = 1\n" + ("# x\n" * (MAX_CODE_LENGTH // 4)))
    with pytest.raises(ValidationError):
        validate_workflow_graph(payload)


def test_code_node_forbidden_import_is_rejected() -> None:
    payload = sample_code_graph(code="import os\nresult = 1")
    with pytest.raises(ValidationError):
        validate_workflow_graph(payload)


def test_edge_missing_target_is_rejected() -> None:
    payload = sample_graph()
    del payload["edges"][0]["target"]
    with pytest.raises(ValidationError):
        validate_workflow_graph(payload)


def test_unknown_node_type_is_rejected() -> None:
    payload = sample_graph()
    payload["nodes"][1]["data"]["type"] = "tool"
    with pytest.raises(ValidationError):
        validate_workflow_graph(payload)


def test_valid_parallel_graph_parses() -> None:
    graph = validate_workflow_graph(sample_parallel_graph())
    start_outs = [edge for edge in graph.edges if edge.source == "start_1"]
    assert len(start_outs) == 2
    assert all(edge.source_handle is None for edge in start_outs)


def test_non_if_else_out_edge_with_handle_is_rejected() -> None:
    payload = sample_parallel_graph()
    payload["edges"][0]["source_handle"] = "true"
    with pytest.raises(ValidationError):
        validate_workflow_graph(payload)
