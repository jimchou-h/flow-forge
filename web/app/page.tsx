"use client";

import { WorkflowEditor } from "../components/workflow-editor";
import styles from "./page.module.css";

export default function HomePage() {
  return (
    <main className={styles.main}>
      <header className={styles.header}>
        <h1>Flow Forge 联调台</h1>
        <p>
          在画布上拖拽编排节点与边，点「从画布运行」：create → run → events（经{" "}
          <code>/api-proxy</code> 转发到本地 Flask）。可展开 JSON 面板做调试加载。
        </p>
      </header>
      <WorkflowEditor />
    </main>
  );
}
