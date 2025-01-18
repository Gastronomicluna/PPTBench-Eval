from typing import Any, Dict, List

from ...shared.pptx_api.api_executor import api_executor
from ..utils import get_slide_from_presentation, has_out_of_bounds, has_overlap


def judge_answer_add_shape(
    api_calls: List[str],
    ground_truth: Dict[str, Any],
    json_data: Dict[str, Any],
) -> bool:
    """
    Judge the answer based on the API calls and ground truth.

    Args:
        api_calls (List[str]): The API calls made by the model.
        ground_truth (Dict[str, Any]): The ground truth JSON data.
        json_data (Dict[str, Any]): The JSON data, the original
        json_path (str): The path to the JSON data.

    Returns:
        bool: Whether the answer is correct.
    """
    # Get slide ID from the ground truth
    slide_id = ground_truth.get("slide", {}).get("slide_id")
    modified_presentation = api_executor(
        lines=api_calls, 
        json=json_data, 
        mode="json"
    )

    modified_slide = get_slide_from_presentation(
        slide_id=slide_id,
        presentation=modified_presentation,
    )

    # Get slides
    original_slide = json_data.get("slide", {})
    gold_slide = ground_truth.get("slide", {})

    gold_shape = get_new_shape(
        modified_slide_json=gold_slide,
        original_slide_json=original_slide,
    )

    modified_shape = get_new_shape(
        modified_slide_json=modified_slide,
        original_slide_json=original_slide,
    )

    # Check if the slide has out of bounds or has overlap
    if has_out_of_bounds(modified_slide):
        return False
    if has_overlap(modified_slide):
        return False

    return compare_shape(gold_shape, modified_shape)


def compare_shape(
    original_shape: Dict[str, Any],
    modified_shape: Dict[str, Any],
) -> bool:
    """
    Compare the original shape with the modified shape.

    Args:
        original_shape (Dict[str, Any]): The original shape data.
        modified_shape (Dict[str, Any]): The modified shape data.

    Returns:
        bool: Whether the shapes are the same.
    """
    # Compare text if it exists in either shape
    original_text = original_shape.get("text")
    modified_text = modified_shape.get("text")

    # If text exists in one shape but not the other, return False
    if bool(original_text) != bool(modified_text):
        return False

    # If both have text, compare them
    if original_text and modified_text and original_text != modified_text:
        return False

    # Compare images
    original_image = original_shape.get("image_path")
    modified_image = modified_shape.get("image_path")

    # If image exists in one shape but not the other, return False
    if bool(original_image) != bool(modified_image):
        return False

    # If both have images, compare them
    if original_image and modified_image and original_image != modified_image:
        return False


def get_new_shape(
    original_slide_json: Dict[str, Any],
    modified_slide_json: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Get the new shape from the modified slide JSON data.

    Args:
        original_slide_json (Dict[str, Any]): The original slide JSON data.
        modified_slide_json (Dict[str, Any]): The modified slide JSON data.

    Returns:
        Dict[str, Any]: The new shape data.
    """
    # Get the shapes from the original slide
    original_shapes = original_slide_json.get("shapes", [])

    # Get the shapes from the modified slide
    modified_shapes = modified_slide_json.get("shapes", [])

    # Find the new shape
    new_shape = None
    for shape in modified_shapes:
        if shape not in original_shapes:
            new_shape = shape
            break

    return new_shape
