"use client";

import {
  Background,
  Controls,
  MiniMap,
  ReactFlow,
  ReactFlowProvider,
  addEdge,
  useEdgesState,
  useNodesState,
  type Connection,
  type Edge,
  type OnSelectionChangeParams,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { useCallback, useMemo, useState } from "react";

import {
  runGraphOnce,
  type RunEvent,
  type WorkflowGraph,
  type WorkflowRun,
} from "../lib/api";
import {
  createNodeId,
  defaultDataForType,
  fromWorkflowGraph,
  toWorkflowGraph,
  type WorkflowFlowNode,
  type WorkflowNodeData,
} from "../lib/graph-codec";
import { SAMPLE_GRAPH, SAMPLE_INPUTS } from "../lib/sample";
import { WorkflowNode } from "./workflow-node";
import styles from "./workflow-editor.module.css";

const ADDABLE_TYPES = ["template", "code", "llm", "if-else", "end"] as const;

const nodeTypes = { workflow: WorkflowNode };

function parseJson<T>(raw: string, label: string): { ok: true; value: T } | { ok: false; message: string } {
  try {
    return { ok: true, value: JSON.parse(raw) as T };
  } catch (error) {
    const detail = error instanceof Error ? error.message : String(error);
    return { ok: false, message: `${label} 不是合法 JSON：${detail}` };
  }
}

function EditorInner() {
  const initial = useMemo(() => fromWorkflowGraph(SAMPLE_GRAPH), []);
  const [nodes, setNodes, onNodesChange] = useNodesState<WorkflowFlowNode>(initial.nodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initial.edges);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [inputsText, setInputsText] = useState(() => JSON.stringify(SAMPLE_INPUTS, null, 2));
  const [jsonPreview, setJsonPreview] = useState(() => JSON.stringify(SAMPLE_GRAPH, null, 2));
  const [showJson, setShowJson] = useState(false);
  const [busy, setBusy] = useState(false);
  const [uiError, setUiError] = useState<string | null>(null);
  const [run, setRun] = useState<WorkflowRun | null>(null);
  const [events, setEvents] = useState<RunEvent[]>([]);

  const selected = nodes.find((node) => node.id === selectedId) ?? null;

  const onConnect = useCallback(
    (connection: Connection) => {
      setEdges((current) =>
        addEdge(
          {
            ...connection,
            id: `e_${connection.source}_${connection.target}_${connection.sourceHandle ?? "out"}`,
          },
          current,
        ),
      );
    },
    [setEdges],
  );

  const onSelectionChange = useCallback(({ nodes: selectedNodes }: OnSelectionChangeParams) => {
    setSelectedId(selectedNodes[0]?.id ?? null);
  }, []);

  function refreshPreview(nextNodes: WorkflowFlowNode[], nextEdges: Edge[]) {
    setJsonPreview(JSON.stringify(toWorkflowGraph(nextNodes, nextEdges), null, 2));
  }

  function addNode(type: (typeof ADDABLE_TYPES)[number]) {
    const id = createNodeId(type, nodes.map((node) => node.id));
    const node: WorkflowFlowNode = {
      id,
      type: "workflow",
      position: { x: 80 + nodes.length * 40, y: 80 + (nodes.length % 4) * 60 },
      data: defaultDataForType(type),
    };
    const next = [...nodes, node];
    setNodes(next);
    setSelectedId(id);
    refreshPreview(next, edges);
  }

  function deleteSelected() {
    if (!selected) return;
    if (selected.data.type === "start") {
      setUiError("不能删除唯一的 start 节点");
      return;
    }
    const nextNodes = nodes.filter((node) => node.id !== selected.id);
    const nextEdges = edges.filter(
      (edge) => edge.source !== selected.id && edge.target !== selected.id,
    );
    setNodes(nextNodes);
    setEdges(nextEdges);
    setSelectedId(null);
    refreshPreview(nextNodes, nextEdges);
  }

  function updateSelectedData(patch: Partial<WorkflowNodeData>) {
    if (!selected) return;
    const nextNodes = nodes.map((node) =>
      node.id === selected.id ? { ...node, data: { ...node.data, ...patch } } : node,
    );
    setNodes(nextNodes);
    refreshPreview(nextNodes, edges);
  }

  function loadFromJson() {
    const parsed = parseJson<WorkflowGraph>(jsonPreview, "图 JSON");
    if (!parsed.ok) {
      setUiError(parsed.message);
      return;
    }
    const { nodes: nextNodes, edges: nextEdges } = fromWorkflowGraph(parsed.value);
    setNodes(nextNodes);
    setEdges(nextEdges);
    setSelectedId(null);
    setUiError(null);
  }

  async function onRun() {
    setUiError(null);
    setRun(null);
    setEvents([]);

    const graph = toWorkflowGraph(nodes as WorkflowFlowNode[], edges);
    setJsonPreview(JSON.stringify(graph, null, 2));

    const inputsParsed = parseJson<Record<string, unknown>>(inputsText, "inputs JSON");
    if (!inputsParsed.ok) {
      setUiError(inputsParsed.message);
      return;
    }

    setBusy(true);
    try {
      const result = await runGraphOnce(graph, inputsParsed.value);
      setRun(result.run);
      setEvents(result.events);
      if (result.run.status === "failed") {
        setUiError(result.run.error ?? "运行失败（详见事件列表）");
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      setUiError(
        message.includes("Failed to fetch")
          ? "无法连接后端。请确认已启动 api（Flask），且 web 的 /api-proxy 可转发。"
          : message,
      );
    } finally {
      setBusy(false);
    }
  }

  const statusClass =
    run?.status === "succeeded" ? styles.ok : run?.status === "failed" ? styles.bad : "";

  return (
    <div className={styles.root}>
      <aside className={styles.palette}>
        <h2>添加节点</h2>
        <div className={styles.paletteButtons}>
          {ADDABLE_TYPES.map((type) => (
            <button key={type} type="button" onClick={() => addNode(type)}>
              + {type}
            </button>
          ))}
        </div>
        <label className={styles.field}>
          <span>inputs JSON</span>
          <textarea
            value={inputsText}
            onChange={(event) => setInputsText(event.target.value)}
            spellCheck={false}
            rows={6}
          />
        </label>
        <button type="button" className={styles.primary} disabled={busy} onClick={onRun}>
          {busy ? "运行中…" : "从画布运行"}
        </button>
        <button type="button" className={styles.secondary} onClick={() => setShowJson((v) => !v)}>
          {showJson ? "隐藏 JSON" : "显示 JSON"}
        </button>
      </aside>

      <div className={styles.center}>
        <div className={styles.canvas}>
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onSelectionChange={onSelectionChange}
            onBeforeDelete={async ({ nodes: deleting }) => {
              if (deleting.some((node) => (node.data as WorkflowNodeData).type === "start")) {
                setUiError("不能删除唯一的 start 节点");
                return false;
              }
              return true;
            }}
            nodeTypes={nodeTypes}
            fitView
            deleteKeyCode={["Backspace", "Delete"]}
          >
            <Background />
            <Controls />
            <MiniMap />
          </ReactFlow>
        </div>

        {showJson ? (
          <div className={styles.jsonPanel}>
            <div className={styles.jsonActions}>
              <span>图 JSON（调试）</span>
              <button type="button" onClick={loadFromJson}>
                从 JSON 加载到画布
              </button>
            </div>
            <textarea
              value={jsonPreview}
              onChange={(event) => setJsonPreview(event.target.value)}
              spellCheck={false}
              rows={10}
            />
          </div>
        ) : null}

        {uiError ? <p className={styles.errorBox}>{uiError}</p> : null}

        {run ? (
          <section className={styles.result}>
            <h2>运行结果</h2>
            <p className={statusClass}>
              status: <strong>{run.status}</strong> · run_id: <code>{run.id}</code>
            </p>
            <h3>outputs</h3>
            <pre>{JSON.stringify(run.outputs, null, 2)}</pre>
            {run.error ? (
              <>
                <h3>error</h3>
                <pre>{run.error}</pre>
              </>
            ) : null}
            <h3>events</h3>
            <ol className={styles.events}>
              {events.map((event) => (
                <li key={event.id}>
                  <code>
                    #{event.sequence} {event.event_type}
                    {event.node_id ? ` @ ${event.node_id}` : ""}
                  </code>
                  {event.payload ? <pre>{JSON.stringify(event.payload, null, 2)}</pre> : null}
                </li>
              ))}
            </ol>
          </section>
        ) : null}
      </div>

      <aside className={styles.sidebar}>
        <h2>节点属性</h2>
        {!selected ? (
          <p className={styles.muted}>选中画布上的节点以编辑</p>
        ) : (
          <>
            <p>
              <code>{selected.id}</code> · {selected.data.type}
            </p>
            {selected.data.type === "template" ? (
              <label className={styles.field}>
                <span>template</span>
                <textarea
                  value={selected.data.template ?? ""}
                  onChange={(event) => updateSelectedData({ template: event.target.value })}
                  rows={4}
                />
              </label>
            ) : null}
            {selected.data.type === "code" ? (
              <label className={styles.field}>
                <span>code</span>
                <textarea
                  value={selected.data.code ?? ""}
                  onChange={(event) => updateSelectedData({ code: event.target.value })}
                  rows={6}
                />
              </label>
            ) : null}
            {selected.data.type === "llm" ? (
              <label className={styles.field}>
                <span>prompt</span>
                <textarea
                  value={selected.data.prompt ?? ""}
                  onChange={(event) => updateSelectedData({ prompt: event.target.value })}
                  rows={4}
                />
              </label>
            ) : null}
            {selected.data.type === "if-else" ? (
              <label className={styles.field}>
                <span>condition</span>
                <textarea
                  value={selected.data.condition ?? ""}
                  onChange={(event) => updateSelectedData({ condition: event.target.value })}
                  rows={4}
                />
              </label>
            ) : null}
            {selected.data.type !== "start" ? (
              <button type="button" className={styles.danger} onClick={deleteSelected}>
                删除节点
              </button>
            ) : (
              <p className={styles.muted}>start 不可删除</p>
            )}
            {selected.data.type === "if-else" ? (
              <p className={styles.hint}>
                从右侧 true / false 锚点连出两条边，对应 API 的 source_handle。
              </p>
            ) : null}
          </>
        )}
      </aside>
    </div>
  );
}

export function WorkflowEditor() {
  return (
    <ReactFlowProvider>
      <EditorInner />
    </ReactFlowProvider>
  );
}
