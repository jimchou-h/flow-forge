"""LLM node: prompt validation and execution."""

from __future__ import annotations

from typing import Any, Mapping

from flow_forge.core.workflow.providers.base import LlmProvider

MAX_PROMPT_LENGTH = 8192


def validate_llm_prompt(prompt: str | None) -> None:
    """图校验与执行前均可调用。"""

    if not prompt or not prompt.strip():
        raise ValueError("llm node requires non-empty data.prompt")
    if len(prompt) > MAX_PROMPT_LENGTH:
        raise ValueError(f"prompt exceeds max length ({MAX_PROMPT_LENGTH} bytes)")


def render_llm_prompt(prompt_template: str, variables: Mapping[str, Any]) -> str:
    """与 template 节点相同：缺 key 即 KeyError。"""

    return prompt_template.format_map(_SafeDict(variables))


def execute_llm(
    prompt_template: str,
    variables: Mapping[str, Any],
    provider: LlmProvider,
) -> str:
    """渲染 prompt 并调用 provider。"""

    validate_llm_prompt(prompt_template)
    rendered = render_llm_prompt(prompt_template, variables)
    return provider.complete(rendered)


class _SafeDict(dict[str, Any]):
    def __missing__(self, key: str) -> str:
        raise KeyError(key)
