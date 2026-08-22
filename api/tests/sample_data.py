"""Reusable sample payloads for tests."""


def sample_graph() -> dict:
    return {
        "nodes": [
            {"id": "start_1", "data": {"type": "start"}},
            {
                "id": "tpl_1",
                "data": {"type": "template", "template": "Hello, {name}!"},
            },
            {"id": "end_1", "data": {"type": "end"}},
        ],
        "edges": [
            {"id": "e1", "source": "start_1", "target": "tpl_1"},
            {"id": "e2", "source": "tpl_1", "target": "end_1"},
        ],
    }


def sample_code_graph(*, code: str = "result = name.upper()") -> dict:
    return {
        "nodes": [
            {"id": "start_1", "data": {"type": "start"}},
            {"id": "code_1", "data": {"type": "code", "code": code}},
            {"id": "end_1", "data": {"type": "end"}},
        ],
        "edges": [
            {"id": "e1", "source": "start_1", "target": "code_1"},
            {"id": "e2", "source": "code_1", "target": "end_1"},
        ],
    }
