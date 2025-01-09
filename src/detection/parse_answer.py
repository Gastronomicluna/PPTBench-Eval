import json
from typing import Any, Dict


def parse_answer(
    answer: str,
) -> Dict[str, Any]:
    """
    Parse the answer from the model into a dictionary.

    Args:
        answer (str): The answer from the model.

    Returns:
        Dict[str, Any]: The parsed answer.
    """
    try:
        parsed_answer = json.loads(answer)
    except json.JSONDecodeError:
        parsed_answer = {"error": "Failed to parse the answer."}

    return parsed_answer


def main():
    # Test the parse_answer function
    answer = '{"dominant_font": "Arial"}'
    parsed_answer = parse_answer(answer)
    print(parsed_answer)


if __name__ == "__main__":
    main()
