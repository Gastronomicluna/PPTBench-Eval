import os
import tempfile
from typing import Any, Dict, Generator

import pytest
from PIL import Image
from pptx import Presentation

import src.shared.pptx_api.api_executor_json as api_json
from src.shared.pptx_api.utils import get_shape_ids, get_slide_ids


@pytest.fixture
def sample_json() -> Dict[str, Any]:
    """Load a sample JSON file.

    Returns:
        Dict[str, Any]: Sample JSON data dictionary
    """
    return {
        "slide_width": 9144000,
        "slide_height": 6858000,
        "slides": [
            {
                "slide_id": 261,
                "slide_name": "",
                "shapes": [
                    {
                        "name": "PlaceHolder 1",
                        "shape_id": 23,
                        "shape_type": "PLACEHOLDER",
                        "measurement_unit": "emu",
                        "height": 1143000,
                        "width": 8229600,
                        "left": 457200,
                        "top": 274320,
                        "text": "Science CRT-Alternate",
                        "font_details": [
                            {
                                "paragraph_index": 0,
                                "run_index": 0,
                                "text": "Science CRT-Alternate",
                                "font_name": "Georgia",
                                "font_size": 44.0,
                            }
                        ],
                        "placeholder_type": "TITLE",
                    },
                    {
                        "name": "PlaceHolder 2",
                        "shape_id": 24,
                        "shape_type": "PLACEHOLDER",
                        "measurement_unit": "emu",
                        "height": 4525920,
                        "width": 8229600,
                        "left": 457200,
                        "top": 1600200,
                        "text": "Summer and Fall 2006\nDevelopment of \nDraft expanded benchmarks aligned with Montana standards\nDraft performance/achievement descriptors\nWinter \u2013 Summer 2007\nDevelopment of tasklets and items\nFall 2007\nBeta test of items\nBias and content reviews\nFinal alignment and adjustments as needed\nSpring 2008\nFirst administration",
                        "font_details": [
                            {
                                "paragraph_index": 0,
                                "run_index": 0,
                                "text": "Summer and Fall 2006",
                                "font_name": "Arial",
                                "font_size": 28.0,
                            },
                            {
                                "paragraph_index": 1,
                                "run_index": 0,
                                "text": "Development of ",
                                "font_name": "Arial",
                                "font_size": 24.0,
                            },
                            {
                                "paragraph_index": 2,
                                "run_index": 0,
                                "text": "Draft expanded benchmarks aligned with Montana standards",
                                "font_name": "Arial",
                                "font_size": 20.0,
                            },
                            {
                                "paragraph_index": 3,
                                "run_index": 0,
                                "text": "Draft performance/achievement descriptors",
                                "font_name": "Arial",
                                "font_size": 20.0,
                            },
                            {
                                "paragraph_index": 4,
                                "run_index": 0,
                                "text": "Winter \u2013 Summer 2007",
                                "font_name": "Arial",
                                "font_size": 28.0,
                            },
                            {
                                "paragraph_index": 5,
                                "run_index": 0,
                                "text": "Development of tasklets and items",
                                "font_name": "Arial",
                                "font_size": 24.0,
                            },
                            {
                                "paragraph_index": 6,
                                "run_index": 0,
                                "text": "Fall 2007",
                                "font_name": "Arial",
                                "font_size": 28.0,
                            },
                            {
                                "paragraph_index": 7,
                                "run_index": 0,
                                "text": "Beta test of items",
                                "font_name": "Arial",
                                "font_size": 24.0,
                            },
                            {
                                "paragraph_index": 8,
                                "run_index": 0,
                                "text": "Bias and content reviews",
                                "font_name": "Arial",
                                "font_size": 24.0,
                            },
                            {
                                "paragraph_index": 9,
                                "run_index": 0,
                                "text": "Final alignment and adjustments as needed",
                                "font_name": "Arial",
                                "font_size": 24.0,
                            },
                            {
                                "paragraph_index": 10,
                                "run_index": 0,
                                "text": "Spring 2008",
                                "font_name": "Arial",
                                "font_size": 28.0,
                            },
                            {
                                "paragraph_index": 11,
                                "run_index": 0,
                                "text": "First administration",
                                "font_name": "Arial",
                                "font_size": 24.0,
                            },
                        ],
                        "placeholder_type": "OBJECT",
                    },
                    {
                        "name": "PlaceHolder 3",
                        "shape_id": 4,
                        "shape_type": "PLACEHOLDER",
                        "measurement_unit": "emu",
                        "height": 476280,
                        "width": 1600200,
                        "left": 7086240,
                        "top": 6244920,
                        "text": "6",
                        "font_details": [],
                        "placeholder_type": "SLIDE_NUMBER",
                    },
                ],
            },
            {
                "slide_id": 262,
                "slide_name": "",
                "shapes": [
                    {
                        "name": "PlaceHolder 1",
                        "shape_id": 25,
                        "shape_type": "PLACEHOLDER",
                        "measurement_unit": "emu",
                        "height": 1143000,
                        "width": 8229600,
                        "left": 457200,
                        "top": 274320,
                        "text": "OPI Assessment \u000bContact Information",
                        "font_details": [
                            {
                                "paragraph_index": 0,
                                "run_index": 0,
                                "text": "OPI Assessment ",
                                "font_name": "Georgia",
                                "font_size": 40.0,
                            },
                            {
                                "paragraph_index": 0,
                                "run_index": 1,
                                "text": "Contact Information",
                                "font_name": "Georgia",
                                "font_size": 40.0,
                            },
                        ],
                        "placeholder_type": "TITLE",
                    },
                    {
                        "name": "PlaceHolder 2",
                        "shape_id": 26,
                        "shape_type": "PLACEHOLDER",
                        "measurement_unit": "emu",
                        "height": 4530600,
                        "width": 8229600,
                        "left": 457200,
                        "top": 1371240,
                        "text": "Karen Crogan\nAssessment Assistant\n406-444-4431  OR kcrogan@mt.gov \nKaren Richem\nAssessment Specialist\n406-444-0748 OR  krichem@mt.gov\nJudy Snow\nState Assessment Director\n406-444-3656 OR jsnow@mt.gov \n",
                        "font_details": [
                            {
                                "paragraph_index": 0,
                                "run_index": 0,
                                "text": "Karen Crogan",
                                "font_name": "Georgia",
                                "font_size": 32.0,
                            },
                            {
                                "paragraph_index": 1,
                                "run_index": 0,
                                "text": "Assessment Assistant",
                                "font_name": "Georgia",
                                "font_size": 28.0,
                            },
                            {
                                "paragraph_index": 2,
                                "run_index": 0,
                                "text": "406-444-4431  OR ",
                                "font_name": "Georgia",
                                "font_size": 28.0,
                            },
                            {
                                "paragraph_index": 2,
                                "run_index": 1,
                                "text": "kcrogan@mt.gov",
                                "font_name": "Georgia",
                                "font_size": 28.0,
                            },
                            {
                                "paragraph_index": 2,
                                "run_index": 2,
                                "text": " ",
                                "font_name": "Georgia",
                                "font_size": 28.0,
                            },
                            {
                                "paragraph_index": 3,
                                "run_index": 0,
                                "text": "Karen Richem",
                                "font_name": "Georgia",
                                "font_size": 32.0,
                            },
                            {
                                "paragraph_index": 4,
                                "run_index": 0,
                                "text": "Assessment Specialist",
                                "font_name": "Georgia",
                                "font_size": 28.0,
                            },
                            {
                                "paragraph_index": 5,
                                "run_index": 0,
                                "text": "406-444-0748 OR  ",
                                "font_name": "Georgia",
                                "font_size": 28.0,
                            },
                            {
                                "paragraph_index": 5,
                                "run_index": 1,
                                "text": "krichem@mt.gov",
                                "font_name": "Georgia",
                                "font_size": 28.0,
                            },
                            {
                                "paragraph_index": 6,
                                "run_index": 0,
                                "text": "Judy Snow",
                                "font_name": "Georgia",
                                "font_size": 32.0,
                            },
                            {
                                "paragraph_index": 7,
                                "run_index": 0,
                                "text": "State Assessment Director",
                                "font_name": "Georgia",
                                "font_size": 28.0,
                            },
                            {
                                "paragraph_index": 8,
                                "run_index": 0,
                                "text": "406-444-3656 OR ",
                                "font_name": "Georgia",
                                "font_size": 28.0,
                            },
                            {
                                "paragraph_index": 8,
                                "run_index": 1,
                                "text": "jsnow@mt.gov",
                                "font_name": "Georgia",
                                "font_size": 28.0,
                            },
                            {
                                "paragraph_index": 8,
                                "run_index": 2,
                                "text": " ",
                                "font_name": "Georgia",
                                "font_size": 28.0,
                            },
                        ],
                        "placeholder_type": "OBJECT",
                    },
                    {
                        "name": "",
                        "shape_id": 27,
                        "shape_type": "PICTURE",
                        "measurement_unit": "emu",
                        "height": 1600200,
                        "width": 1417680,
                        "left": 7238880,
                        "top": 1447920,
                        "auto_shape_type": "RECTANGLE",
                    },
                    {
                        "name": "PlaceHolder 3",
                        "shape_id": 4,
                        "shape_type": "PLACEHOLDER",
                        "measurement_unit": "emu",
                        "height": 476280,
                        "width": 1600200,
                        "left": 7086240,
                        "top": 6244920,
                        "text": "7",
                        "font_details": [],
                        "placeholder_type": "SLIDE_NUMBER",
                    },
                ],
            },
        ],
    }


