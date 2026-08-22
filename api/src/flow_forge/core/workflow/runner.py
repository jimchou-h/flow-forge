"""同步工作流执行器。

设计要点：
- ``run(run_id 对应的 workflow)`` 在调用方线程内跑完整张图（今日同步；日后可改成入队调用同一入口）
- 每步写入 ``WorkflowRunEvent``，客户端可用 run_id 轮询，不必依赖 SSE
- 变量是简单 dict：运行 inputs 起步，template 结果写入 ``text`` 供下游使用
"""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session, sessionmaker

from flow_forge.core.workflow.graph import WorkflowGraph, validate_workflow_graph
from flow_forge.core.workflow.nodes.code import execute_code
from flow_forge.core.workflow.nodes.llm import execute_llm
from flow_forge.core.workflow.providers.base import LlmProvider
from flow_forge.core.workflow.providers.stub import StubLlmProvider
from flow_forge.models import Workflow, WorkflowRun, WorkflowRunEvent


class WorkflowRunner:
    """按边顺序执行图，并持久化 run / events。"""

    def __init__(
        self,
        session_factory: sessionmaker[Session],
        llm_provider: LlmProvider | None = None,
    ) -> None:
        self._session_factory = session_factory
        self._llm_provider = llm_provider or StubLlmProvider()

    def run(self, workflow_id: str, inputs: dict[str, Any] | None = None) -> WorkflowRun:
        """同步执行一次工作流，返回终态 run（succeeded / failed）。"""

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
            # 先拿到 run.id，便于执行过程中写事件
            session.flush()

            try:
                outputs = self._execute(session, run, graph, inputs)
                run.status = "succeeded"
                run.outputs = outputs
            except Exception as exc:  # noqa: BLE001 — 节点失败记到 run，不让进程崩
                run.status = "failed"
                run.error = str(exc)
                run.outputs = None

            session.commit()
            session.refresh(run)
            # 会话关闭后仍可读字段
            session.expunge(run)
            return run

    def list_events(self, run_id: str) -> list[WorkflowRunEvent]:
        """按 sequence 返回某次运行的全部事件。"""

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
        """按 id 读取一次运行记录。"""

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
        """从唯一的 start 出发，沿单后继边走到没有出边为止。"""

        nodes = {node.id: node for node in graph.nodes}
        # adjacency[source] = [target, ...]；本阶段每个节点最多一个后继
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
                    # start 只负责注入 inputs，无额外计算
                    pass
                elif node.data.type == "template":
                    assert node.data.template is not None
                    # format_map + _SafeDict：缺变量会 KeyError，落入 node_failed
                    rendered = node.data.template.format_map(_SafeDict(variables))
                    variables[f"{node.id}.text"] = rendered
                    variables["text"] = rendered
                    outputs = {"text": rendered}
                elif node.data.type == "code":
                    assert node.data.code is not None
                    code_result = execute_code(node.data.code, variables)
                    variables["result"] = code_result
                    variables[f"{node.id}.result"] = code_result
                    if isinstance(code_result, str):
                        variables["text"] = code_result
                        outputs = {"text": code_result, "result": code_result}
                    else:
                        outputs = {"result": code_result}
                elif node.data.type == "llm":
                    assert node.data.prompt is not None
                    llm_text = execute_llm(node.data.prompt, variables, self._llm_provider)
                    variables[f"{node.id}.text"] = llm_text
                    variables["text"] = llm_text
                    outputs = {"text": llm_text}
                elif node.data.type == "end":
                    if "result" in variables:
                        outputs = {"result": variables["result"]}
                        if "text" in variables:
                            outputs["text"] = variables["text"]
                    else:
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
        """追加一条有序事件，返回新的 sequence。"""

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
    """供 str.format_map 使用：缺 key 时立刻失败，而不是静默留空。"""

    def __missing__(self, key: str) -> str:
        raise KeyError(key)
