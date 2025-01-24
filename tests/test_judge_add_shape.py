import json

import pytest

from src.modification.judge_lib.judge_add_shape import (
    get_new_shape,
    judge_answer_add_shape,
)


@pytest.fixture
def base_presentation_json():
    json_file = "tests/data/test_judge_add_shape.json"
    with open(json_file, "r") as f:
        return json.load(f)


@pytest.fixture
def ground_truth():
    return {"slide_width": 9144000, "slide_height": 6858000, "measurement_unit": "emu", "slide": {"slide_id": 302, "slide_name": "", "shapes": [{"name": "PlaceHolder 1", "shape_id": 235, "shape_type": "PLACEHOLDER", "measurement_unit": "emu", "height": 1143000, "width": 8229600, "left": 457200, "top": 274320, "text": "Protecci\\u00f3n contra ca\\u00eddas necesario", "font_details": [{"paragraph_index": 0, "run_index": 0, "text": "Protecci\\u00f3n contra ca\\u00eddas necesario", "font_name": "Times New Roman", "font_size": 40.0}], "placeholder_type": "TITLE"}, {"name": "", "shape_id": 236, "shape_type": "TEXT_BOX", "measurement_unit": "emu", "height": 4495680, "width": 5486400, "left": 457200, "top": 1600200, "text": "Peligros de hueco de elevador\\nTrabajadores son curiosos y miran adentro\\nUse barricadas (algo para bloquear las aperturas) en espacios abiertos para hoyos de elevadores\\nInspeccione frecuentemente los sistemas de barricada\\n", "font_details": [{"paragraph_index": 0, "run_index": 0, "text": "Peligros de hueco de elevador", "font_name": "Times New Roman", "font_size": 32.0}, {"paragraph_index": 1, "run_index": 0, "text": "Trabajadores son curiosos y miran adentro", "font_name": "Times New Roman", "font_size": 26.0}, {"paragraph_index": 2, "run_index": 0, "text": "Use barricadas (algo para bloquear las aperturas) en espacios abiertos para hoyos de elevadores", "font_name": "Times New Roman", "font_size": 26.0}, {"paragraph_index": 3, "run_index": 0, "text": "Inspeccione frecuentemente los sistemas de barricada", "font_name": "Times New Roman", "font_size": 26.0}]}, {"name": "Picture 2", "shape_id": 237, "shape_type": "PICTURE", "measurement_unit": "emu", "height": 3753000, "width": 2492640, "left": 6324480, "top": 1828800, "auto_shape_type": "RECTANGLE", "image_path": "dataset/extracted_images/HU34OGSYJRWDNIPBOH5QHHZ4KNJSRSLG/46/image_46_3.jpg"}, {"name": "Rectangle 4", "shape_id": 238, "shape_type": "AUTO_SHAPE", "measurement_unit": "emu", "height": 246600, "width": 1782720, "left": 6962040, "top": 5715000, "text": "http://farm2.static.flickr.com", "font_details": [{"paragraph_index": 0, "run_index": 0, "text": "http://farm2.static.flickr.com", "font_name": "Tahoma", "font_size": 10.0}]}, {"name": "Slide Number Placeholder 5", "shape_id": 239, "shape_type": "AUTO_SHAPE", "measurement_unit": "emu", "height": 365040, "width": 2133720, "left": 6553080, "top": 6356520, "text": "<number>", "font_details": []}]}}


@pytest.fixture
def shape_to_modify():
    return {"name": "Picture 2", "shape_id": 237, "shape_type": "PICTURE", "measurement_unit": "emu", "height": 3753000, "width": 2492640, "left": 6324480, "top": 1828800, "auto_shape_type": "RECTANGLE", "image_path": "dataset/extracted_images/HU34OGSYJRWDNIPBOH5QHHZ4KNJSRSLG/46/image_46_3.jpg"}



@pytest.fixture
def json_data():
    return {'slide_width': 9144000, 'slide_height': 6858000, 'measurement_unit': 'emu', 'slide': {'slide_id': 302, 'slide_name': '', 'shapes': [{'name': 'PlaceHolder 1', 'shape_id': 235, 'shape_type': 'PLACEHOLDER', 'measurement_unit': 'emu', 'height': 1143000, 'width': 8229600, 'left': 457200, 'top': 274320, 'text': 'Protección contra caídas necesario', 'font_details': [{'paragraph_index': 0, 'run_index': 0, 'text': 'Protección contra caídas necesario', 'font_name': 'Times New Roman', 'font_size': 40.0}], 'placeholder_type': 'TITLE'}, {'name': '', 'shape_id': 236, 'shape_type': 'TEXT_BOX', 'measurement_unit': 'emu', 'height': 4495680, 'width': 5486400, 'left': 457200, 'top': 1600200, 'text': 'Peligros de hueco de elevador\\nTrabajadores son curiosos y miran adentro\\nUse barricadas (algo para bloquear las aperturas) en espacios abiertos para hoyos de elevadores\\nInspeccione frecuentemente los sistemas de barricada\\n', 'font_details': [{'paragraph_index': 0, 'run_index': 0, 'text': 'Peligros de hueco de elevador', 'font_name': 'Times New Roman', 'font_size': 32.0}, {'paragraph_index': 1, 'run_index': 0, 'text': 'Trabajadores son curiosos y miran adentro', 'font_name': 'Times New Roman', 'font_size': 26.0}, {'paragraph_index': 2, 'run_index': 0, 'text': 'Use barricadas (algo para bloquear las aperturas) en espacios abiertos para hoyos de elevadores', 'font_name': 'Times New Roman', 'font_size': 26.0}, {'paragraph_index': 3, 'run_index': 0, 'text': 'Inspeccione frecuentemente los sistemas de barricada', 'font_name': 'Times New Roman', 'font_size': 26.0}]}, {'name': 'Rectangle 4', 'shape_id': 238, 'shape_type': 'AUTO_SHAPE', 'measurement_unit': 'emu', 'height': 246600, 'width': 1782720, 'left': 6962040, 'top': 5715000, 'text': 'http://farm2.static.flickr.com', 'font_details': [{'paragraph_index': 0, 'run_index': 0, 'text': 'http://farm2.static.flickr.com', 'font_name': 'Tahoma', 'font_size': 10.0}]}, {'name': 'Slide Number Placeholder 5', 'shape_id': 239, 'shape_type': 'AUTO_SHAPE', 'measurement_unit': 'emu', 'height': 365040, 'width': 2133720, 'left': 6553080, 'top': 6356520, 'text': '<number>', 'font_details': []}]}}


def test_successful_shape_addition(
    base_presentation_json, ground_truth, shape_to_modify, json_data
):
    """Test case for successful shape addition."""
    api_calls = [
        "choose_slide(302)",
        "add_picture(6324480, 1828800, 2492640, 3753000, 'dataset/extracted_images/HU34OGSYJRWDNIPBOH5QHHZ4KNJSRSLG/46/image_46_3.jpg')",
    ]

    result = judge_answer_add_shape(
        api_calls=api_calls,
        shape_to_modify=shape_to_modify,
        json_data=json_data,
        presentation_json=base_presentation_json,
    )

    assert result is True