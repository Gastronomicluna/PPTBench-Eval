from typing import List

from thefuzz import fuzz

from src.detection.utils import SUBCATEGORY_JUDGE_FUNCTION
def judge_answer(
    task: str,
    ground_truth: str,
    answer: str,
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
    if task not in SUBCATEGORY_JUDGE_FUNCTION:
        raise ValueError(f"Unknown task: {task}")
    return SUBCATEGORY_JUDGE_FUNCTION[task](ground_truth, answer)

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
