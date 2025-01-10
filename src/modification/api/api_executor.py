from typing import Optional

from pptx.shapes.base import BaseShape
from pptx.slide import Slide
from pptx.util import Length


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