def test_set_height(sample_json: Dict[str, Any]) -> None:
    """Test setting shape height.

    Args:
        sample_json: Sample JSON data fixture
    """
    # Reset globals before test
    api_json.reset_globals()

    # Initialize with sample data and verify
    api_json.set_json(sample_json)
    assert api_json.JSON_DATA is not None, "JSON_DATA should be set"
    assert isinstance(api_json.JSON_DATA, dict), "JSON_DATA should be a dictionary"
    assert "slides" in api_json.JSON_DATA, "JSON_DATA should contain slides"

    # Choose first slide and shape
    api_json.choose_slide(262)
    assert api_json.JSON_CURRENT_SLIDE is not None, "Slide 262 should be selected"
    assert api_json.JSON_CURRENT_SLIDE["slide_id"] == 262, "Wrong slide selected"

    api_json.choose_shape(25)
    assert api_json.JSON_CURRENT_SHAPE is not None, "Shape 25 should be selected"
    assert api_json.JSON_CURRENT_SHAPE["shape_id"] == 25, "Wrong shape selected"

    # Test setting new height
    new_height = 2000000
    api_json.set_height(new_height)
    assert api_json.JSON_CURRENT_SHAPE["height"] == new_height

    # Test error cases
    with pytest.raises(ValueError, match="Shape with ID .* not found"):
        api_json.choose_shape(999)

    # Test setting height with no shape selected
    api_json.JSON_CURRENT_SHAPE = None
    with pytest.raises(ValueError, match="No shape selected"):
        api_json.set_height(1000000)


