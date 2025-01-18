from typing import Any, Dict, List, Literal, Optional
import logging
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
