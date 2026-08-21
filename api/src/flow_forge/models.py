"""SQLAlchemy 表模型：工作流定义、一次运行、逐步事件。"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import JSON


class Base(DeclarativeBase):
    """所有 ORM 模型的基类。"""


def new_id() -> str:
    """生成字符串主键（UUID）。"""

    return str(uuid4())


class Workflow(Base):
    """已保存的工作流定义（图 JSON）。"""

    __tablename__ = "workflows"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    # 校验后的 graph 快照：{"nodes": [...], "edges": [...]}
    graph: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    runs: Mapped[list[WorkflowRun]] = relationship(back_populates="workflow")


class WorkflowRun(Base):
    """一次执行实例；status 典型为 pending / running / succeeded / failed。"""

    __tablename__ = "workflow_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    workflow_id: Mapped[str] = mapped_column(ForeignKey("workflows.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending")
    inputs: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    outputs: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    workflow: Mapped[Workflow] = relationship(back_populates="runs")
    events: Mapped[list[WorkflowRunEvent]] = relationship(
        back_populates="run",
        order_by="WorkflowRunEvent.sequence",
    )


class WorkflowRunEvent(Base):
    """单次运行内的有序事件（如 node_started / node_succeeded / node_failed）。"""

    __tablename__ = "workflow_run_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    run_id: Mapped[str] = mapped_column(ForeignKey("workflow_runs.id"), nullable=False)
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    node_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    payload: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    run: Mapped[WorkflowRun] = relationship(back_populates="events")
