"""运行相关 HTTP：同步 JSON run、SSE 流式 run，以及按 run_id 查询。"""

from __future__ import annotations

import json

from flask import Blueprint, Response, current_app, jsonify, request, stream_with_context

from flow_forge.core.workflow.runner import WorkflowRunner

bp = Blueprint("runs", __name__)


def _runner() -> WorkflowRunner:
    return WorkflowRunner(
        current_app.extensions["db_session_factory"],
        llm_provider=current_app.extensions["llm_provider"],
    )


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


@bp.post("/workflows/<workflow_id>/runs/stream")
def start_run_stream(workflow_id: str):
    """SSE 流式运行：边执行边推送节点事件，最后 ``run_finished``。"""

    body = request.get_json(silent=True) or {}
    inputs = body.get("inputs") or {}
    if not isinstance(inputs, dict):
        return jsonify(error="inputs must be an object"), 400

    runner = _runner()
    # 先确认 workflow 存在，避免 SSE 里才 404
    try:
        # 轻量探测：跑空迭代前先 get — 用 session 读一次
        with current_app.extensions["db_session_factory"]() as session:
            from flow_forge.models import Workflow

            if session.get(Workflow, workflow_id) is None:
                return jsonify(error=f"workflow not found: {workflow_id}"), 404
    except Exception as exc:  # noqa: BLE001
        return jsonify(error=str(exc)), 500

    @stream_with_context
    def generate():
        try:
            for message in runner.iter_run(workflow_id, inputs=inputs):
                yield f"data: {json.dumps(message, ensure_ascii=False)}\n\n"
        except ValueError as exc:
            err = {"type": "run_finished", "status": "failed", "error": str(exc)}
            yield f"data: {json.dumps(err, ensure_ascii=False)}\n\n"

    return Response(
        generate(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
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
