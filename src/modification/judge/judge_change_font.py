from ...shared.pptx_api.api_executor import api_executor
from typing import Any, Dict, List, Literal, Optional
import traceback
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
    
    # Get the slide from the result
    slide = None
    for s in result_json.get("slides", []):
        if s.get("slide_id") == slide_id:
            slide = s
            break
    
    if slide is None:
        logging.error(f"Could not find slide with ID {slide_id} in result JSON.")
        return False
        
    # Get the shape from the slide
    result_shape = None
    for s in slide.get("shapes", []):
        if s.get("shape_id") == shape_id:
            result_shape = s
            break
        
    if result_shape is None:
        logging.error(f"Could not find shape with ID {shape_id} in result JSON.")
        return False
    
    # Get the ground truth font name
    pass

def get_font(
    shape_id: int,
    ground_truth: Dict[str, Any],
) -> set:
    """
    Get the font names from the ground truth for a specific shape.

    Args:
        shape_id (int): The shape ID to get the font names for.
        ground_truth (Dict[str, Any]): The ground truth JSON data.

    Returns:
        set: Set of font names used in the shape.
    """
    font_name = set()
    
    # Get the shapes from the ground truth
    shapes = ground_truth.get("slide", {}).get("shapes", [])
    
    # Find the target shape
    target_shape = None
    for shape in shapes:
        if shape.get("shape_id") == shape_id:
            target_shape = shape
            break
    
    if target_shape is None:
        logging.error(f"Shape with ID {shape_id} not found in ground truth.")
        return font_name
        
    # Extract font names from font_details
    for font_detail in target_shape.get("font_details", []):
        if "font_name" in font_detail:
            font_name.add(font_detail["font_name"])
            
    return font_name
