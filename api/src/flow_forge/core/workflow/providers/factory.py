"""Construct LlmProvider from environment."""

from __future__ import annotations

import os

from flow_forge.core.workflow.providers.base import LlmProvider
from flow_forge.core.workflow.providers.openai_compatible import OpenAiCompatibleProvider
from flow_forge.core.workflow.providers.stub import StubLlmProvider


def create_llm_provider_from_env() -> LlmProvider:
    """Env 齐全时用 OpenAI 兼容 API，否则 stub。"""

    base_url = os.environ.get("FLOW_FORGE_LLM_BASE_URL", "").strip()
    api_key = os.environ.get("FLOW_FORGE_LLM_API_KEY", "").strip()
    model = os.environ.get("FLOW_FORGE_LLM_MODEL", "").strip()
    if base_url and api_key and model:
        return OpenAiCompatibleProvider(base_url=base_url, api_key=api_key, model=model)
    return StubLlmProvider()
