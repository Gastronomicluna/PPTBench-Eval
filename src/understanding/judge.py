from pathlib import Path
from typing import Optional

import pandas as pd

from ..shared.utils import csv_to_df, df_to_csv


def judge_answer_df(
    csv_path: Path | str,
    overwrite: bool = False,
) -> pd.DataFrame:
    """
    Judge the answers in the CSV file and save results back to the same file.

    Args:
        csv_path (Union[Path, str]): Path to CSV file for input and output.
        overwrite (bool): Whether to overwrite existing output file.

    Returns:
        pd.DataFrame: DataFrame with judged answers.
    """
    csv_path = Path(csv_path)
    answers_df = csv_to_df(csv_path)

    if answers_df is None:
        raise ValueError("The input DataFrame is empty.")

    if (
        "task" not in answers_df.columns
        or "ground_truth" not in answers_df.columns
        or "answer" not in answers_df.columns
    ):
        raise ValueError(
            "The input DataFrame must contain 'task', 'ground_truth', "
            "and 'answer' columns."
        )

    # Process answers
    answers_df["is_correct"] = answers_df.apply(
        lambda row: judge_answer(row["ground_truth"], row["answer"]),
        axis=1,
    )

    # Save results
    if overwrite:
        df_to_csv(answers_df, csv_path)

    return answers_df


def judge_answer(
    ground_truth: str,
    answer: Optional[str],
) -> bool:
    """
    Judge the answer based on the task and the ground truth.

    Args:
        task (str): The task type.
        ground_truth (str): The ground truth answer.
        answer (str): The answer from the model.

    Returns:
        bool: Whether the answer is correct.
    """
    return str(ground_truth).strip().lower() == str(answer).strip().lower()
