import json
import logging
import traceback
from typing import Any, Dict, List


def parse_api_calls(answer: str) -> List[str]:
    """
    Parse api calls from answer string.

    Args:
        answer (str): Raw answer string containing API calls.

    Returns:
        List[str]: List of API call strings.
    """
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

    # If all else fails, split by newline and clean
    return [call.strip() for call in answer.split("\n") if call.strip()]


def parse_json_answer(
    answer: str,
) -> Dict[str, Any]:
    """
    Parse the answer from the model into a dictionary.

    Args:
        answer (str): The answer from the model, potentially escaped JSON string.

    Returns:
        Dict[str, Any]: The parsed answer.
    """
    try:
        parsed_answer = json.loads(answer)
    except json.JSONDecodeError:
        # Try unescaping the string first
        try:
            decoded_str = answer.encode().decode("unicode_escape")
            parsed_answer = json.loads(decoded_str)
        except (json.JSONDecodeError, UnicodeError) as e:
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
