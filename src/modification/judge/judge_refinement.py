import logging
from typing import Any, Dict, List

import pandas as pd

from ...shared.pptx_api.api_executor import api_executor
from ..utils import get_slide_from_presentation
def judge_answer(
    api_calls: List[str],
    ground_truth: Dict[str, Any],
    json_path: str,
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
    result_json = api_executor(
        api_calls, 
        json_path=json_path, 
        mode="json"
    )

    # Get the slide
    slide = get_slide_from_presentation(
        slide_id=slide_id,
        presentation=result_json,
    )
    
    pass
