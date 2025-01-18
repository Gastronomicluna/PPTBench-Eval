import os
import tempfile
from typing import Generator

import pytest
from PIL import Image
from pptx import Presentation

from src.shared.pptx_api.api_executor_json import (
    set_json,
    choose_shape,
    choose_slide,
    set_height,
    set_left,
    set_top,
    set_width,
    api_executor_json,
)
from src.shared.pptx_api.utils import get_shape_ids, get_slide_ids


@pytest.fixture
def sample_json() -> str:
    """Load a sample JSON file.

    Returns:
        str: Path to the sample JSON file.
    """
    return {
        "slide_width": 9144000,
        "slide_height": 6858000,
        "slides": [
            {
                "slide_id": 261,
                "slide_name": "",
                "shapes": [
                    {
                        "name": "PlaceHolder 1",
                        "shape_id": 23,
                        "shape_type": "PLACEHOLDER",
                        "measurement_unit": "emu",
                        "height": 1143000,
                        "width": 8229600,
                        "left": 457200,
                        "top": 274320,
                        "text": "Science CRT-Alternate",
                        "font_details": [
                            {
                                "paragraph_index": 0,
                                "run_index": 0,
                                "text": "Science CRT-Alternate",
                                "font_name": "Georgia",
                                "font_size": 44.0,
                            }
                        ],
                        "placeholder_type": "TITLE",
                    },
                    {
                        "name": "PlaceHolder 2",
                        "shape_id": 24,
                        "shape_type": "PLACEHOLDER",
                        "measurement_unit": "emu",
                        "height": 4525920,
                        "width": 8229600,
                        "left": 457200,
                        "top": 1600200,
                        "text": "Summer and Fall 2006\nDevelopment of \nDraft expanded benchmarks aligned with Montana standards\nDraft performance/achievement descriptors\nWinter \u2013 Summer 2007\nDevelopment of tasklets and items\nFall 2007\nBeta test of items\nBias and content reviews\nFinal alignment and adjustments as needed\nSpring 2008\nFirst administration",
                        "font_details": [
                            {
                                "paragraph_index": 0,
                                "run_index": 0,
                                "text": "Summer and Fall 2006",
                                "font_name": "Arial",
                                "font_size": 28.0,
                            },
                            {
                                "paragraph_index": 1,
                                "run_index": 0,
                                "text": "Development of ",
                                "font_name": "Arial",
                                "font_size": 24.0,
                            },
                            {
                                "paragraph_index": 2,
                                "run_index": 0,
                                "text": "Draft expanded benchmarks aligned with Montana standards",
                                "font_name": "Arial",
                                "font_size": 20.0,
                            },
                            {
                                "paragraph_index": 3,
                                "run_index": 0,
                                "text": "Draft performance/achievement descriptors",
                                "font_name": "Arial",
                                "font_size": 20.0,
                            },
                            {
                                "paragraph_index": 4,
                                "run_index": 0,
                                "text": "Winter \u2013 Summer 2007",
                                "font_name": "Arial",
                                "font_size": 28.0,
                            },
                            {
                                "paragraph_index": 5,
                                "run_index": 0,
                                "text": "Development of tasklets and items",
                                "font_name": "Arial",
                                "font_size": 24.0,
                            },
                            {
                                "paragraph_index": 6,
                                "run_index": 0,
                                "text": "Fall 2007",
                                "font_name": "Arial",
                                "font_size": 28.0,
                            },
                            {
                                "paragraph_index": 7,
                                "run_index": 0,
                                "text": "Beta test of items",
                                "font_name": "Arial",
                                "font_size": 24.0,
                            },
                            {
                                "paragraph_index": 8,
                                "run_index": 0,
                                "text": "Bias and content reviews",
                                "font_name": "Arial",
                                "font_size": 24.0,
                            },
                            {
                                "paragraph_index": 9,
                                "run_index": 0,
                                "text": "Final alignment and adjustments as needed",
                                "font_name": "Arial",
                                "font_size": 24.0,
                            },
                            {
                                "paragraph_index": 10,
                                "run_index": 0,
                                "text": "Spring 2008",
                                "font_name": "Arial",
                                "font_size": 28.0,
                            },
                            {
                                "paragraph_index": 11,
                                "run_index": 0,
                                "text": "First administration",
                                "font_name": "Arial",
                                "font_size": 24.0,
                            },
                        ],
                        "placeholder_type": "OBJECT",
                    },
                    {
                        "name": "PlaceHolder 3",
                        "shape_id": 4,
                        "shape_type": "PLACEHOLDER",
                        "measurement_unit": "emu",
                        "height": 476280,
                        "width": 1600200,
                        "left": 7086240,
                        "top": 6244920,
                        "text": "6",
                        "font_details": [],
                        "placeholder_type": "SLIDE_NUMBER",
                    },
                ],
            },
            {
                "slide_id": 262,
                "slide_name": "",
                "shapes": [
                    {
                        "name": "PlaceHolder 1",
                        "shape_id": 25,
                        "shape_type": "PLACEHOLDER",
                        "measurement_unit": "emu",
                        "height": 1143000,
                        "width": 8229600,
                        "left": 457200,
                        "top": 274320,
                        "text": "OPI Assessment \u000bContact Information",
                        "font_details": [
                            {
                                "paragraph_index": 0,
                                "run_index": 0,
                                "text": "OPI Assessment ",
                                "font_name": "Georgia",
                                "font_size": 40.0,
                            },
                            {
                                "paragraph_index": 0,
                                "run_index": 1,
                                "text": "Contact Information",
                                "font_name": "Georgia",
                                "font_size": 40.0,
                            },
                        ],
                        "placeholder_type": "TITLE",
                    },
                    {
                        "name": "PlaceHolder 2",
                        "shape_id": 26,
                        "shape_type": "PLACEHOLDER",
                        "measurement_unit": "emu",
                        "height": 4530600,
                        "width": 8229600,
                        "left": 457200,
                        "top": 1371240,
                        "text": "Karen Crogan\nAssessment Assistant\n406-444-4431  OR kcrogan@mt.gov \nKaren Richem\nAssessment Specialist\n406-444-0748 OR  krichem@mt.gov\nJudy Snow\nState Assessment Director\n406-444-3656 OR jsnow@mt.gov \n",
                        "font_details": [
                            {
                                "paragraph_index": 0,
                                "run_index": 0,
                                "text": "Karen Crogan",
                                "font_name": "Georgia",
                                "font_size": 32.0,
                            },
                            {
                                "paragraph_index": 1,
                                "run_index": 0,
                                "text": "Assessment Assistant",
                                "font_name": "Georgia",
                                "font_size": 28.0,
                            },
                            {
                                "paragraph_index": 2,
                                "run_index": 0,
                                "text": "406-444-4431  OR ",
                                "font_name": "Georgia",
                                "font_size": 28.0,
                            },
                            {
                                "paragraph_index": 2,
                                "run_index": 1,
                                "text": "kcrogan@mt.gov",
                                "font_name": "Georgia",
                                "font_size": 28.0,
                            },
                            {
                                "paragraph_index": 2,
                                "run_index": 2,
                                "text": " ",
                                "font_name": "Georgia",
                                "font_size": 28.0,
                            },
                            {
                                "paragraph_index": 3,
                                "run_index": 0,
                                "text": "Karen Richem",
                                "font_name": "Georgia",
                                "font_size": 32.0,
                            },
                            {
                                "paragraph_index": 4,
                                "run_index": 0,
                                "text": "Assessment Specialist",
                                "font_name": "Georgia",
                                "font_size": 28.0,
                            },
                            {
                                "paragraph_index": 5,
                                "run_index": 0,
                                "text": "406-444-0748 OR  ",
                                "font_name": "Georgia",
                                "font_size": 28.0,
                            },
                            {
                                "paragraph_index": 5,
                                "run_index": 1,
                                "text": "krichem@mt.gov",
                                "font_name": "Georgia",
                                "font_size": 28.0,
                            },
                            {
                                "paragraph_index": 6,
                                "run_index": 0,
                                "text": "Judy Snow",
                                "font_name": "Georgia",
                                "font_size": 32.0,
                            },
                            {
                                "paragraph_index": 7,
                                "run_index": 0,
                                "text": "State Assessment Director",
                                "font_name": "Georgia",
                                "font_size": 28.0,
                            },
                            {
                                "paragraph_index": 8,
                                "run_index": 0,
                                "text": "406-444-3656 OR ",
                                "font_name": "Georgia",
                                "font_size": 28.0,
                            },
                            {
                                "paragraph_index": 8,
                                "run_index": 1,
                                "text": "jsnow@mt.gov",
                                "font_name": "Georgia",
                                "font_size": 28.0,
                            },
                            {
                                "paragraph_index": 8,
                                "run_index": 2,
                                "text": " ",
                                "font_name": "Georgia",
                                "font_size": 28.0,
                            },
                        ],
                        "placeholder_type": "OBJECT",
                    },
                    {
                        "name": "",
                        "shape_id": 27,
                        "shape_type": "PICTURE",
                        "measurement_unit": "emu",
                        "height": 1600200,
                        "width": 1417680,
                        "left": 7238880,
                        "top": 1447920,
                        "auto_shape_type": "RECTANGLE",
                    },
                    {
                        "name": "PlaceHolder 3",
                        "shape_id": 4,
                        "shape_type": "PLACEHOLDER",
                        "measurement_unit": "emu",
                        "height": 476280,
                        "width": 1600200,
                        "left": 7086240,
                        "top": 6244920,
                        "text": "7",
                        "font_details": [],
                        "placeholder_type": "SLIDE_NUMBER",
                    },
                ],
            },
        ],
    }

def test_set_height(sample_json: str) -> None:
    pass