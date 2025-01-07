from typing import Any, Dict, List


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
    pass


def compare_coordinates(
    ground_truth: List[Dict[str, Any]],
    answer: List[Dict[str, Any]],
) -> bool:
    """
    Compare the ground truth coordinates with the detected coordinates.

    Args:
        ground_truth (list[dict]): The ground truth coordinates.
        answer (list[dict]): The detected coordinates.

    Returns:
        bool: Whether the coordinates match.
    """
    pass


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
    pass