def test_set_width(sample_json: Dict[str, Any]) -> None:
    """Test setting shape width.

    Args:
        sample_json: Sample JSON data fixture
    """
    # Reset globals before test
    api_json.reset_globals()

    # Initialize with sample data and verify
    api_json.set_json(sample_json)
    assert api_json.JSON_DATA is not None, "JSON_DATA should be set"
    assert isinstance(api_json.JSON_DATA, dict), "JSON_DATA should be a dictionary"
    assert "slides" in api_json.JSON_DATA, "JSON_DATA should contain slides"

    # Choose first slide and shape
    api_json.choose_slide(262)
    assert api_json.JSON_CURRENT_SLIDE is not None, "Slide 262 should be selected"
    assert api_json.JSON_CURRENT_SLIDE["slide_id"] == 262, "Wrong slide selected"

    api_json.choose_shape(25)
    assert api_json.JSON_CURRENT_SHAPE is not None, "Shape 25 should be selected"
    assert api_json.JSON_CURRENT_SHAPE["shape_id"] == 25, "Wrong shape selected"

    # Test setting new width
    new_width = 3000000
    api_json.set_width(new_width)
    assert api_json.JSON_CURRENT_SHAPE["width"] == new_width

    # Test error cases
    with pytest.raises(ValueError, match="Shape with ID .* not found"):
        api_json.choose_shape(999)

    # Test setting width with no shape selected
    api_json.JSON_CURRENT_SHAPE = None
    with pytest.raises(ValueError, match="No shape selected"):
        api_json.set_width(1000000)


