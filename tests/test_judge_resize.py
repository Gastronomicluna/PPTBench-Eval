import json

import pytest

from src.modification.judge_lib.judge_resize import judge_answer_resize

@pytest.fixture
def base_presentation_json():
    json_file = "tests/data/test_judge_resize.json"
    with open(json_file, "r") as f:
        return json.load(f)