/**
 * graph-codec round-trip smoke (run: pnpm exec tsx lib/graph-codec.smoke.ts)
 */
import assert from "node:assert/strict";

import { fromWorkflowGraph, toWorkflowGraph } from "./graph-codec";
import { SAMPLE_GRAPH, SAMPLE_IF_ELSE_GRAPH } from "./sample";

const a = fromWorkflowGraph(SAMPLE_GRAPH);
const out = toWorkflowGraph(a.nodes, a.edges);
assert.equal(out.nodes.length, SAMPLE_GRAPH.nodes.length);
assert.equal(out.edges.length, SAMPLE_GRAPH.edges.length);
assert.equal(out.nodes[1]?.data.type, "template");
assert.equal(out.nodes[1]?.data.template, "Hello, {name}!");

const b = fromWorkflowGraph(SAMPLE_IF_ELSE_GRAPH);
const ifOut = toWorkflowGraph(b.nodes, b.edges);
const handles = ifOut.edges
  .filter((edge) => edge.source === "if_1")
  .map((edge) => edge.source_handle)
  .sort();
assert.deepEqual(handles, ["false", "true"]);

console.log("graph-codec smoke ok");
