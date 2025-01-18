from typing import Any, Dict, List

from ...shared.pptx_api.api_executor import api_executor
from ..utils import get_shape_from_presentation, get_shape_from_slide
import logging


def judge_answer_resize(
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
        lines=api_calls, 
        json=presentation_json, 
        mode="json"
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
    
    # Get the ground truth shape
    ground_truth_shape = get_shape_from_presentation(
        slide_id=slide_id,
        shape_id=shape_id,
        presentation=presentation_json,
    )

    # Compare the shapes
    return compare_shape_size(ground_truth_shape, llm_modified_shape)


def compare_shape_size(
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


pass
