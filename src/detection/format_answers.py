import json
from pathlib import Path
from typing import Any, Dict, Literal, Optional, Union

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
        lambda row: format_answer(row["llm_answer"], row["subcategory"]),
        axis=1,
    )

    if df_to_csv(df, csv_path):
        return df
    else:
        raise ValueError("Failed to save the formatted answers.")


def format_answer(
    answer: str,
    subcategory: Literal["content extraction", "layout detection", "style detection"],
) -> Union[str, Dict[str, Any]]:
    """
    Format the extracted content for the detection tasks.

    Args:
        answer (str): The extracted content.
        subcategory (str): The subcategory type.

    Returns:
        Union[str, Dict[str, Any]]: The formatted answer.
    """
    if subcategory == "content extraction":
        return format_content_extraction_answer(answer)
    elif subcategory == "layout detection":
        return format_layout_detection_answer(answer)
    elif subcategory == "style detection":
        return format_style_detection_answer(answer)
    else:
        raise ValueError(f"Unknown subcategory: {subcategory}")


def format_content_extraction_answer(
    answer: str,
) -> Optional[str]:
    """
    Format the extracted content for content extraction tasks.

    Args:
        answer (str): The extracted content.

    Returns:
        str: The formatted answer.
    """
    try:
        json_answer = parse_json_answer(answer)
        answer = json_answer["answer"]
    except Exception:
        return None
    return answer


def format_style_detection_answer(
    answer: str,
) -> Optional[Union[str, int]]:
    """
    Format the extracted style for style detection tasks.

    Args:
        answer (str): The extracted style.

    Returns:
        Union[str, int]: The formatted answer.
    """
    try:
        json_answer = parse_json_answer(answer)
        answer = json_answer["answer"]
    except Exception:
        return None
    return answer


def format_layout_detection_answer(
    answer: str,
) -> str:
    """
    Format the detected layout for layout detection tasks.

    Args:
        answer (str): The detected layout.

    Returns:
        Dict[str, int]: The formatted answer.
    """
    try:
        json_answer = parse_json_answer(answer)
    except Exception:
        return None
    return json.dumps(json_answer)
