import os
from typing import List, Literal, Optional, Union

from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pptx.presentation import Presentation
from pptx.shapes.autoshape import Shape as AutoShape
from pptx.shapes.base import BaseShape
from pptx.slide import Slide
from pptx.util import Length, Pt

# Global variables
CURRENT_SLIDE: Optional[Slide] = None
CURRENT_SHAPE: Optional[Union[AutoShape, BaseShape]] = None
PRESENTATION: Optional[Presentation] = None
SLIDES: Optional[List[Slide]] = None
SHAPES: Optional[List[BaseShape]] = None


def set_presentation(
    pptx_path: str,
) -> None:
    """Set the presentation to work with.

    Args:
        pptx_path: The path to the presentation.
    """
    global PRESENTATION, SLIDES
    try:
        PRESENTATION = Presentation(pptx_path)
        SLIDES = PRESENTATION.slides
    except Exception as e:
        raise ValueError(f"Failed to open presentation: {str(e)}")


def set_current_slide(
    slide_idx: int,
) -> None:
    """Set the current slide to work with.

    Args:
        slide_idx: The index of the slide to set as the current slide.
    """
    global CURRENT_SLIDE, SHAPES
    try:
        CURRENT_SLIDE = SLIDES[slide_idx]
        SHAPES = CURRENT_SLIDE.shapes
    except Exception as e:
        raise ValueError(f"Failed to set current slide: {str(e)}")


def choose_shape(
    shape_id: int,
) -> None:
    """Choose a shape to work with.

    Args:
        shape_id: The index of the shape to choose.
    """
    global CURRENT_SHAPE
    try:
        CURRENT_SHAPE = SHAPES[shape_id]
    except Exception as e:
        raise ValueError(f"Failed to choose shape: {str(e)}")


def set_width(
    width: int,
) -> None:
    """Set the width of a shape.

    Args:
        width: The width to set.
    """
    try:
        CURRENT_SHAPE.width = Length(width)
    except Exception as e:
        raise ValueError(f"Failed to set width of shape: {str(e)}")


def set_height(
    height: int,
) -> None:
    """Set the height of a shape.

    Args:
        height: The height to set.
    """
    try:
        CURRENT_SHAPE.height = Length(height)
    except Exception as e:
        raise ValueError(f"Failed to set height of shape: {str(e)}")


def set_top(
    top: int,
) -> None:
    """Set the top of a shape.

    Args:
        top: The top to set.
    """
    try:
        CURRENT_SHAPE.top = Length(top)
    except Exception as e:
        raise ValueError(f"Failed to set top of shape: {str(e)}")


def set_left(
    left: int,
) -> None:
    """Set the left of a shape.

    Args:
        left: The left to set.
    """
    try:
        CURRENT_SHAPE.left = Length(left)
    except Exception as e:
        raise ValueError(f"Failed to set left of shape: {str(e)}")


def add_shape(
    shape_type: str,
    left: int,
    top: int,
    width: int,
    height: int,
    image_file: Optional[str] = None,
) -> None:
    """Add a shape to a slide.

    Args:
        shape_type: The type of the shape to add (case insensitive).
        left: The left of the shape to add.
        top: The top of the shape to add.
        width: The width of the shape to add.
        height: The height of the shape to add.
        image_file: The image path of the shape to add.
    """
    # Convert shape_type to uppercase and check if it's valid
    shape_type = shape_type.upper()
    if shape_type not in MSO_SHAPE_TYPE.__members__:
        raise ValueError(f"Invalid shape type: {shape_type}")

    # Check if the image path is valid
    if image_file is not None and not os.path.exists(image_file):
        raise ValueError(f"Image path does not exist: {image_file}")

    # Add the shape to the slide
    try:
        if shape_type == MSO_SHAPE_TYPE.PICTURE.name:
            CURRENT_SLIDE.shapes.add_picture(image_file, left, top, width, height)
        elif shape_type == MSO_SHAPE_TYPE.TEXT_BOX.name:
            CURRENT_SLIDE.shapes.add_textbox(left, top, width, height)
    except Exception as e:
        raise ValueError(f"Failed to add shape to slide: {str(e)}")


def insert_text(
    text: str,
) -> None:
    """Insert text into a shape.

    Args:
        text: The text to insert.
    """
    try:
        CURRENT_SHAPE.text = text
    except Exception as e:
        raise ValueError(f"Failed to insert text into shape: {str(e)}")


def set_font_size(
    font_size: int,
) -> None:
    """Set the font size of a shape.

    Args:
        font_size: The font size to set.
    """
    try:
        for paragraph in CURRENT_SHAPE.text_frame.paragraphs:
            for run in paragraph.runs:
                run.font.size = Pt(font_size)
    except Exception as e:
        raise ValueError(f"Failed to set font size of shape: {str(e)}")


def set_font_style(
    font_style: Literal["bold", "italic"],
) -> None:
    """Set the font style of a shape.

    Args:
        font_style: The font style to set.
    """
    try:
        for paragraph in CURRENT_SHAPE.text_frame.paragraphs:
            for run in paragraph.runs:
                run.font.bold = font_style == "bold"
                run.font.italic = font_style == "italic"
                run.font.underline = font_style == "underline"
    except Exception as e:
        raise ValueError(f"Failed to set font style of shape: {str(e)}")


def set_font(
    font_name: str,
) -> None:
    """Set the font of a shape.

    Args:
        font_name: The font name to set.
    """
    try:
        for paragraph in CURRENT_SHAPE.text_frame.paragraphs:
            for run in paragraph.runs:
                run.font.name = font_name
    except Exception as e:
        raise ValueError(f"Failed to set font of shape: {str(e)}")


def set_font_color(
    font_color: str = "000000",
) -> None:
    """Set the font color of a shape.

    Args:
        shape: The shape to set the font color of.
        font_color: The font color to set in hex format (e.g. 'FF0000' for red)
    """
    try:
        for paragraph in CURRENT_SHAPE.text_frame.paragraphs:
            for run in paragraph.runs:
                run.font.color.rgb = RGBColor.from_string(font_color)
    except Exception as e:
        raise ValueError(f"Failed to set font color of shape: {str(e)}")
