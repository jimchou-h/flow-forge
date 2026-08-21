"""Workflow HTTP controllers."""

from __future__ import annotations

from flask import Blueprint, current_app, jsonify, request
from pydantic import ValidationError

from flow_forge.services.workflow_service import WorkflowService

bp = Blueprint("workflows", __name__)


def _service() -> WorkflowService:
    return WorkflowService(current_app.extensions["db_session_factory"])


@bp.post("/workflows")
def create_workflow():
    body = request.get_json(silent=True) or {}
    graph = body.get("graph")
    if not isinstance(graph, dict):
        return jsonify(error="graph object is required"), 400
    try:
        workflow = _service().create(graph)
    except ValidationError as exc:
        return jsonify(error="invalid graph", details=exc.errors()), 400
    except ValueError as exc:
        return jsonify(error=str(exc)), 400
    return jsonify(id=workflow.id, graph=workflow.graph), 201


@bp.get("/workflows/<workflow_id>")
def get_workflow(workflow_id: str):
    workflow = _service().get(workflow_id)
    if workflow is None:
        return jsonify(error="workflow not found"), 404
    return jsonify(id=workflow.id, graph=workflow.graph), 200
