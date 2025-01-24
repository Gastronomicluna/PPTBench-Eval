from typing import Any, Dict, List

from ...shared.pptx_api.api_executor import api_executor
from ..utils import get_shape_from_presentation


def judge_answer_reposition(
    api_calls: List[str],
    shape_to_modify: Dict[str, Any],
    json_data: Dict[str, Any],
    presentation_json: Dict[str, Any],
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
    # Get slide ID
    slide_json = json_data.get("slide", {})
    if slide_json is None:
        raise ValueError("The slide JSON data is not found in the JSON data.")

    slide_id = slide_json.get("slide_id")
    if slide_id is None:
        raise ValueError("The slide ID is not found in the shape to modify.")

    produced_presentation_json = produced_presentation_json(
        presentation=presentation_json,
        slide_id=slide_id,
        slide_json=slide_json,
    )

    modified_presentation_json = api_executor(
        lines=api_calls,
        json=produced_presentation_json,
        mode="json",
    )

    shape_id = shape_to_modify["shape_id"]

    modified_shape = get_shape_from_presentation(
        slide_id=slide_id,
        shape_id=shape_id,
        presentation=modified_presentation_json,
    )

    ground_truth_shape = shape_to_modify

    return compare_shape_position(ground_truth_shape, modified_shape)


def shape_reposition_score(
    ground_truth_shape: Dict[str, Any], result_shape: Dict[str, Any]
) -> float:
    """
    Calculate a similarity score between two shapes based on their position.

    Args:
        ground_truth_shape (Dict[str, Any]): The ground truth shape.
        result_shape (Dict[str, Any]): The result shape.

    Returns:
        float: Score from 0 to 1, where 1 means exact match.
    """
    gt_coords = {
        "height": ground_truth_shape["height"],
        "width": ground_truth_shape["width"],
        "top": ground_truth_shape["top"],
        "left": ground_truth_shape["left"],
    }

    res_coords = {
        "height": result_shape["height"],
        "width": result_shape["width"],
        "top": result_shape["top"],
        "left": result_shape["left"],
    }

    # Calculate relative differences
    top_diff = abs(gt_coords["top"] - res_coords["top"]) / gt_coords["height"]
    left_diff = abs(gt_coords["left"] - res_coords["left"]) / gt_coords["width"]

    # If dimensions don't match exactly, penalize the score
    dim_penalty = 1.0
    if (
        gt_coords["height"] != res_coords["height"]
        or gt_coords["width"] != res_coords["width"]
    ):
        dim_penalty = 0.7

    # Calculate position score (exponential decay based on difference)
    position_score = dim_penalty * (1.0 - (top_diff + left_diff) / 2)

    # Clamp score between 0 and 1
    return max(0.0, min(1.0, position_score))


def compare_shape_position(
    ground_truth_shape: Dict[str, Any],
    result_shape: Dict[str, Any],
    threshold: float = 0.95,
) -> bool:
    """
    Compare the ground truth shape with the result shape.

    Args:
        ground_truth_shape (Dict[str, Any]): The ground truth shape.
        result_shape (Dict[str, Any]): The result shape.
        threshold (float): Minimum score threshold for positions to be considered equal.

    Returns:
        bool: Whether the shapes are similar enough based on threshold.
    """
    score = shape_reposition_score(ground_truth_shape, result_shape)
    return score >= threshold
