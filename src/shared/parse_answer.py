import json
from typing import Any, Dict
import logging
import re 
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
            unescaped_answer = answer.encode().decode("unicode_escape")
            parsed_answer = json.loads(unescaped_answer)
        except (json.JSONDecodeError, UnicodeError) as e:
            cleaned_answer = clean_json_string(answer)
            print(cleaned_answer)
            try:
                parsed_answer = json.loads(cleaned_answer)
            except json.JSONDecodeError as e:
                parsed_answer = {"error": "Failed to parse the answer."}
                logging.error(f"Failed to parse the answer: {str(e)}")

    return parsed_answer


def clean_json_string(
    json_string: str,
) -> str:
    """
    Clean the JSON string by unescaping it.

    Args:
        json_string (str): The JSON string to clean.

    Returns:
        str: The cleaned JSON string.
    """
    decoded_str = json_string.encode().decode("unicode_escape")
    sanitized_str = re.sub(r'""([^"]+)""', r'"\1"', decoded_str)

    return sanitized_str

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
            # print(parsed_answer)
        except Exception as e:
            print(f"Error parsing answer: {str(e)}")


if __name__ == "__main__":
    main()
