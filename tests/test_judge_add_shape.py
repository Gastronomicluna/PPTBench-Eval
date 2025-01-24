import json

import pytest

from src.modification.judge_lib.judge_add_shape import (
    get_new_shape,
    judge_answer_add_shape,
)


@pytest.fixture
def base_presentation_json():
    json_file = "tests/data/test.json"
    with open(json_file, "r") as f:
        return json.load(f)


@pytest.fixture
def json_data_minus_one():
    return {
        "slide_width": 9144000,
        "slide_height": 6858000,
        "measurement_unit": "emu",
        "slide": {
            "slide_id": 264,
            "slide_name": "",
            "shapes": [
                {
                    "name": "PlaceHolder 2",
                    "shape_id": 89,
                    "shape_type": "PLACEHOLDER",
                    "measurement_unit": "emu",
                    "height": 914400,
                    "width": 9144000,
                    "left": 0,
                    "top": 2057400,
                    "text": "Robert J. Kuligowski\nNOAA/NESDIS/Office of Research and Applications",
                    "font_details": [
                        {
                            "paragraph_index": 0,
                            "run_index": 0,
                            "text": "Robert J. Kuligowski",
                            "font_name": "Arial",
                            "font_size": 28.0,
                        },
                        {
                            "paragraph_index": 1,
                            "run_index": 0,
                            "text": "NOAA/NESDIS/Office of Research and Applications",
                            "font_name": "Arial",
                            "font_size": 20.0,
                        },
                    ],
                    "placeholder_type": "SUBTITLE",
                },
                {
                    "name": "",
                    "shape_id": 90,
                    "shape_type": "AUTO_SHAPE",
                    "measurement_unit": "emu",
                    "height": 3464280,
                    "width": 8229600,
                    "left": 457200,
                    "top": 3313080,
                    "text": "Research Question: How will the increase in frequency of GOES imagery from 15 min to 5 min impact precipitation estimates?\nMethodology: Run the Hydro-Estimator (H-E) precipitation algorithm on 5-min GOES-11 data that were made available in support of the International H2O Project in June 2002 and compare the hourly totals for sampling rates of 30, 15, and 5 min with Stage IV fields.\nResults: A consistently positive, albeit small, positive impact—the H-E’s dry bias was reduced and correlation between the estimates and observations improved slightly.",
                    "font_details": [
                        {
                            "paragraph_index": 0,
                            "run_index": 0,
                            "text": "Research Question:",
                            "font_name": "Arial",
                            "font_size": 20.0,
                        },
                        {
                            "paragraph_index": 0,
                            "run_index": 1,
                            "text": " How will the increase in frequency of GOES imagery from 15 min to 5 min impact precipitation estimates?",
                            "font_name": "Arial",
                            "font_size": 18.0,
                        },
                        {
                            "paragraph_index": 1,
                            "run_index": 0,
                            "text": "Methodology:",
                            "font_name": "Arial",
                            "font_size": 20.0,
                        },
                        {
                            "paragraph_index": 1,
                            "run_index": 1,
                            "text": " Run the Hydro-Estimator (H-E) precipitation algorithm on 5-min GOES-11 data that were made available in support of the International H2O Project in June 2002 and compare the hourly totals for sampling rates of 30, 15, and 5 min with Stage IV fields.",
                            "font_name": "Arial",
                            "font_size": 18.0,
                        },
                        {
                            "paragraph_index": 2,
                            "run_index": 0,
                            "text": "Results:",
                            "font_name": "Arial",
                            "font_size": 20.0,
                        },
                        {
                            "paragraph_index": 2,
                            "run_index": 1,
                            "text": " A consistently positive, albeit small, positive impact—the H-E’s dry bias was reduced and correlation between the estimates and observations improved slightly.",
                            "font_name": "Arial",
                            "font_size": 18.0,
                        },
                    ],
                },
            ],
        },
    }


