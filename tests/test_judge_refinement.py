import json

import pytest

from src.modification.judge_lib.judge_refinement import judge_answer_refinement

@pytest.fixture
def base_presentation_json():
    json_file = "tests/data/test_judge_refinement.json"
    with open(json_file, "r") as f:
        return json.load(f)
    

@pytest.fixture
def shape_to_modify():
    return {"name": "PlaceHolder 2", "shape_id": 22, "shape_type": "PLACEHOLDER", "measurement_unit": "emu", "height": 4114800, "width": 8229600, "left": 609480, "top": 1752480, "text": "Different patient populations\nNa\u00efve subjects harboring resistant virus\nLimited or Intermediate prior treatment with resistance\nExtensive prior treatment with resistance with limited treatment options", "font_details": [{"paragraph_index": 0, "run_index": 0, "text": "Different patient populations", "font_name": "Arial", "font_size": 32.0}, {"paragraph_index": 1, "run_index": 0, "text": "Na\u00efve subjects harboring resistant virus", "font_name": "Arial", "font_size": 28.0}, {"paragraph_index": 2, "run_index": 0, "text": "Limited or Intermediate prior treatment with resistance", "font_name": "Arial", "font_size": 28.0}, {"paragraph_index": 3, "run_index": 0, "text": "Extensive prior treatment with resistance with limited treatment options", "font_name": "Arial", "font_size": 28.0}], "placeholder_type": "OBJECT"}

@pytest.fixture
def 