import json
from copy import deepcopy
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
        The result of the API calls

    Raises:
        ValueError: If JSON operations fail
        FileNotFoundError: If JSON file operations fail
    """
    global JSON_DATA

    if json is not None:
        set_json(json)
    elif json_path is not None:
        set_json(str(json_path))

    for line in lines:
        api_name = line.split("(")[0]
        if api_in_list(api_name):
            try:
                eval(line)
            except Exception as e:
                raise ValueError(f"Error executing {line}: {str(e)}")
        else:
            raise ValueError(f"API '{line}' not found in JSON API list")

    if output_path is not None:
        save_json(str(output_path))

    return JSON_DATA


def save_json(json_path: str) -> None:
    """Save the JSON data.

    Args:
        json_path: The path to save the JSON.

    Raises:
        FileNotFoundError: If file cannot be written
    """
    global JSON_DATA
    try:
        with open(json_path, "w") as f:
            json.dump(JSON_DATA, f, indent=4)
    except Exception as e:
        raise FileNotFoundError(f"Failed to save JSON: {str(e)}")


def set_json(json_input: Union[str, Dict[str, Any]]) -> None:
    """Set the JSON data to work with.

    Args:
        json_input: Either a path to the JSON file or a dictionary containing JSON data.

    Raises:
        ValueError: If JSON data cannot be loaded or processed
    """
    global JSON_DATA, JSON_CURRENT_SLIDE, JSON_CURRENT_SHAPE
    try:
        if isinstance(json_input, str):
            with open(json_input, "r") as f:
                JSON_DATA = json.load(f)
        else:
            JSON_DATA = deepcopy(json_input)
        JSON_CURRENT_SLIDE = None
        JSON_CURRENT_SHAPE = None
    except Exception as e:
        raise ValueError(f"Failed to set JSON: {str(e)}")


def choose_slide(slide_id: int) -> None:
    """Choose a slide to work with by ID.

    Args:
        slide_id: The ID of the slide to choose.

    Raises:
        ValueError: If slide cannot be found or no JSON data available
    """
    global JSON_CURRENT_SLIDE
    if JSON_DATA is None:
        raise ValueError("No JSON data available")
    slides = JSON_DATA.get("slides", [])
    for slide in slides:
        if slide["slide_id"] == slide_id:
            JSON_CURRENT_SLIDE = slide
            return
    raise ValueError(f"Slide with ID {slide_id} not found")


def choose_shape(shape_id: int) -> None:
    """Choose a shape to work with.

    Args:
        shape_id: The ID of the shape to choose.

    Raises:
        ValueError: If shape cannot be found or no current slide selected
    """
    global JSON_CURRENT_SHAPE
    if JSON_CURRENT_SLIDE is None:
        raise ValueError("No current slide selected")
    shapes = JSON_CURRENT_SLIDE.get("shapes", [])
    for shape in shapes:
        if shape["shape_id"] == shape_id:
            JSON_CURRENT_SHAPE = shape
            return
    raise ValueError(f"Shape with ID {shape_id} not found")


def set_width(width: int) -> None:
    """Set the width of a shape.

    Args:
        width: The width to set.

    Raises:
        ValueError: If no shape is selected
    """
    if JSON_CURRENT_SHAPE is None:
        raise ValueError("No shape selected")
    JSON_CURRENT_SHAPE["width"] = width


def set_height(height: int) -> None:
    """Set the height of a shape.

    Args:
        height: The height to set.

    Raises:
        ValueError: If no shape is selected
    """
    if JSON_CURRENT_SHAPE is None:
        raise ValueError("No shape selected")
    JSON_CURRENT_SHAPE["height"] = height


def set_top(top: int) -> None:
    """Set the top of a shape.

    Args:
        top: The top to set.

    Raises:
        ValueError: If no shape is selected
    """
    if JSON_CURRENT_SHAPE is None:
        raise ValueError("No shape selected")
    JSON_CURRENT_SHAPE["top"] = top


def set_left(left: int) -> None:
    """Set the left of a shape.

    Args:
        left: The left to set.

    Raises:
        ValueError: If no shape is selected
    """
    if JSON_CURRENT_SHAPE is None:
        raise ValueError("No shape selected")
    JSON_CURRENT_SHAPE["left"] = left


def add_text_box(
    left: int,
    top: int,
    width: int,
    height: int,
    text: Optional[str] = None,
    placeholder_type: Optional[str] = None,
) -> None:
    """Add a text box to a slide.

    Args:
        left: The left of the text box.
        top: The top of the text box.
        width: The width of the text box.
        height: The height of the text box.
        text: Optional text to add to the text box.
        placeholder_type: Optional placeholder type for the shape.

    Raises:
        ValueError: If no slide is selected
    """
    global JSON_CURRENT_SHAPE, JSON_CURRENT_SLIDE
    if JSON_CURRENT_SLIDE is None:
        raise ValueError("No slide selected")

    if "shapes" not in JSON_CURRENT_SLIDE:
        JSON_CURRENT_SLIDE["shapes"] = []

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
        "font_details": [
            {
                "paragraph_index": 0,
                "run_index": 0,
                "text": text or "",
                "font_name": None,
                "font_size": None,
            }
        ],
    }

    if placeholder_type:
        new_shape["placeholder_type"] = placeholder_type

    JSON_CURRENT_SLIDE["shapes"].append(new_shape)
    JSON_CURRENT_SHAPE = new_shape


def add_picture(
    left: int,
    top: int,
    width: int,
    height: int,
    image_file: Optional[str] = None,
) -> None:
    """Add a picture to a slide.

    Args:
        left: The left of the picture.
        top: The top of the picture.
        width: The width of the picture.
        height: The height of the picture.
        image_file: The path to the image file to add.

    Raises:
        ValueError: If no slide is selected or image file path is not provided
    """
    global JSON_CURRENT_SHAPE
    if JSON_CURRENT_SLIDE is None:
        raise ValueError("No slide selected")
    if image_file is None:
        raise ValueError("Image file path is required")
    new_shape = {
        "name": f"Picture_{len(JSON_CURRENT_SLIDE['shapes'])}",
        "shape_id": assign_shape_id(JSON_CURRENT_SLIDE),
        "shape_type": "PICTURE",
        "measurement_unit": "emu",
        "height": height,
        "width": width,
        "left": left,
        "top": top,
        "image_path": image_file,
    }
    JSON_CURRENT_SLIDE["shapes"].append(new_shape)
    JSON_CURRENT_SHAPE = new_shape


def insert_text(text: str) -> None:
    """Insert text into a shape.

    Args:
        text: The text to insert.

    Raises:
        ValueError: If no shape is selected
    """
    if JSON_CURRENT_SHAPE is None:
        raise ValueError("No shape selected")
    JSON_CURRENT_SHAPE["text"] += text


def set_font_size(font_size: float) -> None:
    """Set the font size of a shape.

    Args:
        font_size: The font size to set (can be floating point).

    Raises:
        ValueError: If no shape is selected
    """
    if JSON_CURRENT_SHAPE is None:
        raise ValueError("No shape selected")
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


def set_font_style(font_style: Literal["bold", "italic"]) -> None:
    """Set the font style of a shape.

    Args:
        font_style: The font style to set.

    Raises:
        ValueError: If no shape is selected
    """
    if JSON_CURRENT_SHAPE is None:
        raise ValueError("No shape selected")
    for detail in JSON_CURRENT_SHAPE.get("font_details", []):
        detail[font_style] = True


def set_font(font_name: str) -> None:
    """Set the font of a shape.

    Args:
        font_name: The font name to set.

    Raises:
        ValueError: If no shape is selected
    """
    if JSON_CURRENT_SHAPE is None:
        raise ValueError("No shape selected")
    for detail in JSON_CURRENT_SHAPE.get("font_details", []):
        detail["font_name"] = font_name


def set_font_color(font_color: str = "000000") -> None:
    """Set the font color of a shape.

    Args:
        font_color: The font color to set in hex format (e.g. 'FF0000' for red)

    Raises:
        ValueError: If no shape is selected
    """
    if JSON_CURRENT_SHAPE is None:
        raise ValueError("No shape selected")
    for detail in JSON_CURRENT_SHAPE.get("font_details", []):
        detail["color"] = font_color


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
