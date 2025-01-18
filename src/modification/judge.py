from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Union

import pandas as pd

from ..shared.utils import csv_to_df, df_to_csv
from .judge.judge_add_shape import judge_answer_add_shape
from .judge.judge_change_font import judge_answer_change_font
from .judge.judge_refinement import judge_answer_refinement
from .judge.judge_reposition import judge_answer_reposition
from .judge.judge_resize import judge_answer_resize


def judge_answer_df(
    csv_path: Union[Path, str],
    overwrite: bool = False,
) -> pd.DataFrame:
    """
    Judge the answers in the CSV file and save results back to the same file.

    Args:
        csv_path (Union[Path, str]): Path to CSV file for input and output.
        overwrite (bool): Whether to overwrite existing output file.

    Returns:
        pd.DataFrame: DataFrame with judged answers.
    """
    csv_path = Path(csv_path)
    answers_df = csv_to_df(csv_path)

    if answers_df is None:
        raise ValueError("The input DataFrame is empty.")

    if (
        "subcategory" not in answers_df.columns
        or "ground_truth" not in answers_df.columns
        or "answer" not in answers_df.columns
    ):
        raise ValueError(
            "The input DataFrame must contain 'subcategory', 'ground_truth', "
            "and 'answer' columns."
        )

    # Process answers
    answers_df["is_correct"] = answers_df.apply(
        lambda row: judge_answer(
            row["subcategory"], row["ground_truth"], row["answer"]
        ),
        axis=1,
    )

    # Save results
    if overwrite:
        df_to_csv(answers_df, csv_path)

    return answers_df


def judge_answer(
    task: Literal[
        "add_shape", "change_font", "reposition", "resize", "overlap", "out_of_bounds"
    ],
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
