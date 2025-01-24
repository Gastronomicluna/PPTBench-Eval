import json

import pytest

from src.modification.judge_lib.judge_reposition import (
    judge_answer_reposition,
    shape_reposition_score,
    compare_shape_position,
)


@pytest.fixture
def base_presentation_json():
    json_file = "tests/data/test_judge_reposition.json"
    with open(json_file, "r") as f:
        return json.load(f)
