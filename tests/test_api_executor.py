import pytest
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE

from src.shared.pptx_api.api_executor import (
    add_shape,
    choose_shape,
    choose_slide,
    insert_text,
    set_font,
    set_font_color,
    set_font_size,
    set_font_style,
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


def test_add_shape_picture(sample_presentation: Presentation) -> None:
    """Test add_shape function with a picture."""
    slide = choose_slide(sample_presentation, 0)
    add_shape(
        slide,
        "PICTURE",
        1000,
        1000,
        2000,
        1000,
        "tests/data/sample_image.jpg",
    )
    new_shape = choose_shape(slide, len(slide.shapes) - 1)
    assert new_shape is not None
    assert new_shape.shape_type == MSO_SHAPE_TYPE.PICTURE


def test_add_shape_invalid_type(sample_presentation: Presentation) -> None:
    """Test add_shape with an invalid shape type."""
    slide = choose_slide(sample_presentation, 0)
    with pytest.raises(ValueError):
        add_shape(slide, "INVALID_TYPE", 1000, 1000, 2000, 1000)


def test_insert_text(sample_presentation: Presentation) -> None:
    """Test insert_text function."""
    slide = choose_slide(sample_presentation, 0)
    add_shape(slide, "TEXTBOX", 1000, 1000, 2000, 1000)
    shape = choose_shape(slide, len(slide.shapes) - 1)
    test_text = "Test Text"
    insert_text(shape, test_text)
    assert shape.text == test_text


def test_set_font_size(sample_presentation: Presentation) -> None:
    """Test set_font_size function."""
    slide = choose_slide(sample_presentation, 0)
    add_shape(slide, "TEXTBOX", 1000, 1000, 2000, 1000)
    shape = choose_shape(slide, len(slide.shapes) - 1)
    insert_text(shape, "Test Text")
    test_size = 24
    set_font_size(shape, test_size)
    assert shape.text_frame.paragraphs[0].runs[0].font.size.pt == test_size


def test_set_font_style_bold(sample_presentation: Presentation) -> None:
    """Test set_font_style function with bold style."""
    slide = choose_slide(sample_presentation, 0)
    add_shape(slide, "TEXTBOX", 1000, 1000, 2000, 1000)
    shape = choose_shape(slide, len(slide.shapes) - 1)
    insert_text(shape, "Test Text")
    set_font_style(shape, "bold")
    assert shape.text_frame.paragraphs[0].runs[0].font.bold is True


def test_set_font_style_italic(sample_presentation: Presentation) -> None:
    """Test set_font_style function with italic style."""
    slide = choose_slide(sample_presentation, 0)
    add_shape(slide, "TEXTBOX", 1000, 1000, 2000, 1000)
    shape = choose_shape(slide, len(slide.shapes) - 1)
    insert_text(shape, "Test Text")
    set_font_style(shape, "italic")
    assert shape.text_frame.paragraphs[0].runs[0].font.italic is True


def test_set_font(sample_presentation: Presentation) -> None:
    """Test set_font function."""
    slide = choose_slide(sample_presentation, 0)
    add_shape(slide, "TEXTBOX", 1000, 1000, 2000, 1000)
    shape = choose_shape(slide, len(slide.shapes) - 1)
    insert_text(shape, "Test Text")
    test_font = "Arial"
    set_font(shape, test_font)
    assert shape.text_frame.paragraphs[0].runs[0].font.name == test_font


def test_set_font_color(sample_presentation: Presentation) -> None:
    """Test set_font_color function."""
    slide = choose_slide(sample_presentation, 0)
    add_shape(slide, "TEXTBOX", 1000, 1000, 2000, 1000)
    shape = choose_shape(slide, len(slide.shapes) - 1)
    insert_text(shape, "Test Text")
    test_color = "FF0000"  # Red
    set_font_color(shape, test_color)
    assert shape.text_frame.paragraphs[0].runs[0].font.color.rgb.hexstr == test_color


def test_add_shape_textbox(sample_presentation: Presentation) -> None:
    """Test add_shape function with a textbox."""
    slide = choose_slide(sample_presentation, 0)
    add_shape(slide, "TEXTBOX", 1000, 1000, 2000, 1000)
    new_shape = choose_shape(slide, len(slide.shapes) - 1)
