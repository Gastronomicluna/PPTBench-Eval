import logging
from typing import Any, Dict, List

from ...shared.pptx_api.api_executor import api_executor
from ..utils import get_font, get_font_from_shape, get_shape_from_presentation


def judge_answer_change_font(
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
    # Get the slide ID from the ground truth
    slide_id = ground_truth.get("slide", {}).get("slide_id")

    # Get the shape ID from the ground truth
    shape_id = shape_to_modify["shape_id"]

    # Get the font names from the ground truth
    font = get_font(
        shape_id=shape_id,
        ground_truth=ground_truth,
    )

    if font is None:
        logging.error("Error getting font names from the ground truth.")
        return False
    if len(font) > 1:
        logging.error("More than one font name found in the ground truth.")
        return False

    font_name = font.pop()

    # Execute the API calls
    result_json = api_executor(lines=api_calls, json=json_data, mode="json")
    if result_json is None:
        logging.error("Error executing API calls, result is None.")
        return False

    # Get the shape from the slide
    result_shape = get_shape_from_presentation(
        slide_id=slide_id,
        shape_id=shape_id,
        presentation=result_json,
    )
    result_font = get_font_from_shape(result_shape)
    if result_font is None:
        logging.error("Error getting font names from the result JSON.")
        return False
    if len(result_font) > 1:
        logging.error("More than one font name found in the result JSON.")
        return False

    result_font_name = result_font.pop()

    return font_name == result_font_name
