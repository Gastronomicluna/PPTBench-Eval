import json
from typing import Any, Dict, List, Optional, Union


def parse_api_calls(answer: str) -> Optional[List[str]]:
    """
    Parse API calls from answer string, handling various formats.

    Args:
        answer (str): Raw answer string containing API calls.

    Returns:
        Optional[List[str]]: List of API call strings.
    """
    # Handle case where answer is already a list of strings
    if isinstance(answer, list):
        if all(isinstance(x, str) for x in answer):
            return answer

    try:
        # Try parsing as JSON first
        parsed_answer = parse_json_answer(answer)

        # Handle the preferred format: dict with "functions" key
        if isinstance(parsed_answer, dict) and "functions" in parsed_answer:
            functions = parsed_answer["functions"]
            if isinstance(functions, list) and all(
                isinstance(x, str) for x in functions
            ):
                return functions

        # Handle list format
        if isinstance(parsed_answer, list):
            if all(isinstance(x, str) for x in parsed_answer):
                return parsed_answer

        # Handle legacy format (dictionary with function1, function2, etc.)
        if isinstance(parsed_answer, dict):
            function_keys = sorted(
                k for k in parsed_answer.keys() if k.startswith("function")
            )
            if function_keys:
                return [parsed_answer[k] for k in function_keys]

        # If we got here, the format wasn't recognized
        raise ValueError(f"Unrecognized API calls format: {parsed_answer}")

    except Exception as e:
        raise ValueError(f"Error parsing API calls: {str(e)}")


def parse_json_answer(
    answer: str,
) -> Union[Dict[str, Any], List[str]]:
    """
    Parse the answer from the model into a dictionary or list.
    Handles various JSON formats including the new {"functions": [...]} format.

    Args:
        answer (str): The answer from the model, potentially escaped JSON string.

    Returns:
        Union[Dict[str, Any], List[str]]: The parsed answer as dictionary or list.
    """
    if not isinstance(answer, str) and (
        isinstance(answer, dict) or isinstance(answer, list)
    ):
        return answer  # Already parsed

    try:
        # First try direct JSON parsing
        parsed_answer = json.loads(answer)
        return parsed_answer
    except json.JSONDecodeError:
        # Try unescaping the string first
        try:
            decoded_str = answer.encode().decode("unicode_escape")
            parsed_answer = json.loads(decoded_str)
            return parsed_answer
        except (json.JSONDecodeError, UnicodeError):
            # Try Python literal evaluation as fallback
            try:
                parsed_answer = eval(answer)  # For list/dict literals
                if not isinstance(parsed_answer, (list, dict)):
                    raise ValueError(
                        f"Expected list or dict, got {type(parsed_answer)}"
                    )
                return parsed_answer
            except Exception as e:
                raise ValueError(f"Error parsing JSON answer: {str(e)}")


def main():
    # Test the parse functions with different formats
    test_cases = [
        '{"functions": ["create_slide()", "add_text_box(50000, 50000, 8000000, 1000000, \'Text\')"]}',
        '["create_slide()", "add_text_box(50000, 50000, 8000000, 1000000, \'Text\')"]',
        '{"function1": "create_slide()", "function2": "add_text_box(50000, 50000, 8000000, 1000000, \'Text\')"}',
    ]

    for i, test_case in enumerate(test_cases):
        print(f"\nTest Case {i+1}:")
        try:
            parsed = parse_json_answer(test_case)
            print(f"Parsed JSON: {parsed}")

            functions = parse_api_calls(test_case)
            print(f"Extracted functions: {functions}")
        except Exception as e:
            print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
