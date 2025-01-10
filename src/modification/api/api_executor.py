from pptx import Presentation
from pptx.slide import Slide

def choose_shape(
    slide: Slide,
    shape_idx: int
):
    """Choose a shape from a slide.

    Args:
        slide: The slide to choose the shape from.
        shape_idx: The index of the shape to choose.

    Returns:
        The chosen shape.
    """
    return slide.shapes[shape_idx]
