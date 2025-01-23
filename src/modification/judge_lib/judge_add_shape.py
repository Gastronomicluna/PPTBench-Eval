import logging
from typing import Any, Dict, List

from ...shared.pptx_api.api_executor import api_executor
from ...shared.utils import fuzzy_match
from ..utils import get_slide_from_presentation, has_out_of_bounds, has_overlap


def judge_answer_add_shape(
    api_calls: List[str],
    ground_truth: Dict[str, Any],
    presentation_json: Dict[str, Any],
) -> bool:
    """
    Judge the answer based on the API calls and ground truth.

    Args:
        api_calls (List[str]): The API calls made by the model.
        ground_truth (Dict[str, Any]): The ground truth JSON data.
        presentation_json (Dict[str, Any]): The JSON data, the original

    Returns:
        bool: Whether the answer is correct.
    """
    slide_height = presentation_json.get("slide_height")
    slide_width = presentation_json.get("slide_width")
    # Get slide ID from the ground truth
    slide_id = ground_truth.get("slide", {}).get("slide_id")

    # Get original slides
    original_slide = get_slide_from_presentation(
        slide_id=slide_id,
        presentation=presentation_json,
    )

    # Execute the API calls
    llm_modified_presentation = api_executor(
        lines=api_calls, json=presentation_json, mode="json"
    )
    if llm_modified_presentation is None:
        logging.error("Error executing API calls, result is None.")
        return False

    llm_modified_slide = get_slide_from_presentation(
        slide_id=slide_id,
        presentation=llm_modified_presentation,
    )

    # Check if the slide has out of bounds or has overlap
    if has_out_of_bounds(
        slide_json=llm_modified_slide,
        slide_height=slide_height,
        slide_width=slide_width,
    ):
        return False
    if has_overlap(slide_json=llm_modified_slide):
        return False

    # Get the gold slide
    gold_slide = ground_truth.get("slide", {})
    # if gold_slide is None:
    #     raise ValueError("Gold slide is None.")
    # Get the gold added shape
    gold_shape = get_new_shape(
        modified_slide_json=gold_slide,
        original_slide_json=original_slide,
    )
    # assert gold_shape is not None, "Gold shape is None."
    # Get the llm modified shape
    llm_added_shape = get_new_shape(
        modified_slide_json=llm_modified_slide,
        original_slide_json=original_slide,
    )

    return compare_shape(gold_shape, llm_added_shape)


def compare_shape(
    original_shape: Dict[str, Any],
    modified_shape: Dict[str, Any],
    text_threshold: float = 0.95,
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
    if (
        original_text
        and modified_text
        and fuzzy_match(
            ground_truth=original_text,
            answer=modified_text,
            threshold=text_threshold,
        )
    ):
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
