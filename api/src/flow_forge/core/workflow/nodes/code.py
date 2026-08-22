"""Code node execution (learning-oriented controlled namespace)."""

from __future__ import annotations

from typing import Any

# 学习向上限：非生产级隔离
MAX_CODE_LENGTH = 4096

FORBIDDEN_PATTERNS = (
    "__import__",
    "open(",
    "import ",
    "from ",
    "exec(",
    "eval(",
    "compile(",
    "globals(",
    "locals(",
)

SAFE_BUILTINS: dict[str, Any] = {
    "len": len,
    "str": str,
    "int": int,
    "float": float,
    "bool": bool,
    "list": list,
    "dict": dict,
    "min": min,
    "max": max,
    "sum": sum,
    "abs": abs,
    "round": round,
}


def validate_code_source(source: str) -> None:
    """校验源码长度与静态禁止项（图校验与执行前均可调用）。"""

    if not source or not source.strip():
        raise ValueError("code node requires non-empty data.code")
    if len(source) > MAX_CODE_LENGTH:
        raise ValueError(f"code exceeds max length ({MAX_CODE_LENGTH} bytes)")
    lowered = source.lower()
    for pattern in FORBIDDEN_PATTERNS:
        if pattern in lowered:
            raise ValueError(f"forbidden pattern in code: {pattern.strip()}")


def execute_code(source: str, variables: dict[str, Any]) -> Any:
    """在受控命名空间中执行用户代码；用户 MUST 赋值 ``result``。"""

    validate_code_source(source)
    locals_dict: dict[str, Any] = dict(variables)
    globals_dict = {"__builtins__": SAFE_BUILTINS}
    exec(source, globals_dict, locals_dict)  # noqa: S102 — 学习向受控 exec
    if "result" not in locals_dict:
        raise ValueError("code must assign a result variable")
    return locals_dict["result"]
