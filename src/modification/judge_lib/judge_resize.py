from typing import Any, Dict, List, Tuple

from ...shared.pptx_api.api_executor import api_executor
from ..utils import (
    calculate_size_diff,
    get_shape_from_presentation,
    produce_modified_presentation_json,
    get_shape_from_slide,
)


def judge_answer_resize(
    api_calls: List[str],
    shape_to_modify: Dict[str, Any],
    ground_truth: Dict[str, Any],
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

    produced_presentation_json = produce_modified_presentation_json(
        presentation=presentation_json,
        slide_id=slide_id,
        slide_json=slide_json,
    )

    try:
        modified_presentation_json = api_executor(
            lines=api_calls,
            json=produced_presentation_json,
            mode="json",
        )
    except Exception as e:
        return False, f"Error executing API calls: {str(e)}"

    shape_id = shape_to_modify["shape_id"]

    modified_shape = get_shape_from_presentation(
        slide_id=slide_id,
        shape_id=shape_id,
        presentation=modified_presentation_json,
    )
    # print("Modified shape:", modified_shape)
    ground_truth_slide = ground_truth.get("slide", {})
    if ground_truth_slide is None:
        raise ValueError("The slide data is not found in the ground truth.")
    ground_truth_shape = get_shape_from_slide(
        shape_id=shape_id,
        slide=ground_truth_slide,
    )
    print("Ground truth shape:", ground_truth_shape)
    # Compare the shapes
    return compare_shape_size(ground_truth_shape, modified_shape)


def compare_shape_size(
    ground_truth_shape: Dict[str, Any],
    result_shape: Dict[str, Any],
    threshold: float = 0.1,
) -> Tuple[bool, str]:
    """
    Compare the ground truth shape with the result shape.

    Args:
        ground_truth_shape (Dict[str, Any]): The ground truth shape.
        result_shape (Dict[str, Any]): The result shape.
        threshold (float, optional): Maximum allowed difference. Defaults to 0.1.

    Returns:
        Tuple[bool, str]: Success flag and error message.
    """
    # Get the position of the shapes
    # position_percentage_diff = calculate_position_diff(ground_truth_shape, result_shape)
    size_percentage_diff = calculate_size_diff(ground_truth_shape, result_shape)

    # if position_percentage_diff > threshold:
    #     return (
    #         False,
    #         f"Position changed unexpectedly (diff: {position_percentage_diff:.4f})",
    #     )
    if size_percentage_diff > threshold:
        return False, f"Size difference too large (diff: {size_percentage_diff:.4f})"

    return True, "Success"
