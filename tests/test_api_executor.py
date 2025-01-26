import json

import pytest

from src.shared.pptx_api.api_executor import api_executor


@pytest.fixture
def base_presentation_json():
    json_file = "tests/data/test_api_executor.json"
    with open(json_file, "r") as f:
        return json.load(f)


def test_api_executor(base_presentation_json):
    lines = [
        "choose_slide(263)",
        "add_text_box(456840, 2000000, 8458200, 3000000, '  Security\\n  Availability\\n  Integrity and Effectiveness\\n  Cost')",
        "set_font('Times New Roman')",
        "set_font_size(32)",
    ]
    result = api_executor(lines, json=base_presentation_json)
    # assert result is not None
    print(result)
