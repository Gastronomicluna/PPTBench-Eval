import pytest
from pptx import Presentation

from src.shared.pptx_api.api_executor import (
    choose_shape,
    choose_slide,
    set_height,
    set_left,
    set_top,
    set_width,
)


@pytest.fixture
def sample_presentation() -> Presentation:
    """Load a sample presentation."""
    return Presentation("tests/data/ZYBVMQIBRRHONKQ7M4INV3LE62ODKIN2.pptx")


def test_choose_slide(sample_presentation: Presentation) -> None:
    """Test choose_slide function."""
    slide = choose_slide(sample_presentation, 0)
    assert slide is not None


def test_choose_slide_invalid_index(sample_presentation: Presentation) -> None:
    """Test choose_slide with an invalid index."""
    with pytest.raises(ValueError):
        choose_slide(sample_presentation, 999)


def test_choose_shape(sample_presentation: Presentation) -> None:
    """Test choose_shape function."""
    slide = choose_slide(sample_presentation, 0)
    shape = choose_shape(slide, 0)
    assert shape is not None


def test_choose_shape_invalid_index(sample_presentation: Presentation) -> None:
    """Test choose_shape with an invalid index."""
    slide = choose_slide(sample_presentation, 0)
    with pytest.raises(ValueError):
        choose_shape(slide, 999)


def test_set_width(sample_presentation: Presentation) -> None:
    """Test set_width function."""
    slide = choose_slide(sample_presentation, 0)
    shape = choose_shape(slide, 0)
    set_width(shape, 4000)
    assert shape.width == 4000


def test_set_height(sample_presentation: Presentation) -> None:
    """Test set_height function."""
    slide = choose_slide(sample_presentation, 0)
    shape = choose_shape(slide, 0)
    set_height(shape, 2000)
    assert shape.height == 2000


def test_set_top(sample_presentation: Presentation) -> None:
    """Test set_top function."""
    slide = choose_slide(sample_presentation, 0)
    shape = choose_shape(slide, 0)
    set_top(shape, 1000)
    assert shape.top == 1000


def test_set_left(sample_presentation: Presentation) -> None:
    """Test set_left function."""
    slide = choose_slide(sample_presentation, 0)
    shape = choose_shape(slide, 0)
    set_left(shape, 1500)
    assert shape.left == 1500
