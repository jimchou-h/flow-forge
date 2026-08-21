"""Synchronous workflow runner."""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session, sessionmaker

from flow_forge.core.workflow.graph import WorkflowGraph, validate_workflow_graph
from flow_forge.models import Workflow, WorkflowRun, WorkflowRunEvent


class WorkflowRunner:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def run(self, workflow_id: str, inputs: dict[str, Any] | None = None) -> WorkflowRun:
        inputs = inputs or {}
        with self._session_factory() as session:
            workflow = session.get(Workflow, workflow_id)
            if workflow is None:
                raise ValueError(f"workflow not found: {workflow_id}")

            graph = validate_workflow_graph(workflow.graph)
            run = WorkflowRun(
                workflow_id=workflow.id,
                status="running",
                inputs=inputs,
            )
            session.add(run)
            session.flush()

            try:
                outputs = self._execute(session, run, graph, inputs)
                run.status = "succeeded"
                run.outputs = outputs
            except Exception as exc:  # noqa: BLE001 — record failure on run
                run.status = "failed"
                run.error = str(exc)
                run.outputs = None

            session.commit()
            session.refresh(run)
            session.expunge(run)
            return run

    def list_events(self, run_id: str) -> list[WorkflowRunEvent]:
        with self._session_factory() as session:
            events = (
                session.query(WorkflowRunEvent)
                .filter(WorkflowRunEvent.run_id == run_id)
                .order_by(WorkflowRunEvent.sequence)
                .all()
            )
            for event in events:
                session.expunge(event)
            return events

    def get_run(self, run_id: str) -> WorkflowRun | None:
        with self._session_factory() as session:
            run = session.get(WorkflowRun, run_id)
            if run is None:
                return None
            session.expunge(run)
            return run

    def _execute(
        self,
        session: Session,
        run: WorkflowRun,
        graph: WorkflowGraph,
        inputs: dict[str, Any],
    ) -> dict[str, Any]:
        nodes = {node.id: node for node in graph.nodes}
        adjacency: dict[str, list[str]] = {node.id: [] for node in graph.nodes}
        for edge in graph.edges:
            adjacency[edge.source].append(edge.target)

        start_nodes = [node for node in graph.nodes if node.data.type == "start"]
        if len(start_nodes) != 1:
            raise ValueError("graph must contain exactly one start node")

        variables: dict[str, Any] = dict(inputs)
        outputs: dict[str, Any] = {}
        sequence = 0
        current_id = start_nodes[0].id
        visited: set[str] = set()

        while current_id:
            if current_id in visited:
                raise ValueError("cycle detected in graph")
            visited.add(current_id)
            node = nodes[current_id]
            sequence = self._append_event(session, run.id, sequence, "node_started", node.id)

            try:
                if node.data.type == "start":
                    pass
                elif node.data.type == "template":
                    assert node.data.template is not None
                    rendered = node.data.template.format_map(_SafeDict(variables))
                    variables[f"{node.id}.text"] = rendered
                    variables["text"] = rendered
                    outputs = {"text": rendered}
                elif node.data.type == "end":
                    outputs = {"text": variables.get("text")}
                else:
                    raise ValueError(f"unsupported node type: {node.data.type}")
            except Exception as exc:
                self._append_event(
                    session,
                    run.id,
                    sequence,
                    "node_failed",
                    node.id,
                    {"error": str(exc)},
                )
                raise

            sequence = self._append_event(session, run.id, sequence, "node_succeeded", node.id)
            next_ids = adjacency.get(current_id, [])
            if not next_ids:
                break
            if len(next_ids) > 1:
                raise ValueError("parallel edges are not supported in this slice")
            current_id = next_ids[0]

        return outputs

    def _append_event(
        self,
        session: Session,
        run_id: str,
        sequence: int,
        event_type: str,
        node_id: str | None,
        payload: dict[str, Any] | None = None,
    ) -> int:
        next_sequence = sequence + 1
        session.add(
            WorkflowRunEvent(
                run_id=run_id,
                sequence=next_sequence,
                event_type=event_type,
                node_id=node_id,
                payload=payload,
            )
        )
        session.flush()
        return next_sequence


class _SafeDict(dict[str, Any]):
    def __missing__(self, key: str) -> str:
        raise KeyError(key)
