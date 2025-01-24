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


def calculate_position_diff(
    ground_truth_shape: Dict[str, Any],
    result_shape: Dict[str, Any],
) -> float:
    """
    Compare the ground truth shape with the result shape.

    Args:
        ground_truth_shape (Dict[str, Any]): The ground truth shape.
        result_shape (Dict[str, Any]): The result shape.

    Returns:
        float: The difference between the ground truth shape and the result shape.
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

    top_diff = abs(ground_truth_coordinates["top"] - result_coordinates["top"])

    left_diff = abs(ground_truth_coordinates["left"] - result_coordinates["left"])

    percentage_diff = top_diff / ground_truth_coordinates["height"]
    percentage_diff += left_diff / ground_truth_coordinates["width"]

    return percentage_diff


def compare_shape_position(
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
    percentage_diff = calculate_position_diff(ground_truth_shape, result_shape)

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

    return percentage_diff <= threshold and equal_height and equal_width
