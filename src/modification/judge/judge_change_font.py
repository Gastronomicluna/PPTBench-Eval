from ...shared.pptx_api.api_executor import api_executor
from typing import Any, Dict, List, Literal, Optional
from ..utils import get_font, get_shape_from_presentation
import logging
def judge_answer(
    api_calls: List[str],
    shape_to_modify: Dict[str, Any],
    ground_truth: Dict[str, Any],
    json_path: str,
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
    # Execute the API calls
    result_json = api_executor(
        lines=api_calls,
        json_path=json_path,
        mode="json",
    )
    if result_json is None:
        logging.error("Error executing API calls, result is None.")
        return False
    
    # Get the slide ID from the ground truth
    slide_id = ground_truth.get("slide", {}).get("slide_id")
    
    # Get the shape ID from the ground truth
    shape_id = shape_to_modify["shape_id"]
        
    # Get the font names from the ground truth
        
    # Get the shape from the slide
    result_shape = get_shape_from_presentation(
        slide_id=slide_id,
        shape_id=shape_id,
        presentation=result_json,
    )

