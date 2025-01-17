from typing import Any, Dict, List
from pathlib import Path
import pandas as pd

from ..shared.parse_answer import parse_json_answer
from ..shared.utils import csv_to_df, df_to_csv


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
    if df is None:
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
    except Exception:
        return {}
    return {"functions": functions}


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
