from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

from .parse_answer import parse_json_answer
from .utils import csv_to_df, df_to_csv


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
    df = csv_to_df(csv_path)
    if df.empty:
        raise ValueError("The CSV file is empty.")

    if "answer" in df.columns and not overwrite:
        # Check if answer column has any non-null values
        if not df["answer"].isna().all():
            return df

    df["answer"] = df.apply(
        lambda row: format_answer(row["llm_answer"]),
        axis=1,
    )

    if df_to_csv(df, csv_path):
        return df
    else:
        raise ValueError("Failed to save the formatted answers.")


def format_answer(
    answer: str,
) -> List[str]:
    """
    Format the extracted functions for the detection tasks.

    Args:
        answer (str): The extracted functions.

    Returns:
        List[str]: The formatted list of functions.
    """
    try:
        json_answer = parse_json_answer(answer)
        functions = extract_functions_from_json(json_answer)
        return functions
    except Exception:
        return []


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
    # format_answer_csv(Path("data/modification_results.csv"), overwrite=True)
    from pathlib import Path

    from .utils import csv_to_df

    # Test the parse_answer function
    csv_path = Path("data/modification_results.csv")

    df = csv_to_df(csv_path)
    answers = df["llm_answer"]
    for answer in answers:
        try:
            parsed_answer = format_answer(answer)
            print(parsed_answer)
        except Exception as e:
            print(f"Error parsing answer: {str(e)}")


if __name__ == "__main__":
    main()
