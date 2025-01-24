import pytest
from src.modification.judge_lib.judge_change_font import judge_answer_change_font
import json
@pytest.fixture
def sample_presentation_json():
    json_file = "tests/data/test_judge_change_font.json"
    with open(json_file, "r") as f:
        return json.load(f)

@pytest.fixture
def sample_shape_to_modify():
    return {'name': 'PlaceHolder 1', 'shape_id': 100, 'shape_type': 'PLACEHOLDER', 'measurement_unit': 'emu', 'height': 1143000, 'width': 7924680, 'left': 1218960, 'top': 75960, 'text': 'mapping the services', 'font_details': [{'paragraph_index': 0, 'run_index': 0, 'text': 'mapping the services', 'font_name': 'NaturaRoman', 'font_size': 36.0}], 'placeholder_type': 'TITLE'}

@pytest.fixture
def sample_ground_truth():
    return {"slide_width": 9144000, "slide_height": 6858000, "measurement_unit": "emu", "slide": {"slide_id": 265, "slide_name": "", "shapes": [{"name": "PlaceHolder 1", "shape_id": 100, "shape_type": "PLACEHOLDER", "measurement_unit": "emu", "height": 1143000, "width": 7924680, "left": 1218960, "top": 75960, "text": "mapping the services", "font_details": [{"paragraph_index": 0, "run_index": 0, "text": "mapping the services", "font_name": "Tahoma", "font_size": 36.0}], "placeholder_type": "TITLE"}, {"name": "", "shape_id": 101, "shape_type": "AUTO_SHAPE", "measurement_unit": "emu", "height": 1069920, "width": 8534520, "left": 228600, "top": 2739960, "text": "\u000b\u000bCarbon Storage \u000b \u000bHow much carbon is currently being held in the forest? What is the carbon sequestration potential?\u000b\u000b Method 1: \u201cFake Age\u201d Estimated biomass based on stand size class for forest cover based on USFS (Smith et al. 2005) estimates for other pools (standing dead wood, understory, dead and down wood, forest floor, soil ) (data: USFS Calveg using WHR classification)\u000b\u000b\u000bMethod 2: \u201cObserved\u201d based on stand survey and interpolation and same estimates for other pools (data: USFS R5 Strata Grid, LEMMA program Oregon State Univ.)", "font_details": [{"paragraph_index": 0, "run_index": 0, "text": "Carbon Storage", "font_name": "Times New Roman", "font_size": 24.0}, {"paragraph_index": 0, "run_index": 1, "text": " ", "font_name": "Times New Roman", "font_size": 24.0}, {"paragraph_index": 0, "run_index": 2, "text": " ", "font_name": "Times New Roman", "font_size": 16.0}, {"paragraph_index": 0, "run_index": 3, "text": "How much carbon is currently being held in the forest? What is the carbon sequestration potential?", "font_name": "Times New Roman", "font_size": 26.0}, {"paragraph_index": 0, "run_index": 4, "text": " ", "font_name": "Times New Roman", "font_size": 22.0}, {"paragraph_index": 0, "run_index": 5, "text": "Method 1: \u201cFake Age\u201d Estimated biomass based on stand size class for forest cover based on USFS (Smith et al. 2005) estimates for other pools (", "font_name": "Times New Roman", "font_size": 24.0}, {"paragraph_index": 0, "run_index": 6, "text": "standing dead wood, understory, dead and down wood, forest floor, soil ", "font_name": "NaturaRoman", "font_size": 24.0}, {"paragraph_index": 0, "run_index": 7, "text": ")", "font_name": "NaturaRoman", "font_size": 24.0}, {"paragraph_index": 0, "run_index": 8, "text": " (d", "font_name": "Times New Roman", "font_size": 14.0}, {"paragraph_index": 0, "run_index": 9, "text": "ata: USFS Calveg using WHR classification)", "font_name": "Times New Roman", "font_size": 14.0}, {"paragraph_index": 0, "run_index": 10, "text": "Method 2: \u201cObserved\u201d based on stand survey and interpolation and same estimates for other pools", "font_name": "Times New Roman", "font_size": 24.0}, {"paragraph_index": 0, "run_index": 11, "text": " ", "font_name": "Times New Roman", "font_size": 20.0}, {"paragraph_index": 0, "run_index": 12, "text": "(data: USFS R5 Strata Grid, LEMMA program Oregon State Univ.)", "font_name": "Times New Roman", "font_size": 14.0}]}]}}

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
