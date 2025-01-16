import os
import tempfile
from typing import Generator

import pytest
from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pptx.util import Pt

from src.shared.pptx_api.api_executor import (
    CURRENT_SHAPE,
    CURRENT_SLIDE,
    PRESENTATION,
    SHAPES,
    SLIDES,
    TEXT_DETAILS,
    add_picture,
    add_text_box,
    api_executor,
    api_in_list,
    choose_shape,
    choose_slide,
    create_slide,
    get_text_details,
    insert_text,
    save_presentation,
    set_current_slide,
    set_font,
    set_font_color,
    set_font_size,
    set_font_style,
    set_height,
    set_left,
    set_presentation,
    set_text_details,
    set_top,
    set_width,
)


@pytest.fixture
def sample_presentation() -> Presentation:
    """Load a sample presentation."""
    return Presentation("tests/data/ZYBVMQIBRRHONKQ7M4INV3LE62ODKIN2.pptx")


@pytest.fixture
def sample_image() -> Generator[str, None, None]:
    """Create a temporary test image file.

    Returns:
        Generator[str, None, None]: Path to the temporary image file.
    """
    # Create a temporary file
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        # Create a small red image
        img = Image.new("RGB", (100, 100), color="red")
        img.save(tmp.name)
        tmp_path = tmp.name

    yield tmp_path

    # Cleanup the temporary file after the test
    os.unlink(tmp_path)


def test_choose_slide(sample_presentation: Presentation) -> None:
    """Test choose_slide function."""
    set_current_slide(0)
    assert CURRENT_SLIDE is not None


def test_choose_slide_invalid_index(sample_presentation: Presentation) -> None:
    """Test choose_slide with an invalid index."""
    with pytest.raises(ValueError):
        choose_slide(sample_presentation, 999)


def test_choose_shape(sample_presentation: Presentation) -> None:
    """Test choose_shape function."""
    set_current_slide(0)
    choose_shape(0)
    assert CURRENT_SHAPE is not None


def test_choose_shape_invalid_index(sample_presentation: Presentation) -> None:
    """Test choose_shape with an invalid index."""
    slide = choose_slide(sample_presentation, 0)
    with pytest.raises(ValueError):
        choose_shape(slide, 999)


def test_set_width(sample_presentation: Presentation) -> None:
    """Test set_width function."""
    set_current_slide(0)
    choose_shape(0)
    set_width(4000)
    assert CURRENT_SHAPE.width == 4000


def test_set_height(sample_presentation: Presentation) -> None:
    """Test set_height function."""
    set_current_slide(0)
    choose_shape(0)
    set_height(2000)
    assert CURRENT_SHAPE.height == 2000


def test_set_top(sample_presentation: Presentation) -> None:
    """Test set_top function."""
    set_current_slide(0)
    choose_shape(0)
    set_top(1000)
    assert CURRENT_SHAPE.top == 1000


def test_set_left(sample_presentation: Presentation) -> None:
    """Test set_left function."""
    set_current_slide(0)
    choose_shape(0)
    set_left(1500)
    assert CURRENT_SHAPE.left == 1500


def test_add_picture(sample_presentation: Presentation, sample_image: str) -> None:
    """Test add_shape function with a picture."""
    set_current_slide(0)
    add_picture(1000, 1000, 2000, 1000, sample_image)
    assert len(CURRENT_SLIDE.shapes) > 0
    assert CURRENT_SLIDE.shapes[-1].shape_type == MSO_SHAPE_TYPE.PICTURE


def test_add_shape_invalid_type(sample_presentation: Presentation) -> None:
    """Test adding shape with an invalid type."""
    set_current_slide(0)
    with pytest.raises(ValueError):
        add_text_box(1000, 1000, 2000, 1000, image_file="nonexistent.png")


def test_insert_text(sample_presentation: Presentation) -> None:
    """Test insert_text function."""
    set_current_slide(0)
    add_text_box(1000, 1000, 2000, 1000)
    choose_shape(len(CURRENT_SLIDE.shapes) - 1)
    insert_text("Test Text")
    assert CURRENT_SHAPE.text == "Test Text"


def test_set_font_size(sample_presentation: Presentation) -> None:
    """Test set_font_size function."""
    set_current_slide(0)
    add_text_box(1000, 1000, 2000, 1000, "Test Text")
    choose_shape(len(CURRENT_SLIDE.shapes) - 1)
    set_font_size(24)
    assert CURRENT_SHAPE.text_frame.paragraphs[0].runs[0].font.size == Pt(24)


def test_set_font_style_bold(sample_presentation: Presentation) -> None:
    """Test set_font_style function with bold style."""
    set_current_slide(0)
    add_text_box(1000, 1000, 2000, 1000, "Test Text")
    choose_shape(len(CURRENT_SLIDE.shapes) - 1)
    set_font_style("bold")
    assert CURRENT_SHAPE.text_frame.paragraphs[0].runs[0].font.bold is True