@pytest.fixture
def shape_to_modify():
    return {
        "name": "PlaceHolder 1",
        "shape_id": 88,
        "shape_type": "PLACEHOLDER",
        "measurement_unit": "emu",
        "height": 1371600,
        "width": 8229600,
        "left": 457200,
        "top": 457200,
        "text": "Projected Impacts of ABI Data on Satellite-Based Precipitation Estimation Part I: Enhanced Temporal Resolution",
        "font_details": [
            {
                "paragraph_index": 0,
                "run_index": 0,
                "text": "Projected Impacts of ABI Data on Satellite-Based Precipitation Estimation Part I: Enhanced Temporal Resolution",
                "font_name": "Arial",
                "font_size": 20.0,
            }
        ],
        "placeholder_type": "TITLE",
    }


@pytest.fixture
def slide_with_n_shape():
    return {
        "slide_id": 264,
        "slide_name": "",
        "shapes": [
            {
                "name": "PlaceHolder 2",
                "shape_id": 89,
                "shape_type": "PLACEHOLDER",
                "measurement_unit": "emu",
                "height": 914400,
                "width": 9144000,
                "left": 0,
                "top": 2057400,
                "text": "Robert J. Kuligowski\nNOAA/NESDIS/Office of Research and Applications",
                "font_details": [
                    {
                        "paragraph_index": 0,
                        "run_index": 0,
                        "text": "Robert J. Kuligowski",
                        "font_name": "Arial",
                        "font_size": 28.0,
                    },
                    {
                        "paragraph_index": 1,
                        "run_index": 0,
                        "text": "NOAA/NESDIS/Office of Research and Applications",
                        "font_name": "Arial",
                        "font_size": 20.0,
                    },
                ],
                "placeholder_type": "SUBTITLE",
            },
            {
                "name": "",
                "shape_id": 90,
                "shape_type": "AUTO_SHAPE",
                "measurement_unit": "emu",
                "height": 3464280,
                "width": 8229600,
                "left": 457200,
                "top": 3313080,
                "text": "Research Question: How will the increase in frequency of GOES imagery from 15 min to 5 min impact precipitation estimates?\nMethodology: Run the Hydro-Estimator (H-E) precipitation algorithm on 5-min GOES-11 data that were made available in support of the International H2O Project in June 2002 and compare the hourly totals for sampling rates of 30, 15, and 5 min with Stage IV fields.\nResults: A consistently positive, albeit small, positive impact—the H-E’s dry bias was reduced and correlation between the estimates and observations improved slightly.",
                "font_details": [
                    {
                        "paragraph_index": 0,
                        "run_index": 0,
                        "text": "Research Question:",
                        "font_name": "Arial",
                        "font_size": 20.0,
                    },
                    {
                        "paragraph_index": 0,
                        "run_index": 1,
                        "text": " How will the increase in frequency of GOES imagery from 15 min to 5 min impact precipitation estimates?",
                        "font_name": "Arial",
                        "font_size": 18.0,
                    },
                    {
                        "paragraph_index": 1,
                        "run_index": 0,
                        "text": "Methodology:",
                        "font_name": "Arial",
                        "font_size": 20.0,
                    },
                    {
                        "paragraph_index": 1,
                        "run_index": 1,
                        "text": " Run the Hydro-Estimator (H-E) precipitation algorithm on 5-min GOES-11 data that were made available in support of the International H2O Project in June 2002 and compare the hourly totals for sampling rates of 30, 15, and 5 min with Stage IV fields.",
                        "font_name": "Arial",
                        "font_size": 18.0,
                    },
                    {
                        "paragraph_index": 2,
                        "run_index": 0,
                        "text": "Results:",
                        "font_name": "Arial",
                        "font_size": 20.0,
                    },
                    {
                        "paragraph_index": 2,
                        "run_index": 1,
                        "text": " A consistently positive, albeit small, positive impact—the H-E’s dry bias was reduced and correlation between the estimates and observations improved slightly.",
                        "font_name": "Arial",
                        "font_size": 18.0,
                    },
                ],
            },
        ],
    }


