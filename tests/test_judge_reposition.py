import json

import pytest

from src.modification.judge_lib.judge_reposition import compare_shape_position


@pytest.fixture
def base_presentation_json():
    json_file = "tests/data/test_judge_reposition.json"
    with open(json_file, "r") as f:
        return json.load(f)


@pytest.fixture
def shape_to_modify():
    return {
        "name": "PlaceHolder 1",
        "shape_id": 149,
        "shape_type": "PLACEHOLDER",
        "measurement_unit": "emu",
        "height": 685800,
        "width": 9144000,
        "left": 0,
        "top": 609120,
        "text": "Consumer Information and Disclosure ",
        "font_details": [
            {
                "paragraph_index": 0,
                "run_index": 0,
                "text": "Consumer Information and Disclosure",
                "font_name": "Verdana",
                "font_size": 32.0,
            },
            {
                "paragraph_index": 0,
                "run_index": 1,
                "text": " ",
                "font_name": "Verdana",
                "font_size": 32.0,
            },
        ],
        "placeholder_type": "TITLE",
    }


@pytest.fixture
def api_calls():
    return ["choose_slide(266)", "choose_shape(149)", "set_top(0)"]


@pytest.fixture
def json_data():
    return {
        "slide_width": 9144000,
        "slide_height": 6858000,
        "measurement_unit": "emu",
        "slide": {
            "slide_id": 266,
            "slide_name": "",
            "shapes": [
                {
                    "name": "PlaceHolder 1",
                    "shape_id": 149,
                    "shape_type": "PLACEHOLDER",
                    "measurement_unit": "emu",
                    "height": 685800,
                    "width": 9144000,
                    "left": 0,
                    "top": 0,
                    "text": "Consumer Information and Disclosure ",
                    "font_details": [
                        {
                            "paragraph_index": 0,
                            "run_index": 0,
                            "text": "Consumer Information and Disclosure",
                            "font_name": "Verdana",
                            "font_size": 32.0,
                        },
                        {
                            "paragraph_index": 0,
                            "run_index": 1,
                            "text": " ",
                            "font_name": "Verdana",
                            "font_size": 32.0,
                        },
                    ],
                    "placeholder_type": "TITLE",
                },
                {
                    "name": "PlaceHolder 2",
                    "shape_id": 150,
                    "shape_type": "PLACEHOLDER",
                    "measurement_unit": "emu",
                    "height": 4343400,
                    "width": 8534160,
                    "left": 304920,
                    "top": 1599840,
                    "text": "Greater transparency in college costs\nED required to develop & release:\nInformation relevant to college cost & net price by institution \nCollege cost & net price watch lists\nInternet-based calculators of the net price of college for consumers",
                    "font_details": [
                        {
                            "paragraph_index": 0,
                            "run_index": 0,
                            "text": "Greater transparency in college costs",
                            "font_name": "Verdana",
                            "font_size": 30.0,
                        },
                        {
                            "paragraph_index": 1,
                            "run_index": 0,
                            "text": "ED required to develop & release:",
                            "font_name": "Verdana",
                            "font_size": 30.0,
                        },
                        {
                            "paragraph_index": 2,
                            "run_index": 0,
                            "text": "Information relevant to college cost & net price by institution ",
                            "font_name": "Verdana",
                            "font_size": 30.0,
                        },
                        {
                            "paragraph_index": 3,
                            "run_index": 0,
                            "text": "College cost & net price watch lists",
                            "font_name": "Verdana",
                            "font_size": 30.0,
                        },
                        {
                            "paragraph_index": 4,
                            "run_index": 0,
                            "text": "Internet-based calculators of the net price of college for consumers",
                            "font_name": "Verdana",
                            "font_size": 30.0,
                        },
                    ],
                    "placeholder_type": "OBJECT",
                },
                {
                    "name": "Slide Number Placeholder 3",
                    "shape_id": 151,
                    "shape_type": "AUTO_SHAPE",
                    "measurement_unit": "emu",
                    "height": 457200,
                    "width": 1905120,
                    "left": 7086600,
                    "top": 6400800,
                    "text": "<number>",
                    "font_details": [],
                },
            ],
        },
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
