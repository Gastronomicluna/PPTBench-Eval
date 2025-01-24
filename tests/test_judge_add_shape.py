import pytest
from src.modification.judge_lib.judge_add_shape import judge_answer_add_shape


@pytest.fixture
def base_presentation_json():
    return {
        "slide_height": 1000,
        "slide_width": 1000,
        "slides": [
            {
                "id": "slide1",
                "shapes": [
                    {
                        "left": 100,
                        "top": 100,
                        "width": 200,
                        "height": 200,
                        "text": "Existing Shape",
                    }
                ],
            }
        ],
    }


@pytest.fixture
def json_data_minus_one():
    return {
        "slide": {
            "id": "slide1",
            "shapes": [
                {
                    "left": 100,
                    "top": 100,
                    "width": 200,
                    "height": 200,
                    "text": "Existing Shape",
                }
            ],
        }
    }


def test_successful_shape_addition():
    """Test case for successful shape addition."""
    api_calls = [
        "add_shape('rectangle', 'slide1', 400, 400, 200, 200)",
        "set_shape_text(1, 'New Shape')",
    ]
    
    shape_to_modify = {
        "slide_id": "slide1",
        "left": 400,
        "top": 400,
        "width": 200,
        "height": 200,
        "text": "New Shape",
    }
    
    result = judge_answer_add_shape(
        api_calls=api_calls,
        shape_to_modify=shape_to_modify,
        json_data=json_data_minus_one(),
        presentation_json=base_presentation_json(),
    )
    
    assert result is True


def test_out_of_bounds_shape():
    """Test case for shape added out of bounds."""
    api_calls = [
        "add_shape('rectangle', 'slide1', 900, 900, 200, 200)",
        "set_shape_text(1, 'Out of Bounds')",
    ]
    
    shape_to_modify = {
        "slide_id": "slide1",
        "left": 900,
        "top": 900,
        "width": 200,
        "height": 200,
        "text": "Out of Bounds",
    }
    
    result = judge_answer_add_shape(
        api_calls=api_calls,
        shape_to_modify=shape_to_modify,
        json_data=json_data_minus_one(),
        presentation_json=base_presentation_json(),
    )
    
    assert result is False


def test_overlapping_shape():
    """Test case for overlapping shapes."""
    api_calls = [
        "add_shape('rectangle', 'slide1', 150, 150, 200, 200)",
        "set_shape_text(1, 'Overlapping Shape')",
    ]
    
    shape_to_modify = {
        "slide_id": "slide1",
        "left": 150,
        "top": 150,
        "width": 200,
        "height": 200,
        "text": "Overlapping Shape",
    }
    
    result = judge_answer_add_shape(
        api_calls=api_calls,
        shape_to_modify=shape_to_modify,
        json_data=json_data_minus_one(),
        presentation_json=base_presentation_json(),
    )
    
    assert result is False


def test_incorrect_shape_properties():
    """Test case for shape with incorrect properties."""
    api_calls = [
        "add_shape('rectangle', 'slide1', 400, 400, 200, 200)",
        "set_shape_text(1, 'Wrong Text')",
    ]
    
    shape_to_modify = {
        "slide_id": "slide1",
        "left": 400,
        "top": 400,
        "width": 200,
        "height": 200,
        "text": "Correct Text",
    }
    
    result = judge_answer_add_shape(
        api_calls=api_calls,
        shape_to_modify=shape_to_modify,
        json_data=json_data_minus_one(),
        presentation_json=base_presentation_json(),
    )
    
    assert result is False
