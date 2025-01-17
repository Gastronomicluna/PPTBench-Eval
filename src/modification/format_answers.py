from typing import Any, Dict, List
import json
from ..shared.parse_answer import parse_json_answer


def format_answer(
    answer: str,
) -> Dict[str, Any]:
    """
    Format the extracted functions for the detection tasks.

    Args:
        answer (str): The extracted functions.

    Returns:
        Dict[str, Any]: The formatted answer.
    """
    try:
        json_answer = parse_json_answer(answer)
        functions = extract_functions_from_json(json_answer)
        result_json = {"functions": functions}
    except Exception:
        return {}
    return json.dumps(result_json)


def extract_functions_from_json(
    json_data: List[Dict[str, Any]],
) -> List[str]:
    """
    Extract the functions from the JSON data.

    Args:
        json_data (List[Dict[str, Any]]): The JSON data.

    Returns:
        List[str]: The list of functions.
    """
    functions = []
    for value in json_data:
        functions.append(value["function"])
    return functions
