"""同步工作流执行器。

设计要点：
- 同步跑完整张图；每步写 ``WorkflowRunEvent``，可用 run_id 轮询
- 调度：前驱计数 + 就绪队列；fan-out 按出边顺序入队（顺序模拟并行）
- if-else：只激活选中支路，对未选支路做 skip 传播，以便汇合点正确 join
"""

from __future__ import annotations

from collections import deque
from typing import Any, Literal

from sqlalchemy.orm import Session, sessionmaker

from flow_forge.core.workflow.graph import GraphEdge, WorkflowGraph, validate_workflow_graph
from flow_forge.core.workflow.nodes.code import execute_code
from flow_forge.core.workflow.nodes.if_else import evaluate_condition
from flow_forge.core.workflow.nodes.llm import execute_llm
from flow_forge.core.workflow.providers.base import LlmProvider
from flow_forge.core.workflow.providers.stub import StubLlmProvider
from flow_forge.models import Workflow, WorkflowRun, WorkflowRunEvent

NodeStatus = Literal["pending", "succeeded", "skipped"]


class WorkflowRunner:
    """按边调度执行图，并持久化 run / events。"""

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
        """就绪队列调度：支持线性、if-else 互斥、fan-out/join。"""

        nodes = {node.id: node for node in graph.nodes}
        adjacency: dict[str, list[GraphEdge]] = {node.id: [] for node in graph.nodes}
        predecessors: dict[str, list[str]] = {node.id: [] for node in graph.nodes}
        remaining: dict[str, int] = {node.id: 0 for node in graph.nodes}

        for edge in graph.edges:
            adjacency[edge.source].append(edge)
            predecessors[edge.target].append(edge.source)
            remaining[edge.target] += 1

        start_nodes = [node for node in graph.nodes if node.data.type == "start"]
        if len(start_nodes) != 1:
            raise ValueError("graph must contain exactly one start node")

        status: dict[str, NodeStatus] = {node.id: "pending" for node in graph.nodes}
        # 每个节点收到的前驱结局：True=成功，False=skip
        pred_signals: dict[str, list[bool]] = {node.id: [] for node in graph.nodes}

        variables: dict[str, Any] = dict(inputs)
        outputs: dict[str, Any] = {}
        sequence = 0
        ready: deque[str] = deque()

        start_id = start_nodes[0].id
        if remaining[start_id] != 0:
            raise ValueError("start node must have in-degree 0")
        ready.append(start_id)

        def signal(target_id: str, *, succeeded: bool) -> None:
            if status[target_id] != "pending":
                return
            pred_signals[target_id].append(succeeded)
            remaining[target_id] -= 1
            if remaining[target_id] > 0:
                return
            if any(pred_signals[target_id]):
                ready.append(target_id)
            else:
                skip_node(target_id)

        def skip_node(node_id: str) -> None:
            if status[node_id] != "pending":
                return
            status[node_id] = "skipped"
            for edge in adjacency[node_id]:
                signal(edge.target, succeeded=False)

        while ready:
            current_id = ready.popleft()
            if status[current_id] != "pending":
                continue
            node = nodes[current_id]
            sequence = self._append_event(session, run.id, sequence, "node_started", node.id)
            chosen_handle: str | None = None

            try:
                if node.data.type == "start":
                    pass
                elif node.data.type == "template":
                    assert node.data.template is not None
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
                elif node.data.type == "if-else":
                    assert node.data.condition is not None
                    branch = evaluate_condition(node.data.condition, variables)
                    chosen_handle = "true" if branch else "false"
                    variables[f"{node.id}.branch"] = chosen_handle
                elif node.data.type == "end":
                    if "result" in variables:
                        outputs = {"result": variables["result"]}
                        if "text" in variables:
                            outputs["text"] = variables["text"]
                    else:
                        # 并行汇合：优先拼 scoped text，避免只剩最后一支的全局 text
                        scoped = {
                            key.removesuffix(".text"): value
                            for key, value in variables.items()
                            if key.endswith(".text") and isinstance(value, str)
                        }
                        if len(scoped) > 1:
                            outputs = {"text": variables.get("text"), "branches": scoped}
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
            status[current_id] = "succeeded"

            out_edges = adjacency.get(current_id, [])
            if node.data.type == "if-else":
                assert chosen_handle is not None
                for edge in out_edges:
                    if edge.source_handle == chosen_handle:
                        signal(edge.target, succeeded=True)
                    else:
                        signal(edge.target, succeeded=False)
            else:
                for edge in out_edges:
                    signal(edge.target, succeeded=True)

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
