from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

from ...shared.pptx_api.api_executor import api_executor
from ...shared.utils import build_json_path
from ..utils import get_shape_from_presentation, get_shape_from_slide


def judge_answer_resize(
    df: pd.DataFrame,
    json_dir: Path = Path("data/json"),
) -> pd.DataFrame:
    """
    Judge the answers in the DataFrame and save results back to the same file.

    Args:
        df (pd.DataFrame): DataFrame with answers.
        json_path (str): Path to the JSON file.

    Returns:
        pd.DataFrame: DataFrame with judged answers.
    """
    # Process answers
    df["is_correct"] = df.apply(
        lambda row: judge_answer(
            api_calls=row["api_calls"],
            shape_to_modify=row["shape_to_modify"],
            ground_truth=row["ground_truth"],
            json_path=build_json_path(file_hash=row["file_hash"], json_dir=json_dir),
        ),
        axis=1,
    )

    return df


def judge_answer(
    api_calls: List[str],
    shape_to_modify: Dict[str, Any],
    ground_truth: Dict[str, Any],
    json_path: str,
) -> bool:
    """
    Judge the answer based on the API calls and ground truth.

    Args:
        api_calls (List[str]): The API calls made by the model.
        shape_to_modify (Dict[str, Any]): The shape to modify.
        ground_truth (Dict[str, Any]): The ground truth JSON data.
        json_path (str): The path to the JSON data.

    Returns:
        bool: Whether the answer is correct.
    """
    # Get ground truth shape
    slide = ground_truth.get("slide", {})
    ground_truth_shape = get_shape_from_slide(
        shape_id=shape_to_modify["shape_id"],
        slide=slide,
    )

    # Get the slide ID from the ground truth
    slide_id = ground_truth.get("slide", {}).get("slide_id")

    # Execute the API calls
    result_json = api_executor(api_calls, json_path=json_path, mode="json")

    # Get the shape from the ground truth
    result_shape = get_shape_from_presentation(
        slide_id=slide_id,
        shape_id=shape_to_modify["shape_id"],
        presentation=result_json,
    )

    # Compare the shapes
    return compare_shape_size(ground_truth_shape, result_shape)


def compare_shape_size(
    ground_truth_shape: Dict[str, Any],
    result_shape: Dict[str, Any],
    threshold: float = 0.01,
) -> bool:
    """
    Compare the ground truth shape with the result shape.

    Args:
        ground_truth_shape (Dict[str, Any]): The ground truth shape.
        result_shape (Dict[str, Any]): The result shape.

    Returns:
        bool: Whether the shapes are the same.
    """


pass
