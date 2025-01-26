import pytest
from src.shared.pptx_api.api_executor_json import (
    set_json,
    choose_slide,
    choose_shape,
    set_font,
    reset_globals,
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
                                "text": "Sample Text"
                            }
                        ]
                    }
                ]
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
