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
    debug: bool = False,
) -> Union[Tuple[bool, str], Tuple[bool, str, float]]:
    """
    Judge the answer based on the API calls and ground truth.

    Args:
        api_calls (List[str]): The API calls made by the model.
        shape_to_modify (Dict[str, Any]): The shape to modify.
        json_data (Dict[str, Any]): The JSON data.
        presentation_json (Dict[str, Any]): The presentation JSON data.
        debug (bool, optional): Whether to return the score. Defaults to False.

    Returns:
        Union[Tuple[bool, str], Tuple[bool, str, float]]: 
            (success, message) or (success, message, score) if debug is True
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
        return (False, "Error executing API calls") if not debug else (False, "Error executing API calls", 1.0)

    shape_id = shape_to_modify["shape_id"]

    modified_shape = get_shape_from_presentation(
        slide_id=slide_id,
        shape_id=shape_id,
        presentation=modified_presentation_json,
    )

    ground_truth_shape = shape_to_modify

    # Compare the shapes
    flag, score = compare_shape_position(ground_truth_shape, modified_shape)

    if debug:
        return flag, "Success" if flag else f"Position difference too large: {score:.4f}", score
    return flag, "Success" if flag else f"Position difference too large: {score:.4f}"


def compare_shape_position(
    ground_truth_shape: Dict[str, Any],
    result_shape: Dict[str, Any],
    threshold: float = 0.001,
) -> Tuple[bool, float]:
    """
    Compare the ground truth shape with the result shape.

    Args:
        ground_truth_shape (Dict[str, Any]): The ground truth shape.
        result_shape (Dict[str, Any]): The result shape.

    Returns:
        bool: Whether the shapes are the same.
    """
    position_percentage_diff = calculate_position_diff(ground_truth_shape, result_shape)

    size_percentage_diff = calculate_size_diff(ground_truth_shape, result_shape)

    return (
        position_percentage_diff <= threshold and size_percentage_diff == 0,
        position_percentage_diff + size_percentage_diff,
    )
