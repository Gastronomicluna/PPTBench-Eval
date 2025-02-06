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

        if "answer" in df.columns and not overwrite:
            if not df["answer"].isna().all():
                return df

        try:
            df["answer"] = df.apply(
                lambda row: format_answer_function(row["llm_answer"], row["subcategory"]),
                axis=1,
            )
        except KeyError as e:
            raise ValueError(f"Required column missing: {e}")
        except Exception as e:
            raise ValueError(f"Error formatting answers: {e}")

        if not df_to_csv(df, csv_path):
            raise ValueError("Failed to save the formatted answers.")

        return df

    except Exception as e:
        raise Exception(f"Error processing CSV file: {e}")
