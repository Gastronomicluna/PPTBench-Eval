import json

import pytest

from src.shared.pptx_api.api_executor import api_executor

@pytest.fixture
def base_presentation_json():
    json_file = "tests/data/test_api_executor.json"
    with open(json_file, "r") as f:
        return json.load(f)
    
    
def test_api_executor(base_presentation_json):
    lines = ['choose_slide(263)', "add_text_box(334800, 1000000, 8477280, 800000, 'Objectives')", "set_font('Arial')", 'set_font_size(72)']
    result = api_executor(lines, json=base_presentation_json)
    # assert result is not None
    print(result)