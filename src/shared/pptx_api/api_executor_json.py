import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Union

from .utils import api_in_list

# Global JSON variables
JSON_DATA: Optional[Dict[str, Any]] = None
JSON_CURRENT_SLIDE: Optional[Dict[str, Any]] = None
JSON_CURRENT_SHAPE: Optional[Dict[str, Any]] = None


def api_executor_json(
    lines: List[str],
    json_path: Optional[Union[str, Path]] = None,
    output_path: Optional[Union[str, Path]] = None,
    json: Optional[Dict[str, Any]] = None,
) -> Optional[Dict[str, Any]]:
    """Execute the API calls for JSON mode.

    Args:
        lines: The API calls to execute
        json_path: Optional path to an existing JSON to modify
        output_path: Optional path to save the modified JSON
        json: Optional JSON data to use directly instead of loading from file

    Returns:
        The result of the API calls and any errors encountered
    """
    global JSON_DATA

    errors = []
    if json is not None:
        error = set_json(json)
        if error:
            errors.append(error)
    elif json_path is not None:
        error = set_json(str(json_path))
        if error:
            errors.append(error)

    for line in lines:
        try:
            api_name = line.split("(")[0]
            if api_in_list(api_name):
                try:
                    result = eval(line)
                    if isinstance(result, str):  # If function returned an error
                        errors.append(result)
                except Exception as e:
                    errors.append(f"Error executing {line}: {str(e)}")
            else:
                errors.append(f"API '{line}' not found in JSON API list")
        except Exception as e:
            errors.append(f"Error parsing {line}: {str(e)}")

    if output_path is not None:
        error = save_json(str(output_path))
        if error:
            errors.append(error)

    if errors:
        logging.warning("Errors occurred during API execution:")
        for error in errors:
            logging.warning(error)

    return JSON_DATA


def save_json(json_path: str) -> Optional[str]:
    """Save the JSON data.

    Args:
        json_path: The path to save the JSON.

    Returns:
        Optional error message if saving fails.
    """
    global JSON_DATA
    try:
        with open(json_path, "w") as f:
            json.dump(JSON_DATA, f, indent=4)
        return None
    except Exception as e:
        return f"Failed to save JSON: {str(e)}"


def set_json(json_input: Union[str, Dict[str, Any]]) -> Optional[str]:
    """Set the JSON data to work with.

    Args:
        json_input: Either a path to the JSON file or a dictionary containing JSON data.

    Returns:
        Optional error message if operation fails.
    """
    global JSON_DATA, JSON_CURRENT_SLIDE, JSON_CURRENT_SHAPE
    try:
        if isinstance(json_input, str):
            with open(json_input, "r") as f:
                JSON_DATA = json.load(f)
        else:
            JSON_DATA = json_input
        JSON_CURRENT_SLIDE = None
        JSON_CURRENT_SHAPE = None
        return None
    except Exception as e:
        return f"Failed to set JSON: {str(e)}"


def set_current_slide(slide_idx: int) -> Optional[str]:
    """Set the current slide to work with.

    Args:
        slide_idx: The index of the slide to set as the current slide.

    Returns:
        Optional error message if operation fails.
    """
    global JSON_CURRENT_SLIDE
    if JSON_DATA is None:
        return "No JSON data available"
    try:
        JSON_CURRENT_SLIDE = JSON_DATA["slides"][slide_idx]
        return None
    except Exception as e:
        return f"Failed to set current JSON slide: {str(e)}"


def choose_slide(slide_id: int) -> Optional[str]:
    """Choose a slide to work with by ID.

    Args:
        slide_id: The ID of the slide to choose.

    Returns:
        Optional error message if operation fails.
    """
    global JSON_CURRENT_SLIDE
    if JSON_DATA is None:
        return "No JSON data available"

    JSON_CURRENT_SLIDE = next(
        (slide for slide in JSON_DATA["slides"] if slide["slide_id"] == slide_id),
        None,
    )
    if JSON_CURRENT_SLIDE is None:
        return f"Slide with ID {slide_id} not found"
    return None


def choose_shape(shape_id: int) -> Optional[str]:
    """Choose a shape to work with.

    Args:
        shape_id: The ID of the shape to choose.

    Returns:
        Optional error message if operation fails.
    """
    global JSON_CURRENT_SHAPE
    if JSON_CURRENT_SLIDE is None:
        return "No current slide selected"

    JSON_CURRENT_SHAPE = next(
        (s for s in JSON_CURRENT_SLIDE["shapes"] if s["shape_id"] == shape_id),
        None,
    )
    if JSON_CURRENT_SHAPE is None:
        return f"Shape with ID {shape_id} not found"
    return None


def set_width(width: int) -> Optional[str]:
    """Set the width of a shape.

    Args:
        width: The width to set.

    Returns:
        Optional error message if operation fails.
    """
    if JSON_CURRENT_SHAPE is None:
        return "No shape selected"
    JSON_CURRENT_SHAPE["width"] = width
    return None


def set_height(height: int) -> Optional[str]:
    """Set the height of a shape.

    Args:
        height: The height to set.

    Returns:
        Optional error message if operation fails.
    """
    if JSON_CURRENT_SHAPE is None:
        return "No shape selected"
    JSON_CURRENT_SHAPE["height"] = height
    return None


def set_top(top: int) -> Optional[str]:
    """Set the top of a shape.

    Args:
        top: The top to set.

    Returns:
        Optional error message if operation fails.
    """
    if JSON_CURRENT_SHAPE is None:
        return "No shape selected"
    JSON_CURRENT_SHAPE["top"] = top
    return None


def set_left(left: int) -> Optional[str]:
    """Set the left of a shape.

    Args:
        left: The left to set.

    Returns:
        Optional error message if operation fails.
    """
    if JSON_CURRENT_SHAPE is None:
        return "No shape selected"
    JSON_CURRENT_SHAPE["left"] = left
    return None


