"""Run HTTP controllers."""

from __future__ import annotations

from flask import Blueprint, current_app, jsonify, request

from flow_forge.core.workflow.runner import WorkflowRunner

bp = Blueprint("runs", __name__)


def _runner() -> WorkflowRunner:
    return WorkflowRunner(current_app.extensions["db_session_factory"])


@bp.post("/workflows/<workflow_id>/runs")
def start_run(workflow_id: str):
    body = request.get_json(silent=True) or {}
    inputs = body.get("inputs") or {}
    if not isinstance(inputs, dict):
        return jsonify(error="inputs must be an object"), 400
    try:
        run = _runner().run(workflow_id, inputs=inputs)
    except ValueError as exc:
        return jsonify(error=str(exc)), 404
    return (
        jsonify(
            id=run.id,
            workflow_id=run.workflow_id,
            status=run.status,
            inputs=run.inputs,
            outputs=run.outputs,
            error=run.error,
        ),
        201,
    )


@bp.get("/runs/<run_id>")
def get_run(run_id: str):
    run = _runner().get_run(run_id)
    if run is None:
        return jsonify(error="run not found"), 404
    return jsonify(
        id=run.id,
        workflow_id=run.workflow_id,
        status=run.status,
        inputs=run.inputs,
        outputs=run.outputs,
        error=run.error,
    )


@bp.get("/runs/<run_id>/events")
def get_run_events(run_id: str):
    run = _runner().get_run(run_id)
    if run is None:
        return jsonify(error="run not found"), 404
    events = _runner().list_events(run_id)
    return jsonify(
        events=[
            {
                "id": event.id,
                "sequence": event.sequence,
                "event_type": event.event_type,
                "node_id": event.node_id,
                "payload": event.payload,
            }
            for event in events
        ]
    )
