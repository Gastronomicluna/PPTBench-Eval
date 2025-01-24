import json

import pytest

from src.modification.judge_lib.judge_reposition import (
    compare_shape_position,
    judge_answer_reposition,
    shape_reposition_score,
)


@pytest.fixture
def base_presentation_json():
    json_file = "tests/data/test_judge_reposition.json"
    with open(json_file, "r") as f:
        return json.load(f)


@pytest.fixture
def shape_to_modify():
    return {
        "name": "PlaceHolder 1",
        "shape_id": 17,
        "shape_type": "PLACEHOLDER",
        "measurement_unit": "emu",
        "height": 533520,
        "width": 7772400,
        "left": 685800,
        "top": 152280,
        "text": "Near Term Priorities (Booster)",
        "font_details": [
            {
                "paragraph_index": 0,
                "run_index": 0,
                "text": "Near Term Priorities (Booster)",
                "font_name": "Comic Sans MS",
                "font_size": 24.0,
            }
        ],
        "placeholder_type": "TITLE",
    }


def test_shape_reposition_score_exact_match(shape_to_modify):
    """Test score calculation with exactly matching shapes."""
    score = shape_reposition_score(shape_to_modify, shape_to_modify.copy())
    assert score == 1.0


def test_shape_reposition_score_near_match(shape_to_modify):
    """Test score calculation with slightly different positions."""
    modified_shape = shape_to_modify.copy()
    modified_shape["top"] = 154000  # Small difference in EMU
    modified_shape["left"] = 687000  # Small difference in EMU
    score = shape_reposition_score(shape_to_modify, modified_shape)
    assert score > 0.95
    assert score < 1.0


def test_shape_reposition_score_dimension_mismatch(shape_to_modify):
    """Test score calculation with different dimensions."""
    modified_shape = shape_to_modify.copy()
    modified_shape["height"] = 400000  # Different height in EMU
    score = shape_reposition_score(shape_to_modify, modified_shape)
    assert score == pytest.approx(0.7, rel=0.1)


def test_compare_shape_position_exact_match(shape_to_modify):
    """Test position comparison with exact match."""
    assert compare_shape_position(shape_to_modify, shape_to_modify.copy())


def test_compare_shape_position_near_match(shape_to_modify):
    """Test position comparison with near match."""
    modified_shape = shape_to_modify.copy()
    modified_shape["top"] = 154000  # Small difference in EMU
    assert compare_shape_position(shape_to_modify, modified_shape, threshold=0.95)


def test_compare_shape_position_mismatch(shape_to_modify):
    """Test position comparison with clear mismatch."""
    modified_shape = shape_to_modify.copy()
    modified_shape["top"] = 300000  # Large difference in EMU
    assert not compare_shape_position(shape_to_modify, modified_shape)


# def test_judge_answer_reposition(base_presentation_json):
#     """Test the main judge function with sample API calls."""
#     api_calls = ["shape = slide.shapes[0]", "shape.top = 152280", "shape.left = 685800"]
#     shape_to_modify = {
#         "shape_id": 17,
#         "slide_id": 1,
#         "top": 152280,
#         "left": 685800,
#         "height": 533520,
#         "width": 7772400,
#     }
#     json_data = {"slide": {"slide_id": 1}}

#     result = judge_answer_reposition(
#         api_calls, shape_to_modify, json_data, base_presentation_json
#     )
#     assert isinstance(result, bool)
