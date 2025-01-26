import pytest

import src.shared.pptx_api.api_executor_json as pjson


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
    pjson.set_json(sample_json)
    pjson.choose_slide(1)
    pjson.choose_shape(1)

    # Test setting font
    result = pjson.set_font("Arial")
    assert result is None

    # Verify font was set
    assert pjson.JSON_CURRENT_SHAPE["font_details"][0]["font_name"] == "Arial"

    # Reset globals after test
    pjson.reset_globals()


def test_set_font_no_shape_selected(sample_json):
    # Setup
    pjson.set_json(sample_json)

    # Test without selecting shape
    result = pjson.set_font("Arial")
    assert result == "No shape selected"

    # Reset globals after test
    pjson.reset_globals()


def test_text_box_creation_with_formatting():
    # Setup initial JSON
    json_data = {"slides": [{"slide_id": 263, "shapes": []}]}
    
    # Test sequence
    pjson.set_json(json_data)
    assert pjson.JSON_DATA is not None, "JSON_DATA should not be None after set_json"
    
    result = pjson.choose_slide(263)
    assert result is None, f"choose_slide failed with: {result}"
    assert pjson.JSON_CURRENT_SLIDE is not None, "JSON_CURRENT_SLIDE should not be None"
    
    result = pjson.add_text_box(334800, 1000000, 8477280, 800000, "Objectives")
    assert result is None, f"add_text_box failed with: {result}"
    assert pjson.JSON_CURRENT_SHAPE is not None, "JSON_CURRENT_SHAPE should not be None"
    
    result = pjson.set_font("Arial")
    assert result is None, f"set_font failed with: {result}"
    
    result = pjson.set_font_size(72)
    assert result is None, f"set_font_size failed with: {result}"

    # Verify the results
    shape = pjson.JSON_CURRENT_SHAPE
    assert shape is not None, "Shape is None after operations"
    assert shape["text"] == "Objectives"
    assert shape["left"] == 334800
    assert shape["top"] == 1000000
    assert shape["width"] == 8477280
    assert shape["height"] == 800000
    assert "font_details" in shape, "font_details missing from shape"
    assert shape["font_details"][0]["font_name"] == "Arial"
    assert shape["font_details"][0]["font_size"] == 72

    # Reset globals after test
    pjson.reset_globals()
