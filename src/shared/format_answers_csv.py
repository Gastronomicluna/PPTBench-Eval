from pathlib import Path
from typing import Callable

import pandas as pd

from .utils import csv_to_df, df_to_csv


def format_answer_csv_shared(
    format_answer_function: Callable,
    csv_path: Path,
    overwrite: bool = False,
) -> pd.DataFrame:
    """
    Format the answers in the CSV file.

    Args:
        format_answer_function (Callable): Function to format individual answers.
        csv_path (Path): Path to the CSV file.
        overwrite (bool, optional): Whether to overwrite existing answers.
            If False and answer column exists with values, skip processing.
            Defaults to False.

    Returns:
        pd.DataFrame: DataFrame with formatted answers.

    Raises:
        ValueError: If the CSV file is empty or cannot be processed.
        Exception: For other unexpected errors during processing.
    """
    try:
        df = csv_to_df(csv_path)
        if df is None:
            raise ValueError("The CSV file is empty.")

        # Initialize error column with string dtype if it doesn't exist
        if "error" not in df.columns:
            df["error"] = pd.Series(dtype="string")
        else:
            # Ensure existing error column is string type
            df["error"] = df["error"].astype("string")

        if "answer" in df.columns and not overwrite:
            if not df["answer"].isna().all():
                return df

        def apply_format_safely(row):
            # Skip if there's already an error
            if pd.notna(row["error"]):
                return pd.NA

            try:
                if "subcategory" in df.columns:
                    return format_answer_function(
                        row["llm_answer"], row["subcategory"]
                    )
                return format_answer_function(row["llm_answer"])
            except Exception as e:
                df.at[row.name, "error"] = str(e)
                return pd.NA

        df["answer"] = df.apply(apply_format_safely, axis=1)

        if not df_to_csv(df, csv_path):
            raise ValueError("Failed to save the formatted answers.")

        return df

    except Exception as e:
        raise Exception(f"Error processing CSV file: {e}")
