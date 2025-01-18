from typing import Any, Dict, List
from ...shared.pptx_api.api_executor import api_executor

from ..utils import get_slide_from_presentation, has_out_of_bounds, has_overlap


def judge_answer(
    api_calls: List[str],
    ground_truth: Dict[str, Any],
    json_data: Dict[str, Any],
    json_path: str,
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
    modified_presentation = api_executor(api_calls, json_path=json_path, mode="json")
    modified_slide = get_slide_from_presentation(
        slide_id=slide_id,
        presentation=modified_presentation,
    )
    
    # Get slides
    original_slide = json_data.get("slide", {})
    gold_slide = ground_truth.get("slide", {})
    
    gold_shape = get_new_shape_from_slide(
        modified_slide_json=gold_slide,
        original_slide_json=original_slide,
    )
    
    modified_shape = get_new_shape_from_presentation(
        modified_presentation=modified_presentation,
        original_slide_json=original_slide,
        ground_truth=ground_truth,
    )
    
    # Check if the shape is out of bounds or has overlap
    if has_out_of_bounds(modified_shape):
        return False
    if has_overlap(modified_shape):
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
    # Compare the shapes
    pass

def get_new_shape_from_presentation(
    modified_presentation: Dict[str, Any],
    original_slide_json: Dict[str, Any],
    ground_truth: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Get the new shape from the modified presentation JSON data.

    Args:
        modified_presentation (Dict[str, Any]): The modified presentation JSON data.
        original_slide_json (Dict[str, Any]): The original slide JSON data.
        ground_truth (Dict[str, Any]): The ground truth JSON data.

    Returns:
        Dict[str, Any]: The new shape data.
    """
    # Get the slide ID from the ground truth
    slide_id = ground_truth.get("slide", {}).get("slide_id")

    # Get the modified slide JSON data
    modified_slide_json = get_slide_from_presentation(
        slide_id=slide_id,
        presentation=modified_presentation,
    )

    # Get the new shape from the modified slide
    new_shape = get_new_shape_from_slide(
        original_slide_json=original_slide_json,
        modified_slide_json=modified_slide_json,
    )

    return new_shape


def get_new_shape_from_slide(
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