def test_set_font_style_italic(sample_presentation: Presentation) -> None:
    """Test set_font_style function with italic style."""
    set_current_slide(0)
    add_text_box(1000, 1000, 2000, 1000, "Test Text")
    choose_shape(len(CURRENT_SLIDE.shapes) - 1)
    set_font_style("italic")
    assert CURRENT_SHAPE.text_frame.paragraphs[0].runs[0].font.italic is True


def test_set_font(sample_presentation: Presentation) -> None:
    """Test set_font function."""
    set_current_slide(0)
    add_text_box(1000, 1000, 2000, 1000, "Test Text")
    choose_shape(len(CURRENT_SLIDE.shapes) - 1)
    test_font = "Arial"
    set_font(test_font)
    assert CURRENT_SHAPE.text_frame.paragraphs[0].runs[0].font.name == test_font


def test_set_font_color(sample_presentation: Presentation) -> None:
    """Test set_font_color function."""
    set_current_slide(0)
    add_text_box(1000, 1000, 2000, 1000, "Test Text")
    choose_shape(len(CURRENT_SLIDE.shapes) - 1)
    test_color = "FF0000"  # Red
    set_font_color(test_color)
    assert CURRENT_SHAPE.text_frame.paragraphs[0].runs[
        0
    ].font.color.rgb == RGBColor.from_string(test_color)


def test_add_text_box(sample_presentation: Presentation) -> None:
    """Test add_text_box function."""
    set_current_slide(0)
    add_text_box(1000, 1000, 2000, 1000, "Test Text")
    assert len(CURRENT_SLIDE.shapes) > 0
    assert CURRENT_SLIDE.shapes[-1].text == "Test Text"


def test_set_presentation(tmp_path) -> None:
    """Test set_presentation function."""
    test_file = str(tmp_path / "test.pptx")
    prs = Presentation()
    prs.save(test_file)
    set_presentation(test_file)
    assert PRESENTATION is not None
    assert SLIDES is not None
    assert CURRENT_SLIDE is None
    assert SHAPES is None
    assert CURRENT_SHAPE is None
    assert TEXT_DETAILS == {}


def test_save_presentation(tmp_path) -> None:
    """Test save_presentation function."""
    test_file = str(tmp_path / "test_save.pptx")
    prs = Presentation()
    prs.save(test_file)
    set_presentation(test_file)
    save_presentation(test_file)
    assert os.path.exists(test_file)


def test_create_slide() -> None:
    """Test create_slide function."""
    prs = Presentation()
    global PRESENTATION, SLIDES
    PRESENTATION = prs
    SLIDES = prs.slides
    initial_slide_count = len(SLIDES)
    create_slide()
    assert len(SLIDES) == initial_slide_count + 1
    assert CURRENT_SLIDE is not None
    assert CURRENT_SHAPE is None


def test_set_current_slide() -> None:
    """Test set_current_slide function."""
    prs = Presentation()
    global PRESENTATION, SLIDES
    PRESENTATION = prs
    SLIDES = prs.slides
    create_slide()
    set_current_slide(0)
    assert CURRENT_SLIDE is not None
    assert SHAPES is not None


def test_api_in_list() -> None:
    """Test api_in_list function."""
    assert api_in_list("create_slide(1)") is True
    assert api_in_list("invalid_api()") is False


def test_api_executor() -> None:
    """Test api_executor function."""
    test_apis = [
        "create_slide(1)",
        "add_text_box(1000, 1000, 2000, 1000)",
    ]
    errors = api_executor(test_apis)
    assert len(errors) == 0


def test_get_text_details(sample_presentation: Presentation) -> None:
    """Test get_text_details function."""
    set_current_slide(0)
    add_text_box(1000, 1000, 2000, 1000, "Test Text")
    choose_shape(len(CURRENT_SLIDE.shapes) - 1)
    get_text_details(CURRENT_SHAPE)
    assert TEXT_DETAILS is not None
    assert "font" in TEXT_DETAILS
    assert "bold" in TEXT_DETAILS
    assert "italic" in TEXT_DETAILS
    assert "size" in TEXT_DETAILS


def test_set_text_details(sample_presentation: Presentation) -> None:
    """Test set_text_details function."""
    set_current_slide(0)
    add_text_box(1000, 1000, 2000, 1000, "Test Text")
    choose_shape(len(CURRENT_SLIDE.shapes) - 1)

    # First get text details
    get_text_details(CURRENT_SHAPE)

    # Modify some text details
    TEXT_DETAILS["bold"] = True
    TEXT_DETAILS["size"] = Pt(24)

    # Create new shape and apply text details
    add_text_box(2000, 2000, 2000, 1000, "New Text")
    choose_shape(len(CURRENT_SLIDE.shapes) - 1)
    set_text_details(CURRENT_SHAPE)

    # Verify changes
    assert CURRENT_SHAPE.text_frame.paragraphs[0].runs[0].font.bold is True
    assert CURRENT_SHAPE.text_frame.paragraphs[0].runs[0].font.size == Pt(24)
