from typing import List

import pandas as pd
from thefuzz import fuzz


def judge_answer_df(
    answers_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Judge the answers in the DataFrame.

    Args:
        answers_df (pd.DataFrame): The DataFrame containing the answers.

    Returns:
        pd.DataFrame: The DataFrame with the judged results.
    """
    if (
        "subcategory" not in answers_df.columns
        or "ground_truth" not in answers_df.columns
        or "llm_answer" not in answers_df.columns
    ):
        raise ValueError(
            "The input DataFrame must contain 'subcategory', 'ground_truth', and 'llm_answer' columns."
        )

    answers_df["is_correct"] = answers_df.apply(
        lambda row: judge_answer(
            row["subcategory"], row["ground_truth"], row["llm_answer"]
        ),
        axis=1,
    )
    return answers_df


def judge_answer(
    subcategory: str,
    ground_truth: str,
    answer: str,
) -> bool:
    """
    Judge the answer based on the subcategory and the ground truth.

    Args:
        subcategory (str): The subcategory type.
        ground_truth (str): The ground truth answer.
        answer (str): The answer from the model.

    Returns:
        bool: Whether the answer is correct.
    """
    judge_function = {
        "content extraction": fuzzy_match,
        "layout detection": compare_coordinate,
        "style detection": exact_match,
    }
    if subcategory not in judge_function:
        raise ValueError(f"Unknown subcategory: {subcategory}")
    return judge_function[subcategory](ground_truth, answer)


def fuzzy_match(
    ground_truth: str,
    answer: str,
    threshold: float = 0.9,
) -> bool:
    """
    Fuzzy matching function to compare the ground truth and the answer.

    Args:
        ground_truth (str): The ground truth answer.
        answer (str): The answer from the model.
        threshold (float): The threshold for the fuzzy matching
    Returns:
        bool: Whether the answer is correct.
    """
    ratio = fuzz.ratio(ground_truth, answer) / 100
    return ratio >= threshold


def compare_coordinate(
    ground_truth: List[int],
    answer: List[int],
) -> bool:
    """
    Compare the ground truth coordinates with the detected coordinates.

    Args:
        ground_truth (list[dict]): The ground truth coordinates.
        answer (list[dict]): The detected coordinates.

    Returns:
        bool: Whether the coordinates match.
    """
    for gt, ans in zip(ground_truth, answer):
        if gt != ans:
            return False
    return True


def exact_match(
    ground_truth: str,
    answer: str,
) -> bool:
    """
    Exact matching function to compare the ground truth and the answer.

    Args:
        ground_truth (str): The ground truth answer.
        answer (str): The answer from the model.

    Returns:
        bool: Whether the answer is correct.
    """
    return ground_truth.strip().lower() == answer.strip().lower()