@pytest.fixture
def slide_with_n_plus_one_shape():
    return {
        "slide_id": 264,
        "slide_name": "",
        "shapes": [
            {
                "name": "PlaceHolder 1",
                "shape_id": 88,
                "shape_type": "PLACEHOLDER",
                "measurement_unit": "emu",
                "height": 1371600,
                "width": 8229600,
                "left": 457200,
                "top": 457200,
                "text": "Projected Impacts of ABI Data on Satellite-Based Precipitation Estimation Part I: Enhanced Temporal Resolution",
                "font_details": [
                    {
                        "paragraph_index": 0,
                        "run_index": 0,
                        "text": "Projected Impacts of ABI Data on Satellite-Based Precipitation Estimation Part I: Enhanced Temporal Resolution",
                        "font_name": "Arial",
                        "font_size": 20.0,
                    }
                ],
                "placeholder_type": "TITLE",
            },
            {
                "name": "PlaceHolder 2",
                "shape_id": 89,
                "shape_type": "PLACEHOLDER",
                "measurement_unit": "emu",
                "height": 914400,
                "width": 9144000,
                "left": 0,
                "top": 2057400,
                "text": "Robert J. Kuligowski\nNOAA/NESDIS/Office of Research and Applications",
                "font_details": [
                    {
                        "paragraph_index": 0,
                        "run_index": 0,
                        "text": "Robert J. Kuligowski",
                        "font_name": "Arial",
                        "font_size": 28.0,
                    },
                    {
                        "paragraph_index": 1,
                        "run_index": 0,
                        "text": "NOAA/NESDIS/Office of Research and Applications",
                        "font_name": "Arial",
                        "font_size": 20.0,
                    },
                ],
                "placeholder_type": "SUBTITLE",
            },
            {
                "name": "",
                "shape_id": 90,
                "shape_type": "AUTO_SHAPE",
                "measurement_unit": "emu",
                "height": 3464280,
                "width": 8229600,
                "left": 457200,
                "top": 3313080,
                "text": "Research Question: How will the increase in frequency of GOES imagery from 15 min to 5 min impact precipitation estimates?\nMethodology: Run the Hydro-Estimator (H-E) precipitation algorithm on 5-min GOES-11 data that were made available in support of the International H2O Project in June 2002 and compare the hourly totals for sampling rates of 30, 15, and 5 min with Stage IV fields.\nResults: A consistently positive, albeit small, positive impact\u2014the H-E\u2019s dry bias was reduced and correlation between the estimates and observations improved slightly.",
                "font_details": [
                    {
                        "paragraph_index": 0,
                        "run_index": 0,
                        "text": "Research Question:",
                        "font_name": "Arial",
                        "font_size": 20.0,
                    },
                    {
                        "paragraph_index": 0,
                        "run_index": 1,
                        "text": " How will the increase in frequency of GOES imagery from 15 min to 5 min impact precipitation estimates?",
                        "font_name": "Arial",
                        "font_size": 18.0,
                    },
                    {
                        "paragraph_index": 1,
                        "run_index": 0,
                        "text": "Methodology:",
                        "font_name": "Arial",
                        "font_size": 20.0,
                    },
                    {
                        "paragraph_index": 1,
                        "run_index": 1,
                        "text": " Run the Hydro-Estimator (H-E) precipitation algorithm on 5-min GOES-11 data that were made available in support of the International H2O Project in June 2002 and compare the hourly totals for sampling rates of 30, 15, and 5 min with Stage IV fields.",
                        "font_name": "Arial",
                        "font_size": 18.0,
                    },
                    {
                        "paragraph_index": 2,
                        "run_index": 0,
                        "text": "Results:",
                        "font_name": "Arial",
                        "font_size": 20.0,
                    },
                    {
                        "paragraph_index": 2,
                        "run_index": 1,
                        "text": " A consistently positive, albeit small, positive impact\u2014the H-E\u2019s dry bias was reduced and correlation between the estimates and observations improved slightly.",
                        "font_name": "Arial",
                        "font_size": 18.0,
                    },
                ],
            },
        ],
    }


