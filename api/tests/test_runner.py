"""WorkflowRunner behaviour."""

from __future__ import annotations

import pytest

from flow_forge.app import create_app
from flow_forge.core.workflow.runner import WorkflowRunner
from flow_forge.services.workflow_service import WorkflowService
from sample_data import sample_graph


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
