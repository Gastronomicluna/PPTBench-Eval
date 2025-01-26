from typing import Any, Dict, List, Tuple, Union

from ...shared.pptx_api.api_executor import api_executor
from ..utils import (
    calculate_position_diff,
    calculate_size_diff,
    get_shape_from_presentation,
)


def judge_answer_reposition(
    api_calls: List[str],
    shape_to_modify: Dict[str, Any],
    json_data: Dict[str, Any],
    presentation_json: Dict[str, Any],
) -> Tuple[bool, str]:
    """
    Judge the answer based on the API calls and ground truth.

    Args:
        api_calls (List[str]): The API calls made by the model.
        shape_to_modify (Dict[str, Any]): The shape to modify.
        json_data (Dict[str, Any]): The JSON data.
        presentation_json (Dict[str, Any]): The presentation JSON data.

    Returns:
        Tuple[bool, str]: Whether the answer is correct and reason if incorrect.
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
    if modified_presentation_json is None:
        return False, "Error executing API calls"

    shape_id = shape_to_modify["shape_id"]

    modified_shape = get_shape_from_presentation(
        slide_id=slide_id,
        shape_id=shape_id,
        presentation=modified_presentation_json,
    )

    ground_truth_shape = shape_to_modify

    # Compare the shapes
    flag, message, score = compare_shape_position(ground_truth_shape, modified_shape)
    return flag, f"{message} (diff: {score:.4f})"


def compare_shape_position(
    ground_truth_shape: Dict[str, Any],
    result_shape: Dict[str, Any],
    threshold: float = 0.001,
) -> Tuple[bool, str, float]:
    """
    Compare the ground truth shape with the result shape.

    Args:
        ground_truth_shape (Dict[str, Any]): The ground truth shape.
        result_shape (Dict[str, Any]): The result shape.
        threshold (float, optional): Maximum allowed position difference. Defaults to 0.001.

    Returns:
        Tuple[bool, str, float]: Success flag, error message, and difference score.
    """
    position_percentage_diff = calculate_position_diff(ground_truth_shape, result_shape)
    size_percentage_diff = calculate_size_diff(ground_truth_shape, result_shape)
    
    total_diff = position_percentage_diff + size_percentage_diff
    
    if size_percentage_diff > 0:
        return False, "Shape size was modified", total_diff
    if position_percentage_diff > threshold:
        return False, "Position difference exceeds threshold", total_diff
        
    return True, "Success", total_diff
