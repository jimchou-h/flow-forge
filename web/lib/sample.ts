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

/** start → code → end：把 name 转大写 */
export const SAMPLE_CODE_GRAPH: WorkflowGraph = {
  nodes: [
    { id: "start_1", data: { type: "start" } },
    {
      id: "code_1",
      data: { type: "code", code: "result = name.upper()" },
    },
    { id: "end_1", data: { type: "end" } },
  ],
  edges: [
    { id: "e1", source: "start_1", target: "code_1" },
    { id: "e2", source: "code_1", target: "end_1" },
  ],
};

export const SAMPLE_CODE_INPUTS = { name: "forge" };

/** start → llm → end：stub 下输出 Echo: Say hello to … */
export const SAMPLE_LLM_GRAPH: WorkflowGraph = {
  nodes: [
    { id: "start_1", data: { type: "start" } },
    {
      id: "llm_1",
      data: { type: "llm", prompt: "Say hello to {name}" },
    },
    { id: "end_1", data: { type: "end" } },
  ],
  edges: [
    { id: "e1", source: "start_1", target: "llm_1" },
    { id: "e2", source: "llm_1", target: "end_1" },
  ],
};

export const SAMPLE_LLM_INPUTS = { name: "Forge" };

/** start → if-else → (true|false) template → end */
export const SAMPLE_IF_ELSE_GRAPH: WorkflowGraph = {
  nodes: [
    { id: "start_1", data: { type: "start" } },
    {
      id: "if_1",
      data: { type: "if-else", condition: "result = score >= 60" },
    },
    { id: "tpl_true", data: { type: "template", template: "pass" } },
    { id: "tpl_false", data: { type: "template", template: "fail" } },
    { id: "end_1", data: { type: "end" } },
  ],
  edges: [
    { id: "e0", source: "start_1", target: "if_1" },
    { id: "e1", source: "if_1", target: "tpl_true", source_handle: "true" },
    { id: "e2", source: "if_1", target: "tpl_false", source_handle: "false" },
    { id: "e3", source: "tpl_true", target: "end_1" },
    { id: "e4", source: "tpl_false", target: "end_1" },
  ],
};

export const SAMPLE_IF_ELSE_INPUTS = { score: 80 };
