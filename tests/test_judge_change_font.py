import pytest
from src.modification.judge_lib.judge_change_font import judge_answer_change_font
import json
@pytest.fixture
def sample_presentation_json():
    json_file = "tests/data/test.json"
    with open(json_file, "r") as f:
        return json.load(f)

@pytest.fixture
def sample_shape_to_modify():
    return {"shape_id": "shape1"}

@pytest.fixture
def sample_ground_truth():
    return {
        "slide": {"slide_id": "slide1"},
        "shapes": [
            {
                "shape_id": "shape1",
                "text": {
                    "paragraphs": [
                        {
                            "runs": [
                                {"font": {"name": "Calibri"}}
                            ]
                        }
                    ]
                }
            }
        ]
    }

def test_successful_font_change():
    """Test successful font change matching ground truth."""
    api_calls = ['shape.font.name = "Calibri"']
    result = judge_answer_change_font(
        api_calls=api_calls,
        shape_to_modify=sample_shape_to_modify(),
        ground_truth=sample_ground_truth(),
        presentation_json=sample_presentation_json()
    )
    assert result is True

def test_incorrect_font_change():
    """Test incorrect font change not matching ground truth."""
    api_calls = ['shape.font.name = "Times New Roman"']
    result = judge_answer_change_font(
        api_calls=api_calls,
        shape_to_modify=sample_shape_to_modify(),
        ground_truth=sample_ground_truth(),
        presentation_json=sample_presentation_json()
    )
    assert result is False

def test_invalid_api_calls():
    """Test handling of invalid API calls."""
    api_calls = ['invalid.api.call()']
    result = judge_answer_change_font(
        api_calls=api_calls,
        shape_to_modify=sample_shape_to_modify(),
        ground_truth=sample_ground_truth(),
        presentation_json=sample_presentation_json()
    )
    assert result is False

def test_multiple_fonts_in_shape():
    """Test handling of multiple fonts in a shape."""
    multi_font_presentation = {
        "slides": [{
            "slide_id": "slide1",
            "shapes": [{
                "shape_id": "shape1",
                "text": {
                    "paragraphs": [
                        {
                            "runs": [
                                {"font": {"name": "Arial"}},
                                {"font": {"name": "Calibri"}}
                            ]
                        }
                    ]
                }
            }]
        }]
    }
    api_calls = ['shape.font.name = "Calibri"']
    result = judge_answer_change_font(
        api_calls=api_calls,
        shape_to_modify=sample_shape_to_modify(),
        ground_truth=sample_ground_truth(),
        presentation_json=multi_font_presentation
    )
    assert result is False
