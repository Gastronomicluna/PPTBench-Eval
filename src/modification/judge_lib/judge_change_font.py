from typing import Any, Dict, List, Tuple

from ...shared.pptx_api.api_executor import api_executor
from ..utils import get_font, get_font_from_shape, get_shape_from_presentation


def judge_answer_change_font(
    api_calls: List[str],
    shape_to_modify: Dict[str, Any],
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
    shape_id = shape_to_modify["shape_id"]

    # Execute the API calls
    modified_presentation_json = api_executor(
        lines=api_calls, json=presentation_json, mode="json"
    )
    if modified_presentation_json is None:
        return False, "Error executing API calls"

    # Get the shape from the slide
    llm_modified_shape = get_shape_from_presentation(
        slide_id=slide_id,
        shape_id=shape_id,
        presentation=modified_presentation_json,
    )
    llm_modified_font = get_font_from_shape(llm_modified_shape)
    
    if llm_modified_font is None:
        return False, "No font found in modified shape"
    if len(llm_modified_font) > 1:
        return False, "Multiple fonts found in modified shape"

    llm_modified_font_name = llm_modified_font.pop()

    # Get the font names from the ground truth
    gold_font = get_font(
        shape_id=shape_id,
        ground_truth=ground_truth,
    )

    if gold_font is None:
        return False, "No font found in ground truth"
    if len(gold_font) > 1:
        return False, "Multiple fonts found in ground truth"

    gold_font_name = gold_font.pop()

    if gold_font_name != llm_modified_font_name:
        return (
            False,
            f"Font mismatch: expected {gold_font_name}, got {llm_modified_font_name}",
        )

    return True, "Success"
