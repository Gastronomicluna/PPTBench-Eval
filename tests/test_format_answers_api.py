from typing import Any

import pytest

from src.shared.format_answers_api import format_answer


@pytest.mark.parametrize(
    "input_str,expected_output",
    [
        (
            '{"function1": "detect_face()", "function2": "detect_objects()"}',
            ["detect_face()", "detect_objects()"],
        ),
        (
            '{"function1": "process_image()", "function2": "analyze_data()"}',
            ["process_image()", "analyze_data()"],
        ),
        ('{"function1": "single_function()"}', ["single_function()"]),
    ],
)
def test_format_answer_success(input_str: str, expected_output: list[str]) -> None:
    """
    Test successful cases of format_answer function.

    Args:
        input_str: Input JSON string containing functions
        expected_output: Expected list of function strings
    """
    result = format_answer(input_str)
    assert result == expected_output


@pytest.mark.parametrize(
    "invalid_input",
    [
        "not a json string",
        '{"wrong_key": "function()"}',
        '{"function1": 123}',
        "[]",
        "null",
    ],
)
def test_format_answer_failure(invalid_input: str) -> None:
    """
    Test error cases of format_answer function.

    Args:
        invalid_input: Invalid input that should raise an exception
    """
    with pytest.raises(Exception):
        format_answer(invalid_input)


def test_format_answer_empty_dict() -> None:
    """Test format_answer with empty dictionary."""
    result = format_answer("{}")
    assert result == []


def test_format_answer_mixed_keys() -> None:
    """Test format_answer with mixed valid and invalid keys."""
    input_str = '{"function1": "first()", "invalid": "skip()", "function2": "last()"}'
    expected = ["first()", "last()"]
    result = format_answer(input_str)
    assert result == expected


@pytest.mark.parametrize(
    "invalid_input,expected_error",
    [
        (None, TypeError),
        (123, TypeError),
        ([], TypeError),
        ("", ValueError),
        ("   ", ValueError),
        ("not a json string", ValueError),
        ('{"wrong_key": "function()"}', ValueError),
        ('{"function1": 123}', ValueError),
        ('{"function1": ""}', ValueError),
        ('{"function1": "  "}', ValueError),
        ("[]", ValueError),
        ("null", ValueError),
    ],
)
def test_format_answer_specific_errors(
    invalid_input: Any, expected_error: Exception
) -> None:
    """
    Test specific error cases of format_answer function.

    Args:
        invalid_input: Invalid input that should raise an exception
        expected_error: Expected exception type
    """
    with pytest.raises(expected_error):
        format_answer(invalid_input)


def test_format_answer_function_ordering() -> None:
    """Test that functions are returned in correct order."""
    input_str = (
        '{"function2": "second()", "function1": "first()", ' '"function3": "third()"}'
    )
    expected = ["first()", "second()", "third()"]
    result = format_answer(input_str)
    assert result == expected
