import json
from typing import Any, Dict, List, Optional, Union


def parse_api_calls(answer: str) -> Optional[List[str]]:
    """
    Parse API calls from answer string, handling both list and dictionary formats.

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
        calls = answer
        if isinstance(calls, list):
            # Handle the case where we have a list of strings
            if all(isinstance(x, str) for x in calls):
                return calls
            # Handle the case where we have a string representation of a list
            if len(calls) == 1 and isinstance(calls[0], str):
                try:
                    inner_calls = eval(
                        calls[0]
                    )  # Safe here since we know it's a list literal
                    if isinstance(inner_calls, list):
                        return inner_calls
                except Exception as e:
                    raise ValueError(f"Error parsing inner API calls: {str(e)}")
    except json.JSONDecodeError:
        # If not JSON, try evaluating as a Python literal
        try:
            calls = eval(answer)  # Safe here since we expect a list literal
            if isinstance(calls, list):
                return calls
        except Exception as e:
            raise ValueError(f"Error parsing API calls: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error parsing API calls: {str(e)}")


def parse_json_answer(
    answer: str,
) -> Union[Dict[str, Any], List[str]]:
    """
    Parse the answer from the model into a dictionary or list.

    Args:
        answer (str): The answer from the model, potentially escaped JSON string.

    Returns:
        Union[Dict[str, Any], List[str]]: The parsed answer as dictionary or list.
    """
    try:
        if isinstance(answer, str):
            parsed_answer = json.loads(answer)
        else:
            parsed_answer = answer
    except json.JSONDecodeError:
        # Try unescaping the string first
        try:
            decoded_str = answer.encode().decode("unicode_escape")
            parsed_answer = json.loads(decoded_str)
        except (json.JSONDecodeError, UnicodeError) as e:
            # Try Python literal evaluation as fallback
            try:
                parsed_answer = eval(answer)  # For list/dict literals
                if not isinstance(parsed_answer, (list, dict)):
                    raise ValueError(f"Expected list or dict, got {type(parsed_answer)}")
            except Exception:
                raise ValueError(f"Error parsing JSON answer: {str(e)}")

    return parsed_answer


def main():
    from pathlib import Path

    from .utils import csv_to_df

    # Test the parse_answer function
    csv_path = Path("data/modification_results.csv")

    df = csv_to_df(csv_path)
    answers = df["llm_answer"]
    for answer in answers:
        try:
            parsed_answer = parse_json_answer(answer)
            print(parsed_answer)
        except Exception as e:
            print(f"Error parsing answer: {str(e)}")


if __name__ == "__main__":
    main()
