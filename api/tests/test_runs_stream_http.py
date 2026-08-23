"""SSE streaming run HTTP."""

import json

from sample_data import sample_graph


def _parse_sse(raw: str) -> list[dict]:
    messages: list[dict] = []
    for block in raw.split("\n\n"):
        line = block.strip()
        if not line.startswith("data:"):
            continue
        payload = line.removeprefix("data:").strip()
        if payload:
            messages.append(json.loads(payload))
    return messages


def test_stream_run_succeeds(client) -> None:
    created = client.post("/workflows", json={"graph": sample_graph()})
    workflow_id = created.get_json()["id"]

    response = client.post(
        f"/workflows/{workflow_id}/runs/stream",
        json={"inputs": {"name": "Forge"}},
    )
    assert response.status_code == 200
    assert "text/event-stream" in response.content_type

    messages = _parse_sse(response.get_data(as_text=True))
    types = [item["type"] for item in messages]
    assert "node_started" in types
    assert "node_succeeded" in types
    assert types[-1] == "run_finished"
    assert messages[-1]["status"] == "succeeded"
    assert messages[-1]["outputs"] == {"text": "Hello, Forge!"}
    assert messages[-1]["run_id"]


def test_stream_run_fails(client) -> None:
    created = client.post("/workflows", json={"graph": sample_graph()})
    workflow_id = created.get_json()["id"]

    response = client.post(
        f"/workflows/{workflow_id}/runs/stream",
        json={"inputs": {}},
    )
    assert response.status_code == 200
    messages = _parse_sse(response.get_data(as_text=True))
    assert any(item.get("type") == "node_failed" for item in messages)
    assert messages[-1]["type"] == "run_finished"
    assert messages[-1]["status"] == "failed"
    assert messages[-1]["error"]
