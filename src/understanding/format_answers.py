from pathlib import Path
from typing import Any, Dict, Optional, Union

import pandas as pd

from ..shared.parse_answer import parse_json_answer
from ..shared.format_answer_csv import format_answer_csv

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
    return format_answer_csv(format_answer, csv_path, overwrite)


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
