"""Workflow application services."""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session, sessionmaker

from flow_forge.core.workflow.graph import WorkflowGraph, validate_workflow_graph
from flow_forge.models import Workflow


class WorkflowService:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def create(self, graph_payload: dict[str, Any]) -> Workflow:
        graph = validate_workflow_graph(graph_payload)
        with self._session_factory() as session:
            workflow = Workflow(graph=graph.model_dump(mode="json", exclude_none=True))
            session.add(workflow)
            session.commit()
            session.refresh(workflow)
            session.expunge(workflow)
            return workflow

    def get(self, workflow_id: str) -> Workflow | None:
        with self._session_factory() as session:
            workflow = session.get(Workflow, workflow_id)
            if workflow is None:
                return None
            session.expunge(workflow)
            return workflow