def add_text_box(
    left: int,
    top: int,
    width: int,
    height: int,
    text: Optional[str] = None,
    placeholder_type: Optional[str] = None,
) -> Optional[str]:
    """Add a text box to a slide.

    Args:
        left: The left of the text box.
        top: The top of the text box.
        width: The width of the text box.
        height: The height of the text box.
        text: Optional text to add to the text box.
        placeholder_type: Optional placeholder type for the shape.

    Returns:
        Optional error message if operation fails.
    """
    global JSON_CURRENT_SHAPE
    if JSON_CURRENT_SLIDE is None:
        return "No slide selected"
    new_shape = {
        "name": f"TextBox_{len(JSON_CURRENT_SLIDE['shapes'])}",
        "shape_id": assign_shape_id(JSON_CURRENT_SLIDE),
        "shape_type": "PLACEHOLDER" if placeholder_type else "TEXT_BOX",
        "measurement_unit": "emu",
        "height": height,
        "width": width,
        "left": left,
        "top": top,
        "text": text or "",
        "font_details": [],
    }
    if placeholder_type:
        new_shape["placeholder_type"] = placeholder_type
    JSON_CURRENT_SLIDE["shapes"].append(new_shape)
    JSON_CURRENT_SHAPE = new_shape
    return None


def add_picture(
    left: int,
    top: int,
    width: int,
    height: int,
    image_file: Optional[str] = None,
) -> Optional[str]:
    """Add a picture to a slide.

    Args:
        left: The left of the picture.
        top: The top of the picture.
        width: The width of the picture.
        height: The height of the picture.
        image_file: The path to the image file to add.

    Returns:
        Optional error message if operation fails.
    """
    global JSON_CURRENT_SHAPE
    if JSON_CURRENT_SLIDE is None:
        return "No slide selected"
    if image_file is None:
        return "Image file path is required"
    new_shape = {
        "name": f"Picture_{len(JSON_CURRENT_SLIDE['shapes'])}",
        "shape_id": assign_shape_id(JSON_CURRENT_SLIDE),
        "shape_type": "PICTURE",
        "measurement_unit": "emu",
        "height": height,
        "width": width,
        "left": left,
        "top": top,
        "image_path": os.path.abspath(image_file),
    }
    JSON_CURRENT_SLIDE["shapes"].append(new_shape)
    JSON_CURRENT_SHAPE = new_shape
    return None


def insert_text(text: str) -> Optional[str]:
    """Insert text into a shape.

    Args:
        text: The text to insert.

    Returns:
        Optional error message if operation fails.
    """
    if JSON_CURRENT_SHAPE is None:
        return "No shape selected"
    JSON_CURRENT_SHAPE["text"] += text
    return None


def set_font_size(font_size: float) -> Optional[str]:
    """Set the font size of a shape.

    Args:
        font_size: The font size to set (can be floating point).

    Returns:
        Optional error message if operation fails.
    """
    if JSON_CURRENT_SHAPE is None:
        return "No shape selected"
    # Create a new font detail if none exists
    if not JSON_CURRENT_SHAPE["font_details"]:
        JSON_CURRENT_SHAPE["font_details"].append(
            {
                "paragraph_index": 0,
                "run_index": 0,
                "text": JSON_CURRENT_SHAPE.get("text", ""),
                "font_size": font_size,
            }
        )
    else:
        for detail in JSON_CURRENT_SHAPE["font_details"]:
            detail["font_size"] = font_size
    return None


def set_font_style(font_style: Literal["bold", "italic"]) -> Optional[str]:
    """Set the font style of a shape.

    Args:
        font_style: The font style to set.

    Returns:
        Optional error message if operation fails.
    """
    if JSON_CURRENT_SHAPE is None:
        return "No shape selected"
    for detail in JSON_CURRENT_SHAPE.get("font_details", []):
        detail[font_style] = True
    return None


def set_font(font_name: str) -> Optional[str]:
    """Set the font of a shape.

    Args:
        font_name: The font name to set.

    Returns:
        Optional error message if operation fails.
    """
    if JSON_CURRENT_SHAPE is None:
        return "No shape selected"
    for detail in JSON_CURRENT_SHAPE.get("font_details", []):
        detail["font_name"] = font_name
    return None


def set_font_color(font_color: str = "000000") -> Optional[str]:
    """Set the font color of a shape.

    Args:
        font_color: The font color to set in hex format (e.g. 'FF0000' for red)

    Returns:
        Optional error message if operation fails.
    """
    if JSON_CURRENT_SHAPE is None:
        return "No shape selected"
    for detail in JSON_CURRENT_SHAPE.get("font_details", []):
        detail["color"] = font_color
    return None


def assign_shape_id(
    slide: Dict[str, Any],
) -> int:
    """
    Assign a new shape ID to a shape in the slide.

    Args:
        slide (Dict[str, Any]): The slide JSON data.

    Returns:
        int: The new shape ID.
    """
    shapes = slide.get("shapes", [])
    if not shapes:
        return 1
    max_shape_id = max(shape.get("shape_id", 0) for shape in shapes)
    return max_shape_id + 1


def reset_globals() -> None:
    """Reset global JSON variables to None."""
    global JSON_DATA, JSON_CURRENT_SLIDE, JSON_CURRENT_SHAPE
    JSON_DATA = None
    JSON_CURRENT_SLIDE = None
    JSON_CURRENT_SHAPE = None


def main() -> None:
    """Run the main function."""
    try:
        # Example JSON operations can go here
        pass
    except Exception as e:
        print(f"Error in main: {str(e)}")


if __name__ == "__main__":
    main()
