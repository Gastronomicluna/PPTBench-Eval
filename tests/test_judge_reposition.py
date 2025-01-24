import json

import pytest

from src.modification.judge_lib.judge_reposition import (
    compare_shape_position,
    judge_answer_reposition,
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
    ground_truth_shape = shape_to_modify.copy()
    result_shape = shape_to_modify.copy()

    assert compare_shape_position(ground_truth_shape, result_shape)


def test_shape_reposition_score_not_matching(shape_to_modify):
    """Test score calculation with not matching shapes."""
    ground_truth_shape = shape_to_modify.copy()
    result_shape = shape_to_modify.copy()
    result_shape["left"] += 10000000

    assert not compare_shape_position(ground_truth_shape, result_shape)[0]
