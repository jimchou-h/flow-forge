"use client";

import { useMemo, useState } from "react";

import {
  runGraphOnce,
  type RunEvent,
  type WorkflowGraph,
  type WorkflowRun,
} from "../lib/api";
import { SAMPLE_GRAPH, SAMPLE_INPUTS } from "../lib/sample";
import styles from "./page.module.css";

type ParseOk<T> = { ok: true; value: T };
type ParseErr = { ok: false; message: string };

function parseJson<T>(raw: string, label: string): ParseOk<T> | ParseErr {
  try {
    return { ok: true, value: JSON.parse(raw) as T };
  } catch (error) {
    const detail = error instanceof Error ? error.message : String(error);
    return { ok: false, message: `${label} 不是合法 JSON：${detail}` };
  }
}

export default function HomePage() {
  const [graphText, setGraphText] = useState(() =>
    JSON.stringify(SAMPLE_GRAPH, null, 2),
  );
  const [inputsText, setInputsText] = useState(() =>
    JSON.stringify(SAMPLE_INPUTS, null, 2),
  );
  const [busy, setBusy] = useState(false);
  const [uiError, setUiError] = useState<string | null>(null);
  const [run, setRun] = useState<WorkflowRun | null>(null);
  const [events, setEvents] = useState<RunEvent[]>([]);

  const statusClass = useMemo(() => {
    if (!run) return "";
    if (run.status === "succeeded") return styles.ok;
    if (run.status === "failed") return styles.bad;
    return "";
  }, [run]);

  async function onRun() {
    setUiError(null);
    setRun(null);
    setEvents([]);

    const graphParsed = parseJson<WorkflowGraph>(graphText, "图 JSON");
    if (!graphParsed.ok) {
      setUiError(graphParsed.message);
      return;
    }
    const inputsParsed = parseJson<Record<string, unknown>>(inputsText, "inputs JSON");
    if (!inputsParsed.ok) {
      setUiError(inputsParsed.message);
      return;
    }

    setBusy(true);
    try {
      const result = await runGraphOnce(graphParsed.value, inputsParsed.value);
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

  return (
    <main className={styles.main}>
      <header className={styles.header}>
        <h1>Flow Forge 联调台</h1>
        <p>
          粘贴最小工作流图与 inputs，一点运行：create → run → events（经{" "}
          <code>/api-proxy</code> 转发到本地 Flask）。
        </p>
      </header>

      <section className={styles.grid}>
        <label className={styles.field}>
          <span>图 JSON</span>
          <textarea
            value={graphText}
            onChange={(event) => setGraphText(event.target.value)}
            spellCheck={false}
            rows={18}
          />
        </label>
        <label className={styles.field}>
          <span>inputs JSON</span>
          <textarea
            value={inputsText}
            onChange={(event) => setInputsText(event.target.value)}
            spellCheck={false}
            rows={8}
          />
          <button type="button" className={styles.primary} disabled={busy} onClick={onRun}>
            {busy ? "运行中…" : "运行"}
          </button>
        </label>
      </section>

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
                {event.payload ? (
                  <pre>{JSON.stringify(event.payload, null, 2)}</pre>
                ) : null}
              </li>
            ))}
          </ol>
        </section>
      ) : null}
    </main>
  );
}
