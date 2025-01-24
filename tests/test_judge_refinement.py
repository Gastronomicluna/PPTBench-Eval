import json

import pytest

from src.modification.judge_lib.judge_refinement import judge_answer_refinement
from src.modification.utils import has_overlap
@pytest.fixture
def base_presentation_json():
    json_file = "tests/data/test_judge_refinement.json"
    with open(json_file, "r") as f:
        return json.load(f)
    

@pytest.fixture
def shape_to_modify():
    return {"name": "PlaceHolder 2", "shape_id": 22, "shape_type": "PLACEHOLDER", "measurement_unit": "emu", "height": 4114800, "width": 8229600, "left": 609480, "top": 1752480, "text": "Different patient populations\nNa\u00efve subjects harboring resistant virus\nLimited or Intermediate prior treatment with resistance\nExtensive prior treatment with resistance with limited treatment options", "font_details": [{"paragraph_index": 0, "run_index": 0, "text": "Different patient populations", "font_name": "Arial", "font_size": 32.0}, {"paragraph_index": 1, "run_index": 0, "text": "Na\u00efve subjects harboring resistant virus", "font_name": "Arial", "font_size": 28.0}, {"paragraph_index": 2, "run_index": 0, "text": "Limited or Intermediate prior treatment with resistance", "font_name": "Arial", "font_size": 28.0}, {"paragraph_index": 3, "run_index": 0, "text": "Extensive prior treatment with resistance with limited treatment options", "font_name": "Arial", "font_size": 28.0}], "placeholder_type": "OBJECT"}

@pytest.fixture
def ground_truth():
    return {"slide_width": 9144000, "slide_height": 6858000, "measurement_unit": "emu", "slide": {"slide_id": 257, "slide_name": "", "shapes": [{"name": "PlaceHolder 1", "shape_id": 21, "shape_type": "PLACEHOLDER", "measurement_unit": "emu", "height": 1143000, "width": 8229600, "left": 457200, "top": 274320, "text": "HIV Drug Resistance ", "font_details": [{"paragraph_index": 0, "run_index": 0, "text": "HIV Drug Resistance ", "font_name": "Arial", "font_size": 44.0}], "placeholder_type": "TITLE"}, {"name": "PlaceHolder 2", "shape_id": 22, "shape_type": "PLACEHOLDER", "measurement_unit": "emu", "height": 4114800, "width": 8229600, "left": 609480, "top": 1752480, "text": "Different patient populations\nNa\u00efve subjects harboring resistant virus\nLimited or Intermediate prior treatment with resistance\nExtensive prior treatment with resistance with limited treatment options", "font_details": [{"paragraph_index": 0, "run_index": 0, "text": "Different patient populations", "font_name": "Arial", "font_size": 32.0}, {"paragraph_index": 1, "run_index": 0, "text": "Na\u00efve subjects harboring resistant virus", "font_name": "Arial", "font_size": 28.0}, {"paragraph_index": 2, "run_index": 0, "text": "Limited or Intermediate prior treatment with resistance", "font_name": "Arial", "font_size": 28.0}, {"paragraph_index": 3, "run_index": 0, "text": "Extensive prior treatment with resistance with limited treatment options", "font_name": "Arial", "font_size": 28.0}], "placeholder_type": "OBJECT"}, {"name": "PlaceHolder 3", "shape_id": 4, "shape_type": "PLACEHOLDER", "measurement_unit": "emu", "height": 476280, "width": 2133720, "left": 6552720, "top": 6244920, "text": "2", "font_details": [], "placeholder_type": "SLIDE_NUMBER"}]}}

@pytest.fixture
def json_data():
    return {'slide_width': 9144000, 'slide_height': 6858000, 'measurement_unit': 'emu', 'slide': {'slide_id': 257, 'slide_name': '', 'shapes': [{'name': 'PlaceHolder 1', 'shape_id': 21, 'shape_type': 'PLACEHOLDER', 'measurement_unit': 'emu', 'height': 1143000, 'width': 8229600, 'left': 457200, 'top': 274320, 'text': 'HIV Drug Resistance ', 'font_details': [{'paragraph_index': 0, 'run_index': 0, 'text': 'HIV Drug Resistance ', 'font_name': 'Arial', 'font_size': 44.0}], 'placeholder_type': 'TITLE'}, {'name': 'PlaceHolder 2', 'shape_id': 22, 'shape_type': 'PLACEHOLDER', 'measurement_unit': 'emu', 'height': 4114800, 'width': 8229600, 'left': 515599, 'top': -74874, 'text': 'Different patient populations\nNaïve subjects harboring resistant virus\nLimited or Intermediate prior treatment with resistance\nExtensive prior treatment with resistance with limited treatment options', 'font_details': [{'paragraph_index': 0, 'run_index': 0, 'text': 'Different patient populations', 'font_name': 'Arial', 'font_size': 32.0}, {'paragraph_index': 1, 'run_index': 0, 'text': 'Naïve subjects harboring resistant virus', 'font_name': 'Arial', 'font_size': 28.0}, {'paragraph_index': 2, 'run_index': 0, 'text': 'Limited or Intermediate prior treatment with resistance', 'font_name': 'Arial', 'font_size': 28.0}, {'paragraph_index': 3, 'run_index': 0, 'text': 'Extensive prior treatment with resistance with limited treatment options', 'font_name': 'Arial', 'font_size': 28.0}], 'placeholder_type': 'OBJECT'}, {'name': 'PlaceHolder 3', 'shape_id': 4, 'shape_type': 'PLACEHOLDER', 'measurement_unit': 'emu', 'height': 476280, 'width': 2133720, 'left': 6552720, 'top': 6244920, 'text': '2', 'font_details': [], 'placeholder_type': 'SLIDE_NUMBER'}]}}

def test_overlap(json_data, ground_truth):
    slide_json = json_data["slide"]
    assert has_overlap(slide_json) == True
    ground_truth_slide = ground_truth["slide"]
    assert has_overlap(ground_truth_slide) == False

def test_judge_answer_refinement_success(json_data, base_presentation_json, ground_truth):
    """Test successful refinement with valid shape position."""
    api_calls = [
        "choose_slide(257)",
        "choose_shape(22)",
        "set_top(1752480)",
        "set_left(609480)",
    ]
    
    result = judge_answer_refinement(
        api_calls=api_calls,
        json_data=json_data,
        ground_truth=ground_truth,
        presentation_json=base_presentation_json,
    )
    
    assert result is True
