from pathlib import Path
from typing import Optional

import pandas as pd

from ..shared.format_answers_csv import format_answer_csv_shared
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
    llm_answer: str,
) -> Optional[str]:
    """
    Format the LLM answer.

    Args:
        llm_answer (Union[str, Dict[str, Any]]): The LLM answer.

    Returns:
        Optional[str]: The formatted answer.
    """
    if not isinstance(llm_answer, str):
        raise ValueError("Expected LLM answer to be a string.")
    if not llm_answer.strip():
        raise ValueError("Expected LLM answer to be a non-empty string.")

    try:
        answer = parse_json_answer(llm_answer)
        # print(answer)
        if answer is None:
            return None
        return answer["answer"]

    except Exception as e:
        raise ValueError(f"Error parsing LLM answer: {str(e)}")
