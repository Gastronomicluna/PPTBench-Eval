import pytest
import json

from src.modification.judge_lib.judge_change_font import (
    compare_slides,
    judge_answer_change_font,
)


@pytest.fixture
def sample_presentation_json():
    json_file = "tests/data/test_judge_change_font.json"
    with open(json_file, "r") as f:
        return json.load(f)


@pytest.fixture
def sample_ground_truth():
    return {"slide_width": 9144000, "slide_height": 6858000, "measurement_unit": "emu", "slide": {"slide_id": 353, "slide_name": "", "shapes": [{"name": "Slide Number Placeholder 4", "shape_id": 583, "shape_type": "AUTO_SHAPE", "measurement_unit": "emu", "height": 476280, "width": 2133720, "left": 6553080, "top": 6245280, "text": "<number>", "font_details": []}, {"name": "PlaceHolder 1", "shape_id": 584, "shape_type": "PLACEHOLDER", "measurement_unit": "emu", "height": 1143000, "width": 9144000, "left": 0, "top": -360, "text": "Additional Personal Data (0077)", "font_details": [{"paragraph_index": 0, "run_index": 0, "text": "Additional Personal Data", "font_name": "Arial Black", "font_size": 30.0}, {"paragraph_index": 0, "run_index": 1, "text": " (0077)", "font_name": "Arial Black", "font_size": 30.0}], "placeholder_type": "TITLE"}, {"name": "PlaceHolder 2", "shape_id": 585, "shape_type": "PLACEHOLDER", "measurement_unit": "emu", "height": 4952880, "width": 3733920, "left": 152280, "top": 1143000, "text": "The Additional Personal Data infotype documents an employee\u2019s Equal Employment Opportunity (EEO) information.\nFor a rehire, verify and correct any data on this infotype.\nWhen finished, click (Enter) and then click (Save). If information is correct, do not save and click (Next Record). ", "font_details": [{"paragraph_index": 0, "run_index": 0, "text": "The Additional Personal Data infotype documents an employee\u2019s Equal Employment Opportunity (EEO) information.", "font_name": "Arial", "font_size": 20.0}, {"paragraph_index": 1, "run_index": 0, "text": "For a rehire, verify and correct any data on this infotype.", "font_name": "Arial", "font_size": 20.0}, {"paragraph_index": 2, "run_index": 0, "text": "When finished, click (Enter) and then click (Save). If information is correct, do not save and click (Next Record). ", "font_name": "Arial", "font_size": 20.0}], "placeholder_type": "OBJECT"}, {"name": "Picture 6", "shape_id": 586, "shape_type": "PICTURE", "measurement_unit": "emu", "height": 304920, "width": 304920, "left": 3035160, "top": 3940200, "auto_shape_type": "RECTANGLE", "image_path": "dataset/extracted_images/7TZWV73FCJEBZUILSPFQ3PCLOSMKS2GQ/97/image_97_4.png"}, {"name": "Picture 7", "shape_id": 587, "shape_type": "PICTURE", "measurement_unit": "emu", "height": 304560, "width": 304920, "left": 2895480, "top": 3602160, "auto_shape_type": "RECTANGLE", "image_path": "dataset/extracted_images/7TZWV73FCJEBZUILSPFQ3PCLOSMKS2GQ/97/image_97_5.png"}, {"name": "Picture 9", "shape_id": 588, "shape_type": "PICTURE", "measurement_unit": "emu", "height": 323640, "width": 311400, "left": 1147680, "top": 4776840, "auto_shape_type": "RECTANGLE", "image_path": "dataset/extracted_images/7TZWV73FCJEBZUILSPFQ3PCLOSMKS2GQ/97/image_97_6.png"}, {"name": "Group 11", "shape_id": 589, "shape_type": "GROUP", "measurement_unit": "emu", "height": 5372280, "width": 4454640, "left": 4308480, "top": 914400, "group_shapes": [{"name": "Picture 2", "shape_id": 590, "shape_type": "PICTURE", "measurement_unit": "emu", "height": 4010040, "width": 4445280, "left": 4314600, "top": 914400, "auto_shape_type": "RECTANGLE"}, {"name": "Picture 3", "shape_id": 591, "shape_type": "PICTURE", "measurement_unit": "emu", "height": 1362600, "width": 4454640, "left": 4308480, "top": 4924080, "auto_shape_type": "RECTANGLE"}]}], "notes": [{"text": "The Additional Personal Data infotype contains employee demographic information used to analyze the demographics within agencies and state employment.\nInformation provided on this infotype produce detail information in Business Intelligence.\nIf information is correct, DO NOT SAVE. Click the \u2018next record\u2019 button to continue.", "font_details": [{"paragraph_index": 0, "run_index": 0, "text": "The ", "font_name": "Calibri", "font_size": 13.0}, {"paragraph_index": 0, "run_index": 1, "text": "Additional Personal Data", "font_name": "Calibri", "font_size": 13.0}, {"paragraph_index": 0, "run_index": 2, "text": " infotype contains employee demographic information used to analyze the demographics within agencies and state employment.", "font_name": "Calibri", "font_size": 13.0}, {"paragraph_index": 1, "run_index": 0, "text": "Information provided on this infotype produce detail information in Business Intelligence.", "font_name": "Calibri", "font_size": 13.0}, {"paragraph_index": 2, "run_index": 0, "text": "If information is correct, DO NOT SAVE. Click the \u2018next record\u2019 button to continue.", "font_name": "Calibri", "font_size": 13.0}]}]}}


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

# def test_judge_answer_change_font_correct(sample_presentation_json, sample_ground_truth):
#     """Test font change judgment with correct API calls."""
#     api_calls = ['choose_slide(256)', 'choose_shape(11)', "set_font('Verdana')", 'choose_shape(12)', "set_font('Verdana')", 'choose_shape(13)', "set_font('Verdana')", 'choose_shape(14)', "set_font('Verdana')"]
#     is_correct, reason = judge_answer_change_font(
#         api_calls, sample_ground_truth, sample_presentation_json
#     )
#     # assert is_correct is True
#     assert reason == "Slides are the same"