/** 浏览器侧 API 封装：一律走 /api-proxy，由 next.config 转到 Flask。 */

export const API_PROXY_PREFIX = "/api-proxy";

export type WorkflowGraph = {
  nodes: Array<{
    id: string;
    data: {
      type: string;
      template?: string;
      code?: string;
      prompt?: string;
      condition?: string;
    };
  }>;
  edges: Array<{
    id?: string;
    source: string;
    target: string;
    source_handle?: "true" | "false";
  }>;
};

export type RunEvent = {
  id: string;
  sequence: number;
  event_type: string;
  node_id: string | null;
  payload: Record<string, unknown> | null;
};

export type WorkflowRun = {
  id: string;
  workflow_id: string;
  status: string;
  inputs: Record<string, unknown>;
  outputs: Record<string, unknown> | null;
  error: string | null;
};

async function readJson(response: Response): Promise<unknown> {
  const text = await response.text();
  try {
    return text ? JSON.parse(text) : null;
  } catch {
    throw new Error(`后端返回了非 JSON（HTTP ${response.status}）：${text.slice(0, 200)}`);
  }
}

export async function createWorkflow(graph: WorkflowGraph): Promise<{ id: string }> {
  const response = await fetch(`${API_PROXY_PREFIX}/workflows`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ graph }),
  });
  const body = (await readJson(response)) as { id?: string; error?: string };
  if (!response.ok) {
    throw new Error(body?.error ?? `创建工作流失败（HTTP ${response.status}）`);
  }
  if (!body.id) {
    throw new Error("创建工作流成功但未返回 id");
  }
  return { id: body.id };
}

export async function startRun(
  workflowId: string,
  inputs: Record<string, unknown>,
): Promise<WorkflowRun> {
  const response = await fetch(`${API_PROXY_PREFIX}/workflows/${workflowId}/runs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ inputs }),
  });
  const body = (await readJson(response)) as WorkflowRun & { error?: string };
  if (!response.ok) {
    throw new Error(
      typeof body?.error === "string"
        ? body.error
        : `启动运行失败（HTTP ${response.status}）`,
    );
  }
  return body;
}

export async function listRunEvents(runId: string): Promise<RunEvent[]> {
  const response = await fetch(`${API_PROXY_PREFIX}/runs/${runId}/events`);
  const body = (await readJson(response)) as { events?: RunEvent[]; error?: string };
  if (!response.ok) {
    throw new Error(body?.error ?? `拉取事件失败（HTTP ${response.status}）`);
  }
  return body.events ?? [];
}

/** 一次联调：建图 → 跑 → 拉事件 */
export async function runGraphOnce(
  graph: WorkflowGraph,
  inputs: Record<string, unknown>,
): Promise<{ run: WorkflowRun; events: RunEvent[] }> {
  const { id } = await createWorkflow(graph);
  const run = await startRun(id, inputs);
  const events = await listRunEvents(run.id);
  return { run, events };
}
