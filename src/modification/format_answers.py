from typing import Any, Dict, List

from ..shared.parse_answer import parse_json_answer
from ..shared.utils import csv_to_df, df_to_csv


def format_answer(
    answer: str,
) -> List[str]:
    """
    Format the extracted functions for the detection tasks.

    Args:
        answer (str): The extracted functions.

    Returns:
        List[str]: The formatted functions.
    """
    try:
        json_answer = parse_json_answer(answer)
        functions = extract_functions_from_json(json_answer)
    except Exception:
        return []
    return functions

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
