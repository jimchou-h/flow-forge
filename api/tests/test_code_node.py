"""Code node unit tests."""

import pytest

from flow_forge.core.workflow.nodes.code import execute_code, validate_code_source


def test_execute_code_transforms_variable() -> None:
    result = execute_code("result = name.upper()", {"name": "flow"})
    assert result == "FLOW"


def test_execute_code_must_assign_result() -> None:
    with pytest.raises(ValueError, match="result"):
        execute_code("x = 1", {"name": "a"})


def test_execute_code_syntax_error() -> None:
    with pytest.raises(SyntaxError):
        execute_code("result = (", {})


def test_validate_rejects_import() -> None:
    with pytest.raises(ValueError, match="forbidden"):
        validate_code_source("import os\nresult = 1")
