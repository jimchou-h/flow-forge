"""工作流应用服务：校验图并读写 Workflow 记录。

位于 controllers 与 core 之间：HTTP 不直接碰 ORM，领域校验复用 core.workflow.graph。
"""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session, sessionmaker

from flow_forge.core.workflow.graph import validate_workflow_graph
from flow_forge.models import Workflow


class WorkflowService:
    """创建 / 读取工作流定义。"""

    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def create(self, graph_payload: dict[str, Any]) -> Workflow:
        """校验图后落库；exclude_none 避免把 template=None 写进 JSON。"""

        graph = validate_workflow_graph(graph_payload)
        with self._session_factory() as session:
            workflow = Workflow(graph=graph.model_dump(mode="json", exclude_none=True))
            session.add(workflow)
            session.commit()
            session.refresh(workflow)
            session.expunge(workflow)
            return workflow

    def get(self, workflow_id: str) -> Workflow | None:
        """按 id 读取；不存在返回 None。"""

        with self._session_factory() as session:
            workflow = session.get(Workflow, workflow_id)
            if workflow is None:
                return None
            session.expunge(workflow)
            return workflow
