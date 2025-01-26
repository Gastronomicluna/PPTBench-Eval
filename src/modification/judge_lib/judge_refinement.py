from typing import Any, Dict, List, Tuple

from ...shared.pptx_api.api_executor import api_executor
from ..utils import (
    get_slide_from_presentation,
    has_out_of_bounds,
    has_overlap,
    produce_modified_presentation_json,
)


def judge_answer_refinement(
    api_calls: List[str],
    json_data: Dict[str, Any],
    presentation_json: Dict[str, Any],
) -> Tuple[bool, str]:
    """
    Judge the answer based on the API calls and ground truth.

    Args:
        api_calls (List[str]): The API calls made by the model.
        json_path (str): The path to the JSON data.

    Returns:
        Tuple[bool, str]: Whether the answer is correct and reason if incorrect.
    """
    slide_height = json_data["slide_height"]
    slide_width = json_data["slide_width"]

    # Get the slide JSON data
    slide_json = json_data.get("slide", {})
    if slide_json is None:
        raise ValueError("The slide JSON data is not found in the JSON data.")

    # Get slide ID from the ground truth
    slide_id = slide_json["slide_id"]
    if slide_id is None:
        raise ValueError("The slide ID is not found in the shape to modify.")

    # Execute the API calls
    produced_presentation_json = produce_modified_presentation_json(
        presentation=presentation_json,
        slide_id=slide_id,
        slide_json=slide_json,
    )

    try:
        llm_modified_presentation = api_executor(
            lines=api_calls, 
            json=produced_presentation_json, 
            mode="json"
        )
    except Exception as e:
        return False, f"Error executing API calls: {str(e)}"

    # Get the llm modified slide
    llm_modified_slide = get_slide_from_presentation(
        slide_id=slide_id,
        presentation=llm_modified_presentation,
    )

    # Check if the slide has overlapping shapes
    has_overlap_result = has_overlap(llm_modified_slide)
    if has_overlap_result:
        return False, "Shapes overlap in the modified slide"

    # Check if the slide has out of bounds shapes
    has_out_of_bounds_result = has_out_of_bounds(
        slide_json=llm_modified_slide,
        slide_height=slide_height,
        slide_width=slide_width,
    )
    if has_out_of_bounds_result:
        return False, "Shapes are out of bounds in the modified slide"

    return True, "Success"
