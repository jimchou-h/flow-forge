"""Workflow HTTP create/get."""

from sample_data import sample_graph


def test_create_and_get_workflow(client) -> None:
    create = client.post("/workflows", json={"graph": sample_graph()})
    assert create.status_code == 201
    body = create.get_json()
    assert "id" in body
    workflow_id = body["id"]

    fetched = client.get(f"/workflows/{workflow_id}")
    assert fetched.status_code == 200
    assert fetched.get_json()["graph"] == sample_graph()


def test_create_rejects_unknown_node_type(client) -> None:
    graph = sample_graph()
    graph["nodes"][1]["data"]["type"] = "tool"
    response = client.post("/workflows", json={"graph": graph})
    assert response.status_code == 400
