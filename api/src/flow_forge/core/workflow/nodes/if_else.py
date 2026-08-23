"""If/Else condition evaluation (controlled namespace, bool result)."""

from __future__ import annotations

from typing import Any

from flow_forge.core.workflow.nodes.code import FORBIDDEN_PATTERNS, SAFE_BUILTINS

MAX_CONDITION_LENGTH = 1024


def validate_condition_source(source: str | None) -> None:
    """图校验与执行前均可调用。"""

    if not source or not source.strip():
        raise ValueError("if-else node requires non-empty data.condition")
    if len(source) > MAX_CONDITION_LENGTH:
        raise ValueError(f"condition exceeds max length ({MAX_CONDITION_LENGTH} bytes)")
    lowered = source.lower()
    for pattern in FORBIDDEN_PATTERNS:
        if pattern in lowered:
            raise ValueError(f"forbidden pattern in condition: {pattern.strip()}")


def evaluate_condition(source: str, variables: dict[str, Any]) -> bool:
    """在受控命名空间执行条件；用户 MUST 赋值 ``result`` 为 bool。"""

    validate_condition_source(source)
    locals_dict: dict[str, Any] = dict(variables)
    globals_dict = {"__builtins__": SAFE_BUILTINS}
    exec(source, globals_dict, locals_dict)  # noqa: S102 — 学习向受控 exec
    if "result" not in locals_dict:
        raise ValueError("condition must assign a result variable")
    value = locals_dict["result"]
    if not isinstance(value, bool):
        raise ValueError("condition result must be a bool")
    return value
