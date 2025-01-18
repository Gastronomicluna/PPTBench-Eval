from typing import Any, Dict
from ..utils import get_slide_from_presentation

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
    new_shape = get_new_shape(
        original_slide_json=original_slide_json,
        modified_slide_json=modified_slide_json,
    )

    return new_shape
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