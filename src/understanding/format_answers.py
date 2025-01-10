from pathlib import Path
from typing import Any, Dict, Optional, Union

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
    llm_answer: Union[str, Dict[str, Any]],
) -> Optional[str]:
    """
    Format the LLM answer.

    Args:
        llm_answer (Union[str, Dict[str, Any]]): The LLM answer.

    Returns:
        Optional[str]: The formatted answer.
    """
    answer = parse_json_answer(llm_answer)
    if answer is None:
        return None

    return answer["answer"]
