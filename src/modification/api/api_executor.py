from pptx.slide import Slide
from pptx.shapes.base import Shape
from typing import Optional
def choose_shape(
    slide: Slide,
    shape_idx: int
) -> Optional[Shape]:
    """Choose a shape from a slide.

    Args:
        slide: The slide to choose the shape from.
        shape_idx: The index of the shape to choose.

    Returns:
        The chosen shape.
    """
    try:
        shape = slide.shapes[shape_idx]
    except Exception as e:
        print(f"Failed to choose shape {shape_idx}: {str(e)}")
        shape = None
    return shape
