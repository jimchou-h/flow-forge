"use client";

import { Handle, Position, type NodeProps } from "@xyflow/react";

import type { WorkflowFlowNode } from "../lib/graph-codec";
import styles from "./workflow-node.module.css";

export function WorkflowNode({ data, selected }: NodeProps<WorkflowFlowNode>) {
  const isStart = data.type === "start";
  const isEnd = data.type === "end";
  const isIfElse = data.type === "if-else";

  return (
    <div className={`${styles.node} ${selected ? styles.selected : ""}`}>
      {!isStart ? <Handle type="target" position={Position.Left} className={styles.handle} /> : null}
      <div className={styles.type}>{data.type}</div>
      <div className={styles.idHint}>{summarize(data)}</div>
      {isIfElse ? (
        <>
          <Handle
            type="source"
            position={Position.Right}
            id="true"
            className={`${styles.handle} ${styles.handleTrue}`}
            style={{ top: "35%" }}
          />
          <Handle
            type="source"
            position={Position.Right}
            id="false"
            className={`${styles.handle} ${styles.handleFalse}`}
            style={{ top: "65%" }}
          />
          <span className={styles.handleLabel} style={{ top: "28%" }}>
            true
          </span>
          <span className={styles.handleLabel} style={{ top: "58%" }}>
            false
          </span>
        </>
      ) : !isEnd ? (
        <Handle type="source" position={Position.Right} className={styles.handle} />
      ) : null}
    </div>
  );
}

function summarize(data: WorkflowFlowNode["data"]): string {
  if (data.template) return truncate(data.template);
  if (data.code) return truncate(data.code);
  if (data.prompt) return truncate(data.prompt);
  if (data.condition) return truncate(data.condition);
  return data.type;
}

function truncate(value: string, max = 28): string {
  const oneLine = value.replace(/\s+/g, " ").trim();
  return oneLine.length > max ? `${oneLine.slice(0, max)}…` : oneLine;
}
