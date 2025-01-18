from typing import Any, Dict, List

from ...shared.pptx_api.api_executor import api_executor
from ..utils import get_shape_from_presentation, get_shape_from_slide


def judge_answer_reposition(
    api_calls: List[str],
    shape_to_modify: Dict[str, Any],
    ground_truth: Dict[str, Any],
    json_data: Dict[str, Any],
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
    result_json = api_executor(
        lines=api_calls, 
        json=json_data, 
        mode="json"
    )
    # Get the shape from the ground truth
    result_shape = get_shape_from_presentation(
        slide_id=slide_id,
        shape_id=shape_to_modify["shape_id"],
        presentation=result_json,
    )

    # Compare the shapes
    return compare_shape_position(ground_truth_shape, result_shape)


def compare_shape_position(
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
    ground_truth_coordinates = {
        "height": ground_truth_shape["height"],
        "width": ground_truth_shape["width"],
        "top": ground_truth_shape["top"],
        "left": ground_truth_shape["left"],
    }

    result_coordinates = {
        "height": result_shape["height"],
        "width": result_shape["width"],
        "top": result_shape["top"],
        "left": result_shape["left"],
    }

    equal_height = ground_truth_coordinates["height"] == result_coordinates["height"]
    equal_width = ground_truth_coordinates["width"] == result_coordinates["width"]

    top_diff = abs(ground_truth_coordinates["top"] - result_coordinates["top"])
    equal_top = top_diff <= threshold * ground_truth_coordinates["height"]

    left_diff = abs(ground_truth_coordinates["left"] - result_coordinates["left"])
    equal_left = left_diff <= threshold * ground_truth_coordinates["width"]

    return equal_height and equal_width and equal_top and equal_left
