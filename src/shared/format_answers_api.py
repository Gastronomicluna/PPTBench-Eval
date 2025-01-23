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
    try:
        df = csv_to_df(csv_path)
        if df is None:
            raise ValueError("The CSV file is empty.")

        # Initialize columns with correct dtypes
        if "error" not in df.columns:
            df["error"] = pd.Series(dtype="string")
        
        if "answer" not in df.columns:
            df["answer"] = pd.Series(dtype="object")
        elif not overwrite:
            if not df["answer"].isna().all():
                return df

        def apply_format_safely(row):
            # Skip if there's already an error
            if pd.notna(row["error"]):
                return None

            try:
                if pd.isna(row["llm_answer"]):
                    return None
                result = format_answer(str(row["llm_answer"]))
                return result if result else None
            except Exception as e:
                idx = pd.Index([row.name], dtype=df.index.dtype)
                df.loc[idx, "error"] = str(e)
                return None

        # Apply formatting and ensure results are stored as objects
        results = df.apply(apply_format_safely, axis=1)
        df["answer"] = results.astype("object")

        if not df_to_csv(df, csv_path):
            raise ValueError("Failed to save the formatted answers.")

        return df

    except Exception as e:
        raise Exception(f"Error processing CSV file: {e}")


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
    except Exception as e:
        raise Exception(f"Error formatting answer: {e}")


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
    else:
        raise ValueError("Invalid JSON data format.")
    return functions


def main() -> None:
    csv_path = Path("data/modification_results/claude-3-5-sonnet-20241022.csv")
    df = csv_to_df(csv_path=csv_path, list_columns=["answer"])
    row = df[df["hash"] == "2bea6a2949d62d49f4773bc977326625"].iloc[0]
    print(row)
    answer_str = row["llm_answer"]
    print(answer_str)
    functions = row["answer"]
    print(functions)
    assert functions == format_answer(answer_str)


if __name__ == "__main__":
    main()
