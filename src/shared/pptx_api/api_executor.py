import os
from typing import Literal, Optional

from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pptx.presentation import Presentation
from pptx.shapes.autoshape import Shape as AutoShape
from pptx.shapes.base import BaseShape
from pptx.slide import Slide
from pptx.util import Length, Pt


def choose_slide(presentation: Presentation, slide_idx: int) -> Optional[Slide]:
    """Choose a slide from a presentation.

    Args:
        presentation: The presentation to choose the slide from.
        slide_idx: The index of the slide to choose.

    Returns:
        The chosen slide.
    """
    try:
        slide = presentation.slides[slide_idx]
        return slide
    except Exception as e:
        raise ValueError(f"Failed to choose slide {slide_idx}: {str(e)}")


def choose_shape(slide: Slide, shape_idx: int) -> Optional[BaseShape]:
    """Choose a shape from a slide.

    Args:
        slide: The slide to choose the shape from.
        shape_idx: The index of the shape to choose.

    Returns:
        The chosen shape.
    """
    try:
        shape = slide.shapes[shape_idx]
        return shape
    except Exception as e:
        raise ValueError(f"Failed to choose shape {shape_idx}: {str(e)}")


def set_width(
    shape: BaseShape,
    width: int,
) -> None:
    """Set the width of a shape.

    Args:
        shape: The shape to set the width of.
        width: The width to set.
    """
    try:
        shape.width = Length(width)
    except Exception as e:
        raise ValueError(f"Failed to set width of shape: {str(e)}")


def set_height(
    shape: BaseShape,
    height: int,
) -> None:
    """Set the height of a shape.

    Args:
        shape: The shape to set the height of.
        height: The height to set.
    """
    try:
        shape.height = Length(height)
    except Exception as e:
        raise ValueError(f"Failed to set height of shape: {str(e)}")


def set_top(
    shape: BaseShape,
    top: int,
) -> None:
    """Set the top of a shape.

    Args:
        shape: The shape to set the top of.
        top: The top to set.
    """
    try:
        shape.top = Length(top)
    except Exception as e:
        raise ValueError(f"Failed to set top of shape: {str(e)}")


def set_left(
    shape: BaseShape,
    left: int,
) -> None:
    """Set the left of a shape.

    Args:
        shape: The shape to set the left of.
        left: The left to set.
    """
    try:
        shape.left = Length(left)
    except Exception as e:
        raise ValueError(f"Failed to set left of shape: {str(e)}")


def add_shape(
    slide: Slide,
    shape_type: str,
    left: int,
    top: int,
    width: int,
    height: int,
    image_file: Optional[str] = None,
) -> None:
    """Add a shape to a slide.

    Args:
        slide: The slide to add the shape to.
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
            slide.shapes.add_picture(image_file, left, top, width, height)
        elif shape_type == MSO_SHAPE_TYPE.TEXT_BOX.name:
            slide.shapes.add_textbox(left, top, width, height)
    except Exception as e:
        raise ValueError(f"Failed to add shape to slide: {str(e)}")


def insert_text(
    shape: AutoShape,
    text: str,
) -> None:
    """Insert text into a shape.

    Args:
        shape: The shape to insert text into.
        text: The text to insert.
    """
    try:
        shape.text = text
    except Exception as e:
        raise ValueError(f"Failed to insert text into shape: {str(e)}")


def set_font_size(
    shape: AutoShape,
    font_size: int,
) -> None:
    """Set the font size of a shape.

    Args:
        shape: The shape to set the font size of.
        font_size: The font size to set.
    """
    try:
        for paragraph in shape.text_frame.paragraphs:
            for run in paragraph.runs:
                run.font.size = Pt(font_size)
    except Exception as e:
        raise ValueError(f"Failed to set font size of shape: {str(e)}")


def set_font_style(
    shape: AutoShape,
    font_style: Literal["bold", "italic"],
) -> None:
    """Set the font style of a shape.

    Args:
        shape: The shape to set the font style of.
        font_style: The font style to set.
    """
    try:
        for paragraph in shape.text_frame.paragraphs:
            for run in paragraph.runs:
                run.font.bold = font_style == "bold"
                run.font.italic = font_style == "italic"
                run.font.underline = font_style == "underline"
    except Exception as e:
        raise ValueError(f"Failed to set font style of shape: {str(e)}")


def set_font(
    shape: AutoShape,
    font_name: str,
) -> None:
    """Set the font of a shape.

    Args:
        shape: The shape to set the font of.
        font_name: The font name to set.
    """
    try:
        for paragraph in shape.text_frame.paragraphs:
            for run in paragraph.runs:
                run.font.name = font_name
    except Exception as e:
        raise ValueError(f"Failed to set font of shape: {str(e)}")


def set_font_color(
    shape: AutoShape,
    font_color: str,
) -> None:
    """Set the font color of a shape.

    Args:
        shape: The shape to set the font color of.
        font_color: The font color to set.
    """
    try:
        for paragraph in shape.text_frame.paragraphs:
            for run in paragraph.runs:
                run.font.color.rgb = RGBColor.from_string(font_color)
    except Exception as e:
        raise ValueError(f"Failed to set font color of shape: {str(e)}")
