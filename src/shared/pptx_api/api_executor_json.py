import json
import logging
import os
from typing import Any, Dict, List, Literal, Optional, Union

from .utils import api_in_list

# Global JSON variables
JSON_DATA: Optional[Dict[str, Any]] = None
JSON_CURRENT_SLIDE: Optional[Dict[str, Any]] = None
JSON_CURRENT_SHAPE: Optional[Dict[str, Any]] = None


def api_executor_json(
    lines: List[str],
    json_path: Optional[str] = None,
    output_path: Optional[str] = None,
    json: Optional[Dict[str, Any]] = None,
) -> Optional[Dict[str, Any]]:
    """Execute the API calls for JSON mode.

    Args:
        lines: The API calls to execute
        json_path: Optional path to an existing JSON to modify
        output_path: Optional path to save the modified JSON
        json: Optional JSON data to use directly instead of loading from file

    Returns:
        The result of the API calls.
    """
    global JSON_DATA

    if json is not None:
        set_json(json)
    elif json_path is not None:
        set_json(json_path)

    errors = []
    for line in lines:
        try:
            api_name = line.split("(")[0]
            if api_in_list(api_name):
                try:
                    exec(line)
                except ValueError as ve:
                    errors.append(str(ve))
                except Exception as e:
                    errors.append(f"Error executing {line}: {str(e)}")
            else:
                errors.append(f"API '{line}' not found.")
        except Exception as e:
            errors.append(f"Error parsing {line}: {str(e)}")

    if output_path is not None:
        try:
            save_json(output_path)
        except ValueError as ve:
            errors.append(f"Error saving JSON: {str(ve)}")
        except Exception as e:
            errors.append(f"Error saving JSON: {str(e)}")

    if errors:
        logging.error("Errors occurred during API execution:")
        for error in errors:
            logging.error(error)

    return JSON_DATA


def save_json(json_path: str) -> None:
    """Save the JSON data.

    Args:
        json_path: The path to save the JSON.
    """
    global JSON_DATA
    try:
        with open(json_path, "w") as f:
            json.dump(JSON_DATA, f, indent=4)
    except Exception as e:
        raise ValueError(f"Failed to save JSON: {str(e)}")


def set_json(json_input: Union[str, Dict[str, Any]]) -> None:
    """Set the JSON data to work with.

    Args:
        json_input: Either a path to the JSON file or a dictionary containing JSON data.
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
    except Exception as e:
        raise ValueError(f"Failed to set JSON: {str(e)}")


def set_current_slide(slide_idx: int) -> None:
    """Set the current slide to work with.

    Args:
        slide_idx: The index of the slide to set as the current slide.
    """
    global JSON_CURRENT_SLIDE
    if JSON_DATA is None:
        raise ValueError("No JSON data available")
    try:
        JSON_CURRENT_SLIDE = JSON_DATA["slides"][slide_idx]
    except Exception as e:
        raise ValueError(f"Failed to set current JSON slide: {str(e)}")


def choose_slide(slide_id: int) -> Dict[str, Any]:
    """Choose a slide to work with by ID.

    Args:
        slide_id: The ID of the slide to choose.

    Returns:
        Dict[str, Any]: The selected slide.

    Raises:
        ValueError: If slide not found or JSON_DATA is None.
    """
    global JSON_CURRENT_SLIDE
    if JSON_DATA is None:
        raise ValueError("No JSON data available")

    JSON_CURRENT_SLIDE = next(
        (slide for slide in JSON_DATA["slides"] if slide["slide_id"] == slide_id),
        None,
    )
    if JSON_CURRENT_SLIDE is None:
        raise ValueError(f"Slide with ID {slide_id} not found")
    return JSON_CURRENT_SLIDE


def choose_shape(shape_id: int) -> Dict[str, Any]:
    """Choose a shape to work with.

    Args:
        shape_id: The ID of the shape to choose.

    Returns:
        Dict[str, Any]: The selected shape.

    Raises:
        ValueError: If shape not found or no slide selected.
    """
    global JSON_CURRENT_SHAPE
    if JSON_CURRENT_SLIDE is None:
        raise ValueError("No current slide selected")

    JSON_CURRENT_SHAPE = next(
        (s for s in JSON_CURRENT_SLIDE["shapes"] if s["shape_id"] == shape_id),
        None,
    )
    if JSON_CURRENT_SHAPE is None:
        raise ValueError(f"Shape with ID {shape_id} not found")
    return JSON_CURRENT_SHAPE


def set_width(width: int) -> None:
    """Set the width of a shape.

    Args:
        width: The width to set.
    """
    if JSON_CURRENT_SHAPE is None:
        raise ValueError("No shape selected")
    JSON_CURRENT_SHAPE["width"] = width


def set_height(height: int) -> None:
    """Set the height of a shape.

    Args:
        height: The height to set.
    """
    if JSON_CURRENT_SHAPE is None:
        raise ValueError("No shape selected")
    JSON_CURRENT_SHAPE["height"] = height


def set_top(top: int) -> None:
    """Set the top of a shape.

    Args:
        top: The top to set.
    """
    if JSON_CURRENT_SHAPE is None:
        raise ValueError("No shape selected")
    JSON_CURRENT_SHAPE["top"] = top


def set_left(left: int) -> None:
    """Set the left of a shape.

    Args:
        left: The left to set.
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
    """
    global JSON_CURRENT_SHAPE
    if JSON_CURRENT_SLIDE is None:
        raise ValueError("No slide selected")
    new_shape = {
        "name": f"TextBox_{len(JSON_CURRENT_SLIDE['shapes'])}",
        "shape_id": len(JSON_CURRENT_SLIDE["shapes"]) + 1,
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
    """
    global JSON_CURRENT_SHAPE
    if JSON_CURRENT_SLIDE is None:
        raise ValueError("No slide selected")
    if image_file is None:
        raise ValueError("Image file path is required")
    new_shape = {
        "name": f"Picture_{len(JSON_CURRENT_SLIDE['shapes'])}",
        "shape_id": len(JSON_CURRENT_SLIDE["shapes"]) + 1,
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


def insert_text(text: str) -> None:
    """Insert text into a shape.

    Args:
        text: The text to insert.
    """
    if JSON_CURRENT_SHAPE is None:
        raise ValueError("No shape selected")
    JSON_CURRENT_SHAPE["text"] += text


def set_font_size(font_size: float) -> None:
    """Set the font size of a shape.

    Args:
        font_size: The font size to set (can be floating point).
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
    """
    if JSON_CURRENT_SHAPE is None:
        raise ValueError("No shape selected")
    for detail in JSON_CURRENT_SHAPE.get("font_details", []):
        detail[font_style] = True


def set_font(font_name: str) -> None:
    """Set the font of a shape.

    Args:
        font_name: The font name to set.
    """
    if JSON_CURRENT_SHAPE is None:
        raise ValueError("No shape selected")
    for detail in JSON_CURRENT_SHAPE.get("font_details", []):
        detail["font_name"] = font_name


def set_font_color(font_color: str = "000000") -> None:
    """Set the font color of a shape.

    Args:
        font_color: The font color to set in hex format (e.g. 'FF0000' for red)
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
