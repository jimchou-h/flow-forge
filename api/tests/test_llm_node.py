"""LLM node and provider unit tests."""

import pytest

from flow_forge.core.workflow.nodes.llm import execute_llm, validate_llm_prompt
from flow_forge.core.workflow.providers.openai_compatible import OpenAiCompatibleProvider
from flow_forge.core.workflow.providers.stub import StubLlmProvider


def test_stub_provider_echoes_prompt() -> None:
    provider = StubLlmProvider()
    assert provider.complete("hello") == "Echo: hello"


def test_execute_llm_renders_and_calls_provider() -> None:
    text = execute_llm("Hi {name}", {"name": "Forge"}, StubLlmProvider())
    assert text == "Echo: Hi Forge"


def test_execute_llm_missing_variable_raises() -> None:
    with pytest.raises(KeyError):
        execute_llm("Hi {name}", {}, StubLlmProvider())


def test_validate_rejects_empty_prompt() -> None:
    with pytest.raises(ValueError, match="prompt"):
        validate_llm_prompt("   ")


def test_openai_provider_parses_response() -> None:
    class FakeResponse:
        def __init__(self, payload: bytes) -> None:
            self._payload = payload

        def read(self) -> bytes:
            return self._payload

        def __enter__(self):
            return self

        def __exit__(self, *args: object) -> None:
            return None

    def fake_urlopen(request, timeout=60.0):  # noqa: ARG001
        assert request.full_url.endswith("/chat/completions")
        return FakeResponse(
            b'{"choices":[{"message":{"content":"Hello from model"}}]}',
        )

    import urllib.request

    original = urllib.request.urlopen
    urllib.request.urlopen = fake_urlopen  # type: ignore[assignment]
    try:
        provider = OpenAiCompatibleProvider(
            base_url="https://example.com/v1",
            api_key="test-key",
            model="gpt-test",
        )
        assert provider.complete("ping") == "Hello from model"
    finally:
        urllib.request.urlopen = original
