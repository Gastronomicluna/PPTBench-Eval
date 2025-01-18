from .judge.judge_add_shape import judge_answer_add_shape
from .judge.judge_change_font import judge_answer_change_font
from .judge.judge_refinement import judge_answer_refinement
from .judge.judge_reposition import judge_answer_reposition
from .judge.judge_resize import judge_answer_resize
from typing import Dict, Optional, Literal, List, Any

def judge_answer(
    task: Literal["add_shape", "change_font", "reposition", "resize", "overlap", "out_of_bounds"],
    api_calls: List[str],
    ground_truth: Dict[str, Any],
    json_data: Dict[str, Any] = None,
    shape_to_modify: Optional[Dict[str, Any]] = None,
) -> bool:
    """
    Judge the answer based on the task type.

    Args:
        task (str): The type of task.
        api_calls (List[str]): The API calls made by the model.
        ground_truth (Dict[str, Any]): The ground truth JSON data.
        json_data (Dict[str, Any]): The JSON data, the original
        json_path (str): The path to the JSON data.

    Returns:
        bool: Whether the answer is correct.
    """
    if task == "add_shape":
        return judge_answer_add_shape(
            api_calls=api_calls,
            ground_truth=ground_truth,
            json_data=json_data,
        )
    elif task == "change_font":
        return judge_answer_change_font(
            api_calls=api_calls,
            shape_to_modify=shape_to_modify,
            ground_truth=ground_truth,
            json_data=json_data,
        )
    elif task == "reposition":
        return judge_answer_reposition(
            api_calls=api_calls,
            shape_to_modify=shape_to_modify,
            ground_truth=ground_truth,
            json_data=json_data,
        )
    elif task == "resize":
        return judge_answer_resize(
            api_calls=api_calls,
            shape_to_modify=shape_to_modify,
            ground_truth=ground_truth,
            json_data=json_data,
        )
    elif task == "overlap" or task == "out_of_bounds":
        return judge_answer_refinement(
            api_calls=api_calls,
            ground_truth=ground_truth,
            json_data=json_data,
        )
    else:
        raise ValueError(f"Unknown task type: {task}")