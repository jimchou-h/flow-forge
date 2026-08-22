"""Graph validation behaviour."""

import pytest
from pydantic import ValidationError

from flow_forge.core.workflow.graph import validate_workflow_graph
from flow_forge.core.workflow.nodes.code import MAX_CODE_LENGTH
from flow_forge.core.workflow.nodes.llm import MAX_PROMPT_LENGTH
from sample_data import sample_code_graph, sample_graph, sample_llm_graph


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
