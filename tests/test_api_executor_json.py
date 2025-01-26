import pytest

from src.shared.pptx_api.api_executor_json import (
    choose_shape,
    choose_slide,
    reset_globals,
    set_font,
    set_json,
    add_text_box,
    set_font_size,
    JSON_CURRENT_SHAPE,
)


@pytest.fixture
def sample_json():
    return {
        "slides": [
            {
                "slide_id": 1,
                "shapes": [
                    {
                        "shape_id": 1,
                        "text": "Sample Text",
                        "font_details": [
                            {
                                "paragraph_index": 0,
                                "run_index": 0,
                                "text": "Sample Text",
                            }
                        ],
                    }
                ],
            }
        ]
    }


def test_set_font(sample_json):
    # Setup
    set_json(sample_json)
    choose_slide(1)
    choose_shape(1)

    # Test setting font
    result = set_font("Arial")
    assert result is None

    # Verify font was set
    from src.shared.pptx_api.api_executor_json import JSON_CURRENT_SHAPE

    assert JSON_CURRENT_SHAPE["font_details"][0]["font_name"] == "Arial"

    # Reset globals after test
    reset_globals()


def test_set_font_no_shape_selected(sample_json):
    # Setup
    set_json(sample_json)

    # Test without selecting shape
    result = set_font("Arial")
    assert result == "No shape selected"

    # Reset globals after test
    reset_globals()


def test_text_box_creation_with_formatting():
    # Setup initial JSON
    json_data = {
        "slides": [
            {
                "slide_id": 263,
                "shapes": []
            }
        ]
    }
    
    # Test sequence
    set_json(json_data)
    assert choose_slide(263) is None
    assert add_text_box(334800, 1000000, 8477280, 800000, 'Objectives') is None
    assert set_font('Arial') is None
    assert set_font_size(72) is None

    # Verify the results
    shape = JSON_CURRENT_SHAPE
    assert shape is not None
    assert shape["text"] == "Objectives"
    assert shape["left"] == 334800
    assert shape["top"] == 1000000
    assert shape["width"] == 8477280
    assert shape["height"] == 800000
    assert shape["font_details"][0]["font_name"] == "Arial"
    assert shape["font_details"][0]["font_size"] == 72

    # Reset globals after test
    reset_globals()
