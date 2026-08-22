"""Factory for LlmProvider from environment."""

from flow_forge.core.workflow.providers.factory import create_llm_provider_from_env
from flow_forge.core.workflow.providers.openai_compatible import OpenAiCompatibleProvider
from flow_forge.core.workflow.providers.stub import StubLlmProvider


def test_factory_uses_stub_when_env_incomplete(monkeypatch) -> None:
    monkeypatch.delenv("FLOW_FORGE_LLM_BASE_URL", raising=False)
    monkeypatch.delenv("FLOW_FORGE_LLM_API_KEY", raising=False)
    monkeypatch.delenv("FLOW_FORGE_LLM_MODEL", raising=False)
    assert isinstance(create_llm_provider_from_env(), StubLlmProvider)


def test_factory_uses_openai_when_env_complete(monkeypatch) -> None:
    monkeypatch.setenv("FLOW_FORGE_LLM_BASE_URL", "https://example.com/v1")
    monkeypatch.setenv("FLOW_FORGE_LLM_API_KEY", "sk-test")
    monkeypatch.setenv("FLOW_FORGE_LLM_MODEL", "gpt-test")
    provider = create_llm_provider_from_env()
    assert isinstance(provider, OpenAiCompatibleProvider)
