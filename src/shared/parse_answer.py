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
            decoded_str = answer.encode().decode("unicode_escape")
            parsed_answer = json.loads(decoded_str)
        except (json.JSONDecodeError, UnicodeError) as e:
            decoded_str = answer.encode().decode("unicode_escape")
            print(decoded_str)
            cleaned_answer = escape_quotes_in_values(decoded_str)
            print(cleaned_answer)
            try:
                parsed_answer = json.loads(cleaned_answer)
            except json.JSONDecodeError as e:
                parsed_answer = {"error": "Failed to parse the answer."}
                logging.error(f"Failed to parse the answer: {str(e)}")

    return parsed_answer


def escape_quotes_in_values(decoded_str: str) -> str:
    # Matches a JSON-style string: " (any non-quote or backslash OR backslash + any char)* "
    # e.g. "some text with possible \"internal\" quotes"
    pattern = r'("([^"\\]|\\.)*")'

    def replacer(match):
        # The entire quoted string, including the outer quotes
        full_str = match.group(1)
        # Remove outer quotes
        inner = full_str[1:-1]
        # Escape any unescaped " inside the value
        inner_escaped = re.sub(r'(?<!\\)"', r'\"', inner)
        # Put the outer quotes back
        return f'"{inner_escaped}"'

    return re.sub(pattern, replacer, decoded_str)

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

def test() -> None:
    string = """{
    "function1": "choose_slide(256)",
    "function2": "add_text_box(609480, 3327431, 7772400, 400000, "2007 California Children's Dental Disease Program")"
}"""
    print(escape_quotes_in_values(string))

if __name__ == "__main__":
    # main()
    test()
