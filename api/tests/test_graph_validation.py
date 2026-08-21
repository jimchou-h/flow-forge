"""Graph validation behaviour."""

import pytest
from pydantic import ValidationError

from flow_forge.core.workflow.graph import validate_workflow_graph
from sample_data import sample_graph


def test_valid_start_template_end_graph_parses() -> None:
    graph = validate_workflow_graph(sample_graph())
    assert len(graph.nodes) == 3
    assert len(graph.edges) == 2


def test_edge_missing_target_is_rejected() -> None:
    payload = sample_graph()
    del payload["edges"][0]["target"]
    with pytest.raises(ValidationError):
        validate_workflow_graph(payload)


def test_unknown_node_type_is_rejected() -> None:
    payload = sample_graph()
    payload["nodes"][1]["data"]["type"] = "llm"
    with pytest.raises(ValidationError):
        validate_workflow_graph(payload)