def test_set_top(sample_json: Dict[str, Any]) -> None:
    """Test setting shape top.

    Args:
        sample_json: Sample JSON data fixture
    """
    # Reset globals before test
    api_json.reset_globals()

    # Initialize with sample data and verify
    api_json.set_json(sample_json)
    assert api_json.JSON_DATA is not None, "JSON_DATA should be set"
    assert isinstance(api_json.JSON_DATA, dict), "JSON_DATA should be a dictionary"
    assert "slides" in api_json.JSON_DATA, "JSON_DATA should contain slides"

    # Choose first slide and shape
    api_json.choose_slide(262)
    assert api_json.JSON_CURRENT_SLIDE is not None, "Slide 262 should be selected"
    assert api_json.JSON_CURRENT_SLIDE["slide_id"] == 262, "Wrong slide selected"

    api_json.choose_shape(25)
    assert api_json.JSON_CURRENT_SHAPE is not None, "Shape 25 should be selected"
    assert api_json.JSON_CURRENT_SHAPE["shape_id"] == 25, "Wrong shape selected"

    # Test setting new top
    new_top = 4000000
    api_json.set_top(new_top)
    assert api_json.JSON_CURRENT_SHAPE["top"] == new_top

    # Test error cases
    with pytest.raises(ValueError, match="Shape with ID .* not found"):
        api_json.choose_shape(999)

    # Test setting top with no shape selected
    api_json.JSON_CURRENT_SHAPE = None
    with pytest.raises(ValueError, match="No shape selected"):
        api_json.set_top(1000000)


def test_set_left(sample_json: Dict[str, Any]) -> None:
    """Test setting shape left.

    Args:
        sample_json: Sample JSON data fixture
    """
    # Reset globals before test
    api_json.reset_globals()

    # Initialize with sample data and verify
    api_json.set_json(sample_json)
    assert api_json.JSON_DATA is not None, "JSON_DATA should be set"
    assert isinstance(api_json.JSON_DATA, dict), "JSON_DATA should be a dictionary"
    assert "slides" in api_json.JSON_DATA, "JSON_DATA should contain slides"

    # Choose first slide and shape
    api_json.choose_slide(262)
    assert api_json.JSON_CURRENT_SLIDE is not None, "Slide 262 should be selected"
    assert api_json.JSON_CURRENT_SLIDE["slide_id"] == 262, "Wrong slide selected"

    api_json.choose_shape(25)
    assert api_json.JSON_CURRENT_SHAPE is not None, "Shape 25 should be selected"
    assert api_json.JSON_CURRENT_SHAPE["shape_id"] == 25, "Wrong shape selected"

    # Test setting new left
    new_left = 5000000
    api_json.set_left(new_left)
    assert api_json.JSON_CURRENT_SHAPE["left"] == new_left

    # Test error cases
    with pytest.raises(ValueError, match="Shape with ID .* not found"):
        api_json.choose_shape(999)

    # Test setting left with no shape selected
    api_json.JSON_CURRENT_SHAPE = None
    with pytest.raises(ValueError, match="No shape selected"):
        api_json.set_left(1000000)


def test_add_text_box(sample_json: Dict[str, Any]) -> None:
    """Test adding a text box to a slide.

    Args:
        sample_json: Sample JSON data fixture
    """
    # Reset globals before test
    api_json.reset_globals()

    # Initialize with sample data
    api_json.set_json(sample_json)
    api_json.choose_slide(262)

    # Test adding a regular text box
    api_json.add_text_box(
        left=1000000, top=2000000, width=3000000, height=1500000, text="Test Text Box"
    )

    # Verify the text box was added correctly
    new_shape = api_json.JSON_CURRENT_SLIDE["shapes"][-1]
    assert new_shape["shape_type"] == "TEXT_BOX"
    assert new_shape["left"] == 1000000
    assert new_shape["top"] == 2000000
    assert new_shape["width"] == 3000000
    assert new_shape["height"] == 1500000
    assert new_shape["text"] == "Test Text Box"

    # Test error case - no slide selected
    api_json.JSON_CURRENT_SLIDE = None
    with pytest.raises(ValueError, match="No slide selected"):
        api_json.add_text_box(0, 0, 1000000, 1000000)


