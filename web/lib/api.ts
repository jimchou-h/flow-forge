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

export type StreamRunMessage =
  | {
      type: string;
      event_type?: string;
      id?: string;
      sequence?: number;
      node_id?: string | null;
      payload?: Record<string, unknown> | null;
    }
  | {
      type: "run_finished";
      run_id: string;
      workflow_id?: string;
      status: string;
      inputs?: Record<string, unknown>;
      outputs: Record<string, unknown> | null;
      error: string | null;
    };

/** 解析 SSE 文本流，对每条 data JSON 回调 */
export async function consumeSse(
  response: Response,
  onMessage: (message: StreamRunMessage) => void,
): Promise<void> {
  if (!response.body) {
    throw new Error("响应无 body，无法读取 SSE");
  }
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const parts = buffer.split("\n\n");
    buffer = parts.pop() ?? "";
    for (const part of parts) {
      const line = part
        .split("\n")
        .map((item) => item.trim())
        .find((item) => item.startsWith("data:"));
      if (!line) continue;
      const payload = line.replace(/^data:\s?/, "");
      if (!payload) continue;
      onMessage(JSON.parse(payload) as StreamRunMessage);
    }
  }
}

/** 建图后走 SSE 流式运行 */
export async function runGraphOnceStream(
  graph: WorkflowGraph,
  inputs: Record<string, unknown>,
  onMessage: (message: StreamRunMessage) => void,
): Promise<{ run: WorkflowRun; events: RunEvent[] }> {
  const { id: workflowId } = await createWorkflow(graph);
  const response = await fetch(`${API_PROXY_PREFIX}/workflows/${workflowId}/runs/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "text/event-stream" },
    body: JSON.stringify({ inputs }),
  });
  if (!response.ok) {
    const body = (await readJson(response)) as { error?: string };
    throw new Error(body?.error ?? `流式运行失败（HTTP ${response.status}）`);
  }

  const liveEvents: RunEvent[] = [];
  const finishBox: {
    value: {
      run_id: string;
      workflow_id?: string;
      status: string;
      inputs?: Record<string, unknown>;
      outputs: Record<string, unknown> | null;
      error: string | null;
    } | null;
  } = { value: null };

  await consumeSse(response, (message) => {
    onMessage(message);
    if (message.type === "run_finished") {
      const done = message as {
        type: "run_finished";
        run_id: string;
        workflow_id?: string;
        status: string;
        inputs?: Record<string, unknown>;
        outputs: Record<string, unknown> | null;
        error: string | null;
      };
      finishBox.value = done;
      return;
    }
    if ("sequence" in message && message.sequence != null) {
      liveEvents.push({
        id: message.id ?? `seq-${message.sequence}`,
        sequence: message.sequence,
        event_type: message.event_type ?? message.type,
        node_id: message.node_id ?? null,
        payload: message.payload ?? null,
      });
    }
  });

  const finished = finishBox.value;
  if (!finished) {
    throw new Error("SSE 流结束但未收到 run_finished");
  }

  const run: WorkflowRun = {
    id: finished.run_id,
    workflow_id: finished.workflow_id ?? workflowId,
    status: finished.status,
    inputs: finished.inputs ?? inputs,
    outputs: finished.outputs,
    error: finished.error,
  };
  return { run, events: liveEvents };
}

/** 一次联调：建图 → 跑 → 拉事件（JSON，非 SSE） */
export async function runGraphOnce(
  graph: WorkflowGraph,
  inputs: Record<string, unknown>,
): Promise<{ run: WorkflowRun; events: RunEvent[] }> {
  const { id } = await createWorkflow(graph);
  const run = await startRun(id, inputs);
  const events = await listRunEvents(run.id);
  return { run, events };
}
