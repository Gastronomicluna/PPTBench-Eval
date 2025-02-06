from pathlib import Path
from typing import Callable, Union
import pandas as pd

def format_answer_csv_shared(
    format_func: Callable,
    csv_path: Path,
    overwrite: bool = False,
) -> pd.DataFrame:
    """Format answers in the CSV file using the provided formatting function.

    Args:
        format_func: Function to format individual answers
        csv_path: Path to the CSV file
        overwrite: Whether to overwrite existing formatted answers

    Returns:
        DataFrame with formatted answers
    """
    df = pd.read_csv(csv_path)
    
    # Initialize columns with appropriate dtypes
    if "formatted_answer" not in df.columns:
        df["formatted_answer"] = pd.NA
    if "error" not in df.columns:
        df["error"] = pd.NA.astype(str)  # Initialize as string type

    # Only process rows that need formatting
    rows_to_process = df[
        df["formatted_answer"].isna() if not overwrite else pd.Series([True] * len(df))
    ]

    for _, row in rows_to_process.iterrows():
        try:
            formatted = format_func(row["answer"], row["subcategory"])
            df.at[row.name, "formatted_answer"] = formatted
            df.at[row.name, "error"] = pd.NA
        except Exception as e:
            df.at[row.name, "formatted_answer"] = pd.NA
            df.at[row.name, "error"] = str(e)  # Cast to string type explicitly

    df.to_csv(csv_path, index=False)
    return df
