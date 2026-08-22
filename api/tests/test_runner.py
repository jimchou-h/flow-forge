"""WorkflowRunner behaviour."""

from __future__ import annotations

import pytest

from flow_forge.app import create_app
from flow_forge.core.workflow.runner import WorkflowRunner
from flow_forge.services.workflow_service import WorkflowService
from sample_data import sample_code_graph, sample_graph


@pytest.fixture
def session_factory(tmp_path):
    app = create_app(database_url=f"sqlite:///{tmp_path / 'runner.db'}")
    return app.extensions["db_session_factory"]


def test_runner_start_template_end_succeeds(session_factory) -> None:
    service = WorkflowService(session_factory)
    workflow = service.create(sample_graph())
    runner = WorkflowRunner(session_factory)

    run = runner.run(workflow.id, inputs={"name": "Flow"})

    assert run.status == "succeeded"
    assert run.outputs == {"text": "Hello, Flow!"}
    events = runner.list_events(run.id)
    types = [event.event_type for event in events]
    assert "node_started" in types
    assert "node_succeeded" in types
    assert types.count("node_started") == 3


def test_runner_missing_template_variable_fails(session_factory) -> None:
    service = WorkflowService(session_factory)
    workflow = service.create(sample_graph())
    runner = WorkflowRunner(session_factory)

    run = runner.run(workflow.id, inputs={})

    assert run.status == "failed"
    assert run.error
    events = runner.list_events(run.id)
    assert any(event.event_type == "node_failed" for event in events)


def test_runner_start_code_end_succeeds(session_factory) -> None:
    service = WorkflowService(session_factory)
    workflow = service.create(sample_code_graph())
    runner = WorkflowRunner(session_factory)

    run = runner.run(workflow.id, inputs={"name": "flow"})

    assert run.status == "succeeded"
    assert run.outputs == {"text": "FLOW", "result": "FLOW"}
    events = runner.list_events(run.id)
    assert len(events) == 6
    assert events[0].event_type == "node_started"


def test_runner_code_syntax_error_fails(session_factory) -> None:
    service = WorkflowService(session_factory)
    workflow = service.create(sample_code_graph(code="result = ("))
    runner = WorkflowRunner(session_factory)

    run = runner.run(workflow.id, inputs={"name": "x"})

    assert run.status == "failed"
    assert run.error
    events = runner.list_events(run.id)
    assert any(event.event_type == "node_failed" for event in events)
