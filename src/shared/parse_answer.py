import json
import logging
from typing import Any, Dict
import traceback

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
            logging.error(f"Error parsing JSON answer: {str(e)}")
            print(traceback.format_exc())
            parsed_answer = {}

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
