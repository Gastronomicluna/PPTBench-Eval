import pytest
import json

from src.modification.judge_lib.judge_change_font import (
    compare_slides,
    judge_answer_change_font,
)


@pytest.fixture
def base_presentation_json():
    json_file = "tests/data/test_judge_change_font.json"
    with open(json_file, "r") as f:
        return json.load(f)


@pytest.fixture
def sample_ground_truth():
    return {
        "slide": {
            "slide_id": "slide1",
            "shapes": [
                {
                    "shape_id": "shape1",
                    "text": "Hello",
                    "font": {"name": "Times New Roman", "size": 14},
                }
            ],
        }
    }


def test_compare_slides_identical():
    """Test comparing identical slides."""
    slide1 = {"slide_id": "1", "shapes": [{"text": "Test"}]}
    slide2 = {"slide_id": "1", "shapes": [{"text": "Test"}]}

    is_same, reason = compare_slides(slide1, slide2)
    assert is_same is True
    assert reason == "Slides are the same"


def test_compare_slides_different():
    """Test comparing different slides."""
    slide1 = {"slide_id": "1", "shapes": [{"text": "Test"}]}
    slide2 = {"slide_id": "1", "shapes": [{"text": "Different"}]}

    is_same, reason = compare_slides(slide1, slide2)
    assert is_same is False
    assert reason == "Slides are different"


def test_judge_answer_change_font_invalid_api(
    sample_presentation_json, sample_ground_truth
):
    """Test font change judgment with invalid API calls."""
    api_calls = ["invalid.api.call()"]

    is_correct, reason = judge_answer_change_font(
        api_calls, sample_ground_truth, sample_presentation_json
    )
    assert is_correct is False
    assert "Error executing API calls" in reason
