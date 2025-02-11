import json

import pytest

from src.shared.pptx_api.api_executor import api_executor


@pytest.fixture
def base_presentation_json():
    json_file = "tests/data/test_api_executor.json"
    with open(json_file, "r") as f:
        return json.load(f)


def test_api_executor(base_presentation_json):
    lines = ['choose_slide(257)', 'choose_shape(19)', 'set_top(0)']
    result = api_executor(lines, json=base_presentation_json, mode="json")
    assert result[0] is True
    # print(result)
