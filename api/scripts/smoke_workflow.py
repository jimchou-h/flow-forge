from pathlib import Path
import tempfile

from flow_forge.app import create_app

db = Path(tempfile.mkdtemp()) / "w.db"
client = create_app(f"sqlite:///{db}").test_client()
graph = {
    "nodes": [
        {"id": "start_1", "data": {"type": "start"}},
        {"id": "tpl_1", "data": {"type": "template", "template": "Hello, {name}!"}},
        {"id": "end_1", "data": {"type": "end"}},
    ],
    "edges": [
        {"id": "e1", "source": "start_1", "target": "tpl_1"},
        {"id": "e2", "source": "tpl_1", "target": "end_1"},
    ],
}
workflow = client.post("/workflows", json={"graph": graph}).get_json()
run = client.post(
    f"/workflows/{workflow['id']}/runs",
    json={"inputs": {"name": "Forge"}},
).get_json()
events = client.get(f"/runs/{run['id']}/events").get_json()["events"]
print(run["status"], run["outputs"], len(events))
assert run["status"] == "succeeded"
assert run["outputs"] == {"text": "Hello, Forge!"}
assert len(events) >= 3
