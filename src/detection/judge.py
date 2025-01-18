import json
from pathlib import Path
from typing import Dict, Optional, Union

import pandas as pd
from thefuzz import fuzz

from ..shared.parse_answer import parse_json_answer
from ..shared.utils import csv_to_df, df_to_csv


def judge_answer_df(
    csv_path: Union[Path, str],
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
        "subcategory" not in answers_df.columns
        or "ground_truth" not in answers_df.columns
        or "answer" not in answers_df.columns
    ):
        raise ValueError(
            "The input DataFrame must contain 'subcategory', 'ground_truth', "
            "and 'answer' columns."
        )

    # Process answers
    answers_df["is_correct"] = answers_df.apply(
        lambda row: judge_answer(
            row["subcategory"], row["ground_truth"], row["answer"]
        ),
        axis=1,
    )

    # Save results
    if overwrite:
        df_to_csv(answers_df, csv_path)

    return answers_df


def judge_answer(
    subcategory: str,
    ground_truth: str,
    answer: Optional[str],
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
    if answer is None:
        return False

    judge_function = {
        "content extraction": fuzzy_match,
        "layout detection": compare_coordinate,
        "style detection": exact_match,
    }
    if subcategory not in judge_function:
        raise ValueError(f"Unknown subcategory: {subcategory}")

    if subcategory == "layout detection":
        try:
            ground_truth = parse_json_answer(ground_truth)
            answer = json.loads(answer)
            # print("Ground Truth:" , ground_truth)
            # print("Answer:", answer)
        except (ValueError, SyntaxError) as e:
            print(e)
            return False

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
    ground_truth: Dict[str, int],
    answer: Dict[str, int],
) -> bool:
    """
    Compare the ground truth coordinates with the detected coordinates.

    Args:
        ground_truth (Dict[str, int]): The ground truth coordinates.
        answer (Dict[str, int]): The detected coordinates.

    Returns:
        bool: Whether the coordinates match.

    Raises:
        ValueError: If ground_truth contains invalid keys.
    """
    valid_keys = {"top", "left", "width", "height"}
    invalid_keys = set(answer.keys()) - valid_keys

    if invalid_keys:
        # print(f"Invalid keys in ground_truth: {invalid_keys}")
        return False

    # check if the valid keys are present in the answer
    if not valid_keys.issubset(answer.keys()):
        # print(f"Missing keys in answer: {valid_keys - set(answer.keys())}")
        return False

    if ground_truth["top"] != answer["top"]:
        return False
    if ground_truth["left"] != answer["left"]:
        return False
    if ground_truth["width"] != answer["width"]:
        return False
    if ground_truth["height"] != answer["height"]:
        return False
    return True


def exact_match(
    ground_truth: str | int | float,
    answer: str | int | float,
) -> bool:
    """
    Exact matching function to compare the ground truth and the answer.

    Args:
        ground_truth (Union[str, int, float]): The ground truth answer.
        answer (Union[str, int, float]): The answer from the model.

    Returns:
        bool: Whether the answer is correct.
    """
    # Try numeric comparison first
    try:
        return float(ground_truth) == float(answer)
    except (ValueError, TypeError):
        # Fall back to string comparison if not numeric
        return str(ground_truth).strip().lower() == str(answer).strip().lower()
