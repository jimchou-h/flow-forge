"""LLM provider abstractions."""

from __future__ import annotations

from typing import Protocol


class LlmProvider(Protocol):
    """同步文本生成；本 slice 不流式。"""

    def complete(self, prompt: str) -> str:
        """把渲染后的 prompt 交给模型，返回生成文本。"""
