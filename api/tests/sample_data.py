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


def sample_llm_graph(*, prompt: str = "Say hello to {name}") -> dict:
    return {
        "nodes": [
            {"id": "start_1", "data": {"type": "start"}},
            {"id": "llm_1", "data": {"type": "llm", "prompt": prompt}},
            {"id": "end_1", "data": {"type": "end"}},
        ],
        "edges": [
            {"id": "e1", "source": "start_1", "target": "llm_1"},
            {"id": "e2", "source": "llm_1", "target": "end_1"},
        ],
    }


def sample_if_else_graph(*, condition: str = "result = score >= 60") -> dict:
    return {
        "nodes": [
            {"id": "start_1", "data": {"type": "start"}},
            {"id": "if_1", "data": {"type": "if-else", "condition": condition}},
            {
                "id": "tpl_true",
                "data": {"type": "template", "template": "pass"},
            },
            {
                "id": "tpl_false",
                "data": {"type": "template", "template": "fail"},
            },
            {"id": "end_1", "data": {"type": "end"}},
        ],
        "edges": [
            {"id": "e0", "source": "start_1", "target": "if_1"},
            {
                "id": "e1",
                "source": "if_1",
                "target": "tpl_true",
                "source_handle": "true",
            },
            {
                "id": "e2",
                "source": "if_1",
                "target": "tpl_false",
                "source_handle": "false",
            },
            {"id": "e3", "source": "tpl_true", "target": "end_1"},
            {"id": "e4", "source": "tpl_false", "target": "end_1"},
        ],
    }