def test_successful_shape_addition(
    base_presentation_json, json_data_minus_one, shape_to_modify
):
    """Test case for successful shape addition."""
    api_calls = [
        "choose_slide(264)",
        "add_text_box(457200, 457200, 8229600, 1371600, 'Projected Impacts of ABI Data on Satellite-Based Precipitation Estimation Part I: Enhanced Temporal Resolution')",
    ]

    result = judge_answer_add_shape(
        api_calls=api_calls,
        shape_to_modify=shape_to_modify,
        json_data=json_data_minus_one,
        presentation_json=base_presentation_json,
    )

    assert result is True


def test_out_of_bounds_shape(
    base_presentation_json, json_data_minus_one, shape_to_modify
):
    """Test case for shape added out of bounds."""
    api_calls = [
        "choose_slide(264)",
        "add_text_box(457200000, 457200000, 8229600, 1371600, 'Projected Impacts of ABI Data on Satellite-Based Precipitation Estimation Part I: Enhanced Temporal Resolution')",
    ]

    result = judge_answer_add_shape(
        api_calls=api_calls,
        shape_to_modify=shape_to_modify,
        json_data=json_data_minus_one,
        presentation_json=base_presentation_json,
    )

    assert result is False


def test_overlapping_shape(
    base_presentation_json, json_data_minus_one, shape_to_modify
):
    """Test case for overlapping shapes."""
    api_calls = [
        "choose_slide(264)",
        "add_text_box(0, 0, 9144000, 9144000, 'Projected Impacts of ABI Data on Satellite-Based Precipitation Estimation Part I: Enhanced Temporal Resolution')",
    ]

    result = judge_answer_add_shape(
        api_calls=api_calls,
        shape_to_modify=shape_to_modify,
        json_data=json_data_minus_one,
        presentation_json=base_presentation_json,
    )

    assert result is False


def test_incorrect_shape_properties(
    base_presentation_json, json_data_minus_one, shape_to_modify
):
    """Test case for shape with incorrect properties."""
    api_calls = [
        "choose_slide(264)",
        "add_text_box(457200, 457200, 8229600, 1371600, 'Projected')",
    ]

    result = judge_answer_add_shape(
        api_calls=api_calls,
        shape_to_modify=shape_to_modify,
        json_data=json_data_minus_one,
        presentation_json=base_presentation_json,
    )

    assert result is False


def test_get_new_shape_success(slide_with_n_shape, slide_with_n_plus_one_shape):
    """Test successful identification of new shape."""
    new_shape = get_new_shape(
        slide_with_n_shape=slide_with_n_shape,
        slide_with_n_plus_one_shape=slide_with_n_plus_one_shape,
    )

    expected_shape = {
        "name": "PlaceHolder 1",
        "shape_id": 88,
        "shape_type": "PLACEHOLDER",
        "measurement_unit": "emu",
        "height": 1371600,
        "width": 8229600,
        "left": 457200,
        "top": 457200,
        "text": "Projected Impacts of ABI Data on Satellite-Based Precipitation Estimation Part I: Enhanced Temporal Resolution",
        "font_details": [
            {
                "paragraph_index": 0,
                "run_index": 0,
                "text": "Projected Impacts of ABI Data on Satellite-Based Precipitation Estimation Part I: Enhanced Temporal Resolution",
                "font_name": "Arial",
                "font_size": 20.0,
            }
        ],
        "placeholder_type": "TITLE",
    }

    assert new_shape == expected_shape


def test_get_new_shape_no_change(slide_with_n_shape):
    """Test when no new shape is added."""
    new_shape = get_new_shape(
        slide_with_n_shape=slide_with_n_shape,
        slide_with_n_plus_one_shape=slide_with_n_shape,
    )

    assert new_shape is None
