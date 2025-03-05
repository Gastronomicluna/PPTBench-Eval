from typing import List

from pptx.presentation import Presentation
from pptx.slide import Slide

from .api_doc import API_LIST


def get_slide_ids(
    presentation: Presentation,
) -> List[int]:
    """Get the slide ids of a presentation.

    Args:
        presentation: The presentation to get the slide ids of.

    Returns:
        The slide ids of the presentation.
    """
    slide_ids = []
    for slide in presentation.slides:
        slide_ids.append(slide.slide_id)
    return slide_ids


def get_shape_ids(
    slide: Slide,
) -> List[int]:
    """Get the shape ids of a slide.

    Args:
        slide: The slide to get the shape ids of.

    Returns:
        The shape ids of the slide.
    """
    shape_ids = []
    for shape in slide.shapes:
        shape_ids.append(shape.shape_id)
    return shape_ids


def api_in_list(
    line: str,
) -> bool:
    """Parse an API from a line.

    Args:
        line: The line to parse the API from.

    Returns:
        The parsed API.
    """
    for api in API_LIST:
        if api.name == line:
            return True
    return False
