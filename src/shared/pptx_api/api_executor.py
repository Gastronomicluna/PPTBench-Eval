import os
from typing import List, Literal, Optional, Union

from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pptx.presentation import Presentation
from pptx.shapes.autoshape import Shape as AutoShape
from pptx.shapes.base import BaseShape
from pptx.slide import Slide
from pptx.util import Length, Pt

from .api_doc import API, api_list

# Global variables
CURRENT_SLIDE: Optional[Slide] = None
CURRENT_SHAPE: Optional[Union[AutoShape, BaseShape]] = None
PRESENTATION: Optional[Presentation] = None
SLIDES: Optional[List[Slide]] = None
SHAPES: Optional[List[BaseShape]] = None


def check_if_api_in_list(
    api_name: str,
    api_list: List[API],
) -> bool:
    """Check if an API is in the API list.

    Args:
        api_name: The name of the API to check.
        api_list: The list of APIs to check against.

    Returns:
        True if the API is in the list, False otherwise.
    """
    for api in api_list:
        if api_name == api.name:
            return True
    return False


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


def add_text_box(
    left: int,
    top: int,
    width: int,
    height: int,
    text: Optional[str] = None,
) -> None:
    """Add a text box to a slide.

    Args:
        left: The left of the text box.
        top: The top of the text box.
        width: The width of the text box.
        height: The height of the text box.
    """
    try:
        text_box: BaseShape = CURRENT_SLIDE.shapes.add_textbox(
            Length(left),
            Length(top),
            Length(width),
            Length(height),
        )
        text_box.text = text
    except Exception as e:
        raise ValueError(f"Failed to add text box to slide: {str(e)}")


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
    try:
        img_path = os.path.abspath(image_file)
        CURRENT_SLIDE.shapes.add_picture(
            img_path,
            Length(left),
            Length(top),
            Length(width),
            Length(height),
        )
    except Exception as e:
        raise ValueError(f"Failed to add picture to slide: {str(e)}")


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
