from .utils import csv_to_df, df_to_csv
from pathlib import Path
import pandas as pd
from typing import Callable
def format_answer_csv(
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
    """
    df = csv_to_df(csv_path)
    if df is None:
        raise ValueError("The CSV file is empty.")

    if "answer" in df.columns and not overwrite:
        # Check if answer column has any non-null values
        if not df["answer"].isna().all():
            return df

    df["answer"] = df.apply(
        lambda row: format_answer_function(row["llm_answer"], row["subcategory"]),
        axis=1,
    )

    if df_to_csv(df, csv_path):
        return df
    else:
        raise ValueError("Failed to save the formatted answers.")