def test_add_picture(sample_json: Dict[str, Any]) -> None:
    """Test adding a picture to a slide.

    Args:
        sample_json: Sample JSON data fixture
    """
    # Reset globals before test
    api_json.reset_globals()

    # Initialize with sample data
    api_json.set_json(sample_json)
    api_json.choose_slide(262)

    # Test adding a picture
    api_json.add_picture(
        left=1000000,
        top=2000000,
        width=3000000,
        height=1500000,
        image_file="test_image.png",
    )

    # Verify the picture was added correctly
    new_shape = api_json.JSON_CURRENT_SLIDE["shapes"][-1]
    assert new_shape["shape_type"] == "PICTURE"
    assert new_shape["left"] == 1000000
    assert new_shape["top"] == 2000000
    assert new_shape["width"] == 3000000
    assert new_shape["height"] == 1500000


def test_insert_text(sample_json: Dict[str, Any]) -> None:
    """Test inserting text into a shape.

    Args:
        sample_json: Sample JSON data fixture
    """
    # Reset globals before test
    api_json.reset_globals()

    # Initialize with sample data
    api_json.set_json(sample_json)
    api_json.choose_slide(262)
    api_json.choose_shape(25)

    # Store original text
    original_text = api_json.JSON_CURRENT_SHAPE["text"]

    # Test inserting text
    new_text = "New Text"
    api_json.insert_text(new_text)

    # Verify the text was concatenated correctly
    assert api_json.JSON_CURRENT_SHAPE["text"] == original_text + new_text

    # Test error case - no shape selected
    api_json.JSON_CURRENT_SHAPE = None
    with pytest.raises(ValueError, match="No shape selected"):
        api_json.insert_text("Should Fail")


def test_set_font_size(sample_json: Dict[str, Any]) -> None:
    """Test setting font size in a shape.

    Args:
        sample_json: Sample JSON data fixture
    """
    # Reset globals before test
    api_json.reset_globals()

    # Initialize with sample data
    api_json.set_json(sample_json)
    api_json.choose_slide(262)
    api_json.choose_shape(25)

    # Test setting font size
    new_font_size = 20.0
    api_json.set_font_size(new_font_size)

    # Verify the font size was set correctly for all font details
    for font_detail in api_json.JSON_CURRENT_SHAPE["font_details"]:
        assert font_detail["font_size"] == new_font_size, (
            f"Font size not updated correctly for paragraph {font_detail['paragraph_index']}, "
            f"run {font_detail['run_index']}"
        )

    # Test shape with no font details
    api_json.choose_shape(4)  # Choose shape with empty font_details
    api_json.set_font_size(new_font_size)
    assert len(api_json.JSON_CURRENT_SHAPE["font_details"]) == 1
    assert api_json.JSON_CURRENT_SHAPE["font_details"][0]["font_size"] == new_font_size

    # Test error case - no shape selected
    api_json.JSON_CURRENT_SHAPE = None
    with pytest.raises(ValueError, match="No shape selected"):
        api_json.set_font_size(24.0)


def test_set_font_style(sample_json: Dict[str, Any]) -> None:
    """Test setting font style in a shape.

    Args:
        sample_json: Sample JSON data fixture
    """
    # Reset globals before test
    api_json.reset_globals()

    # Initialize with sample data
    api_json.set_json(sample_json)
    api_json.choose_slide(262)
    api_json.choose_shape(25)

    # Test setting bold style
    api_json.set_font_style("bold")

    # Verify bold style was set correctly for all font details
    for font_detail in api_json.JSON_CURRENT_SHAPE["font_details"]:
        assert font_detail.get("bold") is True, (
            f"Bold style not set correctly for paragraph {font_detail['paragraph_index']}, "
            f"run {font_detail['run_index']}"
        )

    # Test setting italic style
    api_json.set_font_style("italic")

    # Verify italic style was set correctly for all font details
    for font_detail in api_json.JSON_CURRENT_SHAPE["font_details"]:
        assert font_detail.get("italic") is True, (
            f"Italic style not set correctly for paragraph {font_detail['paragraph_index']}, "
            f"run {font_detail['run_index']}"
        )

    # Test error case - no shape selected
    api_json.JSON_CURRENT_SHAPE = None
    with pytest.raises(ValueError, match="No shape selected"):
        api_json.set_font_style("bold")
