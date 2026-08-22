"""Deterministic LLM provider for tests and local dev without API keys."""

from __future__ import annotations


class StubLlmProvider:
    """固定前缀 + prompt，便于断言且无需网络。"""

    prefix: str = "Echo: "

    def complete(self, prompt: str) -> str:
        return f"{self.prefix}{prompt}"
