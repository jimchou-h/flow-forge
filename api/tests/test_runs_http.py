"""Run HTTP main path."""

from sample_data import sample_graph


def test_create_run_and_fetch_events(client) -> None:
    created = client.post("/workflows", json={"graph": sample_graph()})
    workflow_id = created.get_json()["id"]

    started = client.post(
        f"/workflows/{workflow_id}/runs",
        json={"inputs": {"name": "Forge"}},
    )
    assert started.status_code == 201
    body = started.get_json()
    assert body["status"] == "succeeded"
    assert body["outputs"] == {"text": "Hello, Forge!"}
    run_id = body["id"]

    run = client.get(f"/runs/{run_id}")
    assert run.status_code == 200
    assert run.get_json()["status"] == "succeeded"

    events = client.get(f"/runs/{run_id}/events")
    assert events.status_code == 200
    payload = events.get_json()["events"]
    assert len(payload) >= 3
    assert any(item["event_type"] == "node_succeeded" for item in payload)


def test_failed_run_is_queryable(client) -> None:
    created = client.post("/workflows", json={"graph": sample_graph()})
    workflow_id = created.get_json()["id"]

    started = client.post(f"/workflows/{workflow_id}/runs", json={"inputs": {}})
    assert started.status_code == 201
    body = started.get_json()
    assert body["status"] == "failed"
    run_id = body["id"]

    run = client.get(f"/runs/{run_id}")
    assert run.get_json()["status"] == "failed"
    events = client.get(f"/runs/{run_id}/events").get_json()["events"]
    assert any(item["event_type"] == "node_failed" for item in events)
