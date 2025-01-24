from typing import Any, Dict, List

from ...shared.pptx_api.api_executor import api_executor
from ..utils import (
    calculate_position_diff,
    calculate_size_diff,
    get_shape_from_presentation,
)


def judge_answer_resize(
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

    # Compare the shapes
    return compare_shape_size(ground_truth_shape, modified_shape)


def compare_shape_size(
    ground_truth_shape: Dict[str, Any],
    result_shape: Dict[str, Any],
    threshold: float = 0.001,
) -> bool:
    """
    Compare the ground truth shape with the result shape.

    Args:
        ground_truth_shape (Dict[str, Any]): The ground truth shape.
        result_shape (Dict[str, Any]): The result shape.

    Returns:
        bool: Whether the shapes are the same.
    """

    # Get the position of the shapes
    ground_truth_position = ground_truth_shape["position"]
    result_position = result_shape["position"]

    # Get the size of the shapes
    ground_truth_size = ground_truth_shape["size"]
    result_size = result_shape["size"]

    # Calculate the difference in position
    position_diff = calculate_position_diff(ground_truth_position, result_position)

    # Calculate the difference in size
    size_diff = calculate_size_diff(ground_truth_size, result_size)

    # Check if the difference is within the threshold
    return position_diff <= threshold and size_diff <= threshold
