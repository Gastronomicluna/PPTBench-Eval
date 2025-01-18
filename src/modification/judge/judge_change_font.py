import logging
from typing import Any, Dict, List

from ...shared.pptx_api.api_executor import api_executor
from ..utils import get_font, get_font_from_shape, get_shape_from_presentation


def judge_answer_change_font(
    api_calls: List[str],
    shape_to_modify: Dict[str, Any],
    ground_truth: Dict[str, Any],
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
    # Get the slide ID and shape ID from the ground truth
    slide_id = ground_truth.get("slide", {}).get("slide_id")
    shape_id = shape_to_modify["shape_id"]

    # Execute the API calls
    llm_modified_presentation = api_executor(
        lines=api_calls, json=presentation_json, mode="json"
    )
    if llm_modified_presentation is None:
        logging.error("Error executing API calls, result is None.")
        return False

    # Get the shape from the slide
    llm_modified_shape = get_shape_from_presentation(
        slide_id=slide_id,
        shape_id=shape_id,
        presentation=llm_modified_presentation,
    )
    llm_modified_font = get_font_from_shape(llm_modified_shape)
    if llm_modified_font is None:
        logging.error("Error getting font names from the result JSON.")
        return False
    if len(llm_modified_font) > 1:
        logging.error("More than one font name found in the result JSON.")
        return False

    llm_modified_font_name = llm_modified_font.pop()

    # Get the font names from the ground truth
    gold_font = get_font(
        shape_id=shape_id,
        ground_truth=ground_truth,
    )

    if gold_font is None:
        logging.error("Error getting font names from the ground truth.")
        return False
    if len(gold_font) > 1:
        logging.error("More than one font name found in the ground truth.")
        return False

    gold_font_name = gold_font.pop()

    return gold_font_name == llm_modified_font_name
