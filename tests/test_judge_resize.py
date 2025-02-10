import json

import pytest

from src.modification.judge_lib.judge_resize import judge_answer_resize

@pytest.fixture
def base_presentation_json():
    json_file = "tests/data/test_judge_resize.json"
    with open(json_file, "r") as f:
        return json.load(f)
    
@pytest.fixture
def ground_truth():
    return {"slide_width": 9144000, "slide_height": 6858000, "measurement_unit": "emu", "slide": {"slide_id": 257, "slide_name": "", "shapes": [{"name": "PlaceHolder 1", "shape_id": 19, "shape_type": "PLACEHOLDER", "measurement_unit": "emu", "height": 603360, "width": 7864560, "left": 903240, "top": 217440, "text": "Agenda", "font_details": [{"paragraph_index": 0, "run_index": 0, "text": "Agenda", "font_name": "Arial", "font_size": 24.0}], "placeholder_type": "TITLE"}, {"name": "PlaceHolder 2", "shape_id": 20, "shape_type": "PLACEHOLDER", "measurement_unit": "emu", "height": 5216400, "width": 8458200, "left": 431280, "top": 1216080, "text": "Mission Overview\nNetwork Test\nInterim Support Instructions (ISI)\nC-band Tracking\nFDF Support\nFDF Staffing\nNIC Staffing\nSN Support\nWSC TOA Staffing\nProposed Activities/Open Discussions", "font_details": [{"paragraph_index": 0, "run_index": 0, "text": "Mission Overview", "font_name": "Arial", "font_size": 18.0}, {"paragraph_index": 1, "run_index": 0, "text": "Network Test", "font_name": "Arial", "font_size": 18.0}, {"paragraph_index": 2, "run_index": 0, "text": "Interim Support Instructions (ISI)", "font_name": "Arial", "font_size": 18.0}, {"paragraph_index": 3, "run_index": 0, "text": "C-band Tracking", "font_name": "Arial", "font_size": 18.0}, {"paragraph_index": 4, "run_index": 0, "text": "FDF Support", "font_name": "Arial", "font_size": 18.0}, {"paragraph_index": 5, "run_index": 0, "text": "FDF Staffing", "font_name": "Arial", "font_size": 18.0}, {"paragraph_index": 6, "run_index": 0, "text": "NIC Staffing", "font_name": "Arial", "font_size": 18.0}, {"paragraph_index": 7, "run_index": 0, "text": "SN Support", "font_name": "Arial", "font_size": 18.0}, {"paragraph_index": 8, "run_index": 0, "text": "WSC TOA Staffing", "font_name": "Arial", "font_size": 18.0}, {"paragraph_index": 9, "run_index": 0, "text": "Proposed Activities/Open Discussions", "font_name": "Arial", "font_size": 18.0}], "placeholder_type": "OBJECT"}]}}

@pytest.fixture
def shape_to_modify():
    return {"name": "PlaceHolder 1", "shape_id": 19, "shape_type": "PLACEHOLDER", "measurement_unit": "emu", "height": 603360, "width": 7864560, "left": 903240, "top": 217440, "text": "Agenda", "font_details": [{"paragraph_index": 0, "run_index": 0, "text": "Agenda", "font_name": "Arial", "font_size": 24.0}], "placeholder_type": "TITLE"}

@pytest.fixture
def json_data():
    return {"slide_width": 9144000, "slide_height": 6858000, "measurement_unit": "emu", "slide": {"slide_id": 257, "slide_name": "", "shapes": [{"name": "PlaceHolder 1", "shape_id": 19, "shape_type": "PLACEHOLDER", "measurement_unit": "emu", "height": 603360, "width": 7864560, "left": 903240, "top": 0, "text": "Agenda", "font_details": [{"paragraph_index": 0, "run_index": 0, "text": "Agenda", "font_name": "Arial", "font_size": 24.0}], "placeholder_type": "TITLE"}, {"name": "PlaceHolder 2", "shape_id": 20, "shape_type": "PLACEHOLDER", "measurement_unit": "emu", "height": 5216400, "width": 8458200, "left": 431280, "top": 1216080, "text": "Mission Overview\nNetwork Test\nInterim Support Instructions (ISI)\nC-band Tracking\nFDF Support\nFDF Staffing\nNIC Staffing\nSN Support\nWSC TOA Staffing\nProposed Activities/Open Discussions", "font_details": [{"paragraph_index": 0, "run_index": 0, "text": "Mission Overview", "font_name": "Arial", "font_size": 18.0}, {"paragraph_index": 1, "run_index": 0, "text": "Network Test", "font_name": "Arial", "font_size": 18.0}, {"paragraph_index": 2, "run_index": 0, "text": "Interim Support Instructions (ISI)", "font_name": "Arial", "font_size": 18.0}, {"paragraph_index": 3, "run_index": 0, "text": "C-band Tracking", "font_name": "Arial", "font_size": 18.0}, {"paragraph_index": 4, "run_index": 0, "text": "FDF Support", "font_name": "Arial", "font_size": 18.0}, {"paragraph_index": 5, "run_index": 0, "text": "FDF Staffing", "font_name": "Arial", "font_size": 18.0}, {"paragraph_index": 6, "run_index": 0, "text": "NIC Staffing", "font_name": "Arial", "font_size": 18.0}, {"paragraph_index": 7, "run_index": 0, "text": "SN Support", "font_name": "Arial", "font_size": 18.0}, {"paragraph_index": 8, "run_index": 0, "text": "WSC TOA Staffing", "font_name": "Arial", "font_size": 18.0}, {"paragraph_index": 9, "run_index": 0, "text": "Proposed Activities/Open Discussions", "font_name": "Arial", "font_size": 18.0}], "placeholder_type": "OBJECT"}]}}

def test_judge_answer_resize(base_presentation_json, ground_truth, shape_to_modify, json_data):
    api_calls = ['choose_slide(257)', 'choose_shape(19)', 'set_top(0)']
    result = judge_answer_resize(api_calls, shape_to_modify, json_data, base_presentation_json)
    assert result[0] == True