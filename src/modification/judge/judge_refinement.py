from typing import Any, Dict, List

from ...shared.pptx_api.api_executor import api_executor
from ..utils import get_slide_from_presentation, has_out_of_bounds, has_overlap


def judge_answer_refinement(
    api_calls: List[str],
    ground_truth: Dict[str, Any],
    json_data: Dict[str, Any],
) -> bool:
    """
    Judge the answer based on the API calls and ground truth.

    Args:
        api_calls (List[str]): The API calls made by the model.
        json_path (str): The path to the JSON data.

    Returns:
        bool: Whether the answer is correct.
    """
    # Get slide ID from the ground truth
    slide_id = ground_truth.get("slide", {}).get("slide_id")

    # Execute the API calls
    result_json = api_executor(lines=api_calls, json=json_data, mode="json")

    # Get the slide
    slide = get_slide_from_presentation(
        slide_id=slide_id,
        presentation=result_json,
    )

    # Check if the slide has overlapping shapes
    has_overlap_result = has_overlap(slide)

    # Check if the slide has out of bounds shapes
    has_out_of_bounds_result = has_out_of_bounds(slide)

    return not has_overlap_result and not has_out_of_bounds_result
