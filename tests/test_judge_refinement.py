import json

import pytest

from src.modification.judge_lib.judge_refinement import judge_answer_refinement

@pytest.fixture
def base_presentation_json():
    json_file = "tests/data/test_judge_refinement.json"
    with open(json_file, "r") as f:
        return json.load(f)