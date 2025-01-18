from typing import Any, Dict, List

import pandas as pd
from pathlib import Path
from ...shared.pptx_api.api_executor import api_executor
from ..utils import get_slide_from_presentation, has_out_of_bounds, has_overlap
from ...shared.utils import build_json_path
def judge_answer_refinement(
    df: pd.DataFrame,
    json_dir: Path = Path("data/json"),
) -> pd.DataFrame:
    """
    Judge the answers in the DataFrame and save results back to the same file.
    
    Args:
        df (pd.DataFrame): DataFrame with answers.
        json_path (str): Path to the JSON file.
        
    Returns:
        pd.DataFrame: DataFrame with judged answers.
    """
    # Process answers
    df["is_correct"] = df.apply(
        lambda row: judge_answer(
            api_calls=row["api_calls"],
            ground_truth=row["ground_truth"],
            json_path=build_json_path(file_hash=row["hash"], json_dir=json_dir),
        ),
        axis=1,
    )
    
    return df


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
    result_json = api_executor(api_calls, json_path=json_path, mode="json")

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