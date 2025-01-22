import logging
from typing import Any, Dict


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
    # Get the shape from the ground truth
    slide = ground_truth.get("slide", {})
    target_shape = get_shape_from_slide(
        shape_id=shape_id,
        slide=slide,
    )

    font_name = get_font_from_shape(target_shape)

    return font_name


def get_shape_from_presentation(
    slide_id: int,
    shape_id: int,
    presentation: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Get the shape from the presentation JSON data.

    Args:
        slide_id (int): The slide ID of the shape.
        shape_id (int): The shape ID to get.
        presentation (Dict[str, Any]): The presentation JSON data.

    Returns:
        Dict[str, Any]: The shape data.
    """
    # Find the target slide
    target_slide = get_slide_from_presentation(
        slide_id=slide_id,
        presentation=presentation,
    )

    # Find the target shape
    target_shape = get_shape_from_slide(
        shape_id=shape_id,
        slide=target_slide,
    )

    return target_shape


def get_shape_from_slide(
    shape_id: int,
    slide: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Get the shape from the slide JSON data.

    Args:
        shape_id (int): The shape ID to get.
        slide (Dict[str, Any]): The slide JSON data.

    Returns:
        Dict[str, Any]: The shape data.
    """
    # Get the shapes from the slide
    shapes = slide.get("shapes", [])

    # Find the target shape
    target_shape = None
    for shape in shapes:
        if shape.get("shape_id") == shape_id:
            target_shape = shape
            break

    if target_shape is None:
        logging.error(f"Shape with ID {shape_id} not found in slide.")
        return {}

    return target_shape


def get_font_from_shape(
    shape: Dict[str, Any],
) -> set:
    """
    Get the font names from a shape.

    Args:
        shape (Dict[str, Any]): The shape to get the font names for.

    Returns:
        set: Set of font names used in the shape.
    """
    font_name = set()

    # Extract font names from font_details
    for font_detail in shape.get("font_details", []):
        if "font_name" in font_detail:
            font_name.add(font_detail["font_name"])

    return font_name


def get_slide_from_presentation(
    slide_id: int,
    presentation: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Get the slide from the presentation JSON data.

    Args:
        slide_id (int): The slide ID of the slide.
        presentation (Dict[str, Any]): The presentation JSON data.

    Returns:
        Dict[str, Any]: The slide data.
    """
    # Get the slides from the presentation
    slides = presentation.get("slides", [])

    # Find the target slide
    target_slide = None
    for slide in slides:
        if slide.get("slide_id") == slide_id:
            target_slide = slide
            break

    if target_slide is None:
        logging.error(f"Slide with ID {slide_id} not found in presentation.")
        return {}

    return target_slide


def has_overlap(slide_json: Dict[str, Any]) -> bool:
    """
    Check if the slide contains overlapping elements.

    Args:
        slide_json (Dict[str, Any]): The JSON representation of the slide.

    Returns:
        bool: True if the slide contains overlapping elements, False otherwise.
    """
    shapes = slide_json["shapes"]
    n_shapes = len(shapes)

    for i in range(n_shapes):
        for j in range(i + 1, n_shapes):
            shape1 = shapes[i]
            shape2 = shapes[j]

            # Calculate boundaries for each shape
            shape1_right = shape1["left"] + shape1["width"]
            shape1_bottom = shape1["top"] + shape1["height"]
            shape2_right = shape2["left"] + shape2["width"]
            shape2_bottom = shape2["top"] + shape2["height"]

            # Check if shapes overlap
            if not (
                shape1_right <= shape2["left"]  # shape1 is left of shape2
                or shape2_right <= shape1["left"]  # shape2 is left of shape1
                or shape1_bottom <= shape2["top"]  # shape1 is above shape2
                or shape2_bottom <= shape1["top"]
            ):  # shape2 is above shape1
                return True

    return False


def has_out_of_bounds(
    slide_json: Dict[str, Any],
    slide_height: int,
    slide_width: int,
) -> bool:
    """
    Check if the slide contains elements that are out of bounds.

    Args:
        slide_json (Dict[str, Any]): The JSON representation of the slide.

    Returns:
        bool: True if the slide contains elements that are out of bounds, False otherwise.
    """
    shapes = slide_json["slide"]["shapes"]

    for shape in shapes:
        # Check if shape extends beyond slide boundaries
        if (
            shape["left"] < 0
            or shape["top"] < 0
            or shape["left"] + shape["width"] > slide_width
            or shape["top"] + shape["height"] > slide_height
        ):
            return True

    return False
