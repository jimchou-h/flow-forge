"""运行相关 HTTP：启动同步 run，并按 run_id 查询详情 / 事件。"""

from __future__ import annotations

from flask import Blueprint, current_app, jsonify, request

from flow_forge.core.workflow.runner import WorkflowRunner

bp = Blueprint("runs", __name__)


def _runner() -> WorkflowRunner:
    return WorkflowRunner(current_app.extensions["db_session_factory"])


@bp.post("/workflows/<workflow_id>/runs")
def start_run(workflow_id: str):
    """同步启动一次运行。

    Body 可选 ``{"inputs": {...}}``。无论成功或节点失败，只要 workflow 存在通常返回 201，
    终态看响应里的 ``status``（succeeded / failed），便于与日后轮询模型一致。
    """

    body = request.get_json(silent=True) or {}
    inputs = body.get("inputs") or {}
    if not isinstance(inputs, dict):
        return jsonify(error="inputs must be an object"), 400
    try:
        run = _runner().run(workflow_id, inputs=inputs)
    except ValueError as exc:
        # 目前主要是 workflow 不存在
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
    """查询单次运行的终态快照。"""

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
    """查询逐步事件列表（可轮询；本阶段同步跑完后一次即可读全）。"""

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
