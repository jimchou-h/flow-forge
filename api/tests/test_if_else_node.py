"""If/Else condition unit tests."""

import pytest

from flow_forge.core.workflow.nodes.if_else import evaluate_condition, validate_condition_source


def test_evaluate_condition_true() -> None:
    assert evaluate_condition("result = score >= 60", {"score": 80}) is True


def test_evaluate_condition_false() -> None:
    assert evaluate_condition("result = score >= 60", {"score": 40}) is False


def test_evaluate_condition_non_bool_raises() -> None:
    with pytest.raises(ValueError, match="bool"):
        evaluate_condition("result = 1", {})


def test_evaluate_condition_missing_result_raises() -> None:
    with pytest.raises(ValueError, match="result"):
        evaluate_condition("x = True", {})


def test_validate_rejects_empty() -> None:
    with pytest.raises(ValueError, match="condition"):
        validate_condition_source("  ")
