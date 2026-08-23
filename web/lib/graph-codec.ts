/** 画布 ↔ API WorkflowGraph 编解码（剥离 React Flow / UI 私有字段）。 */

import type { Edge, Node } from "@xyflow/react";

import type { WorkflowGraph } from "./api";

export type WorkflowNodeData = {
  type: string;
  template?: string;
  code?: string;
  prompt?: string;
  condition?: string;
  label?: string;
  /** 运行态高亮：仅前端，不进入 API graph */
  runStatus?: "running" | "succeeded" | "failed";
};

export type WorkflowFlowNode = Node<WorkflowNodeData>;
export type WorkflowFlowEdge = Edge;

const DEFAULT_GAP_X = 220;
const DEFAULT_Y = 120;

export function fromWorkflowGraph(graph: WorkflowGraph): {
  nodes: WorkflowFlowNode[];
  edges: WorkflowFlowEdge[];
} {
  const nodes: WorkflowFlowNode[] = graph.nodes.map((node, index) => ({
    id: node.id,
    type: "workflow",
    position: { x: 40 + index * DEFAULT_GAP_X, y: DEFAULT_Y },
    data: {
      type: node.data.type,
      template: node.data.template,
      code: node.data.code,
      prompt: node.data.prompt,
      condition: node.data.condition,
      label: node.data.type,
    },
  }));

  const edges: WorkflowFlowEdge[] = graph.edges.map((edge, index) => ({
    id: edge.id ?? `e_${edge.source}_${edge.target}_${index}`,
    source: edge.source,
    target: edge.target,
    sourceHandle: edge.source_handle ?? undefined,
  }));

  return { nodes, edges };
}

export function toWorkflowGraph(
  nodes: WorkflowFlowNode[],
  edges: WorkflowFlowEdge[],
): WorkflowGraph {
  return {
    nodes: nodes.map((node) => {
      const data: WorkflowGraph["nodes"][number]["data"] = {
        type: node.data.type,
      };
      if (node.data.template !== undefined && node.data.template !== "") {
        data.template = node.data.template;
      }
      if (node.data.code !== undefined && node.data.code !== "") {
        data.code = node.data.code;
      }
      if (node.data.prompt !== undefined && node.data.prompt !== "") {
        data.prompt = node.data.prompt;
      }
      if (node.data.condition !== undefined && node.data.condition !== "") {
        data.condition = node.data.condition;
      }
      return { id: node.id, data };
    }),
    edges: edges.map((edge) => {
      const out: WorkflowGraph["edges"][number] = {
        id: edge.id,
        source: edge.source,
        target: edge.target,
      };
      if (edge.sourceHandle === "true" || edge.sourceHandle === "false") {
        out.source_handle = edge.sourceHandle;
      }
      return out;
    }),
  };
}

export function createNodeId(type: string, existing: string[]): string {
  const base = type === "if-else" ? "if" : type;
  let n = 1;
  let id = `${base}_${n}`;
  const used = new Set(existing);
  while (used.has(id)) {
    n += 1;
    id = `${base}_${n}`;
  }
  return id;
}

export function defaultDataForType(type: string): WorkflowNodeData {
  switch (type) {
    case "template":
      return { type, template: "Hello, {name}!", label: type };
    case "code":
      return { type, code: "result = name.upper()", label: type };
    case "llm":
      return { type, prompt: "Say hello to {name}", label: type };
    case "if-else":
      return { type, condition: "result = score >= 60", label: type };
    case "end":
      return { type, label: type };
    case "start":
      return { type, label: type };
    default:
      return { type, label: type };
  }
}
