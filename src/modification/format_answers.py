import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

from ..shared.format_answer_csv import format_answer_csv_shared
from ..shared.parse_answer import parse_json_answer


def format_answer_csv(
    csv_path: Path,
    overwrite: bool = False,
) -> pd.DataFrame:
    """
    Format the answers in the CSV file.

    Args:
        csv_path (Path): Path to the CSV file.
        overwrite (bool, optional): Whether to overwrite existing answers.
            If False and answer column exists with values, skip processing.
            Defaults to False.

    Returns:
        pd.DataFrame: DataFrame with formatted answers.
    """
    return format_answer_csv_shared(format_answer, csv_path, overwrite)


def format_answer(
    answer: str,
    subcategory: Optional[str] = None,
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
        # print(json_answer)
        functions = extract_functions_from_json(json_answer)
        result_json = {"functions": functions}
    except Exception:
        return {}
    return json.dumps(result_json)


def extract_functions_from_json(
    json_data: Dict[str, Any],
) -> List[str]:
    """
    Extract the functions from the JSON data.

    Args:
        json_data (Dict[str, Any]): The JSON data containing numbered function keys
            (e.g., "function1", "function2", etc.) with function call strings as values.

    Returns:
        List[str]: The list of function call strings in order.
    """
    functions = []
    if isinstance(json_data, dict):
        # Sort keys to maintain order (function1, function2, etc.)
        for key in sorted(json_data.keys()):
            if key.startswith("function"):
                functions.append(json_data[key])
    return functions


def main() -> None:
    format_answer_csv(Path("data/modification_results.csv"), overwrite=True)


if __name__ == "__main__":
    main()
