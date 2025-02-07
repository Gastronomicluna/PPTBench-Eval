from typing import Any, Dict, List, Tuple

from ...shared.pptx_api.api_executor import api_executor
from ..utils import get_slide_from_presentation


def judge_answer_change_font(
    api_calls: List[str],
    ground_truth: Dict[str, Any],
    presentation_json: Dict[str, Any],
) -> Tuple[bool, str]:
    """
    Judge the answer based on the API calls and ground truth.

    Args:
        api_calls (List[str]): The API calls made by the model.
        shape_to_modify (Dict[str, Any]): The shape to modify.
        ground_truth (Dict[str, Any]): The ground truth JSON data.
        presentation_json (Dict[str, Any]): The presentation JSON data.

    Returns:
        Tuple[bool, str]: Whether the answer is correct and reason if incorrect.
    """
    # Get the slide ID and shape ID from the ground truth
    slide_id = ground_truth.get("slide", {}).get("slide_id")

    # Execute the API calls
    try:
        modified_presentation_json = api_executor(
            lines=api_calls, json=presentation_json, mode="json"
        )
    except Exception as e:
        return False, f"Error executing API calls: {str(e)}"

    gold_slide = ground_truth.get("slide", {})

    modified_slide = get_slide_from_presentation(
        presentation=modified_presentation_json,
        slide_id=slide_id,
    )

    if modified_slide is None:
        return False, "Modified slide not found"

    # Compare the slides
    is_same, reason = compare_slides(gold_slide, modified_slide)

    return is_same, reason


def compare_slides(
    slide1: Dict[str, Any],
    slide2: Dict[str, Any],
) -> Tuple[bool, str]:
    """
    Compare two slides to determine if they are the same.

    Args:
        slide1 (Dict[str, Any]): The first slide.
        slide2 (Dict[str, Any]): The second slide.

    Returns:
        Tuple[bool, str]: Whether the slides are the same and reason if not.
    """
    if slide1 == slide2:
        return True, "Slides are the same"
    else:
        return False, "Slides are different"
