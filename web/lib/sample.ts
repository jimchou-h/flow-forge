import type { WorkflowGraph } from "./api";

/** 与 api 测试夹具同构的最小图：start → template → end */
export const SAMPLE_GRAPH: WorkflowGraph = {
  nodes: [
    { id: "start_1", data: { type: "start" } },
    {
      id: "tpl_1",
      data: { type: "template", template: "Hello, {name}!" },
    },
    { id: "end_1", data: { type: "end" } },
  ],
  edges: [
    { id: "e1", source: "start_1", target: "tpl_1" },
    { id: "e2", source: "tpl_1", target: "end_1" },
  ],
};

export const SAMPLE_INPUTS = { name: "Forge" };
