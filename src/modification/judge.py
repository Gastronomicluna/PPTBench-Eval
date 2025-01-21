import json
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Union

import pandas as pd

from ..shared.utils import build_json_path, csv_to_df, df_to_csv
from .judge_lib.judge_add_shape import judge_answer_add_shape
from .judge_lib.judge_change_font import judge_answer_change_font
from .judge_lib.judge_refinement import judge_answer_refinement
from .judge_lib.judge_reposition import judge_answer_reposition
from .judge_lib.judge_resize import judge_answer_resize


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
        "task" not in answers_df.columns
        or "ground_truth" not in answers_df.columns
        or "file_hash" not in answers_df.columns
        or "shape_to_modify" not in answers_df.columns
        or "answer" not in answers_df.columns
    ):
        raise ValueError(
            "The input DataFrame must contain 'subcategory', 'ground_truth', "
            "and 'answer' columns."
        )

    # Process answers
    answers_df["is_correct"] = answers_df.apply(
        lambda row: judge_answer(
            task=row["task"],
            api_calls=row["answer"],
            file_hash=row["file_hash"],
            ground_truth=row["ground_truth"],
            shape_to_modify=row["shape_to_modify"],
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
    file_hash: str,
    ground_truth: Dict[str, Any],
    shape_to_modify: Optional[Dict[str, Any]] = None,
) -> bool:
    """
    Judge the answer based on the task type.

    Args:
        task (str): The type of task.
        api_calls (List[str]): The API calls made by the model.
        ground_truth (Dict[str, Any]): The ground truth JSON data.
        presentation_json (Dict[str, Any]): The JSON data, the original
        json_path (str): The path to the JSON data.

    Returns:
        bool: Whether the answer is correct.
    """
    json_path = build_json_path(
        file_hash=file_hash,
        json_dir=Path("data/json"),
    )

    presentation_json = json.load(open(json_path, "r"))

    if task == "add_shape":
        return judge_answer_add_shape(
            api_calls=api_calls,
            ground_truth=ground_truth,
            presentation_json=presentation_json,
        )
    elif task == "change_font":
        return judge_answer_change_font(
            api_calls=api_calls,
            shape_to_modify=shape_to_modify,
            ground_truth=ground_truth,
            presentation_json=presentation_json,
        )
    elif task == "reposition":
        return judge_answer_reposition(
            api_calls=api_calls,
            shape_to_modify=shape_to_modify,
            ground_truth=ground_truth,
            presentation_json=presentation_json,
        )
    elif task == "resize":
        return judge_answer_resize(
            api_calls=api_calls,
            shape_to_modify=shape_to_modify,
            ground_truth=ground_truth,
            presentation_json=presentation_json,
        )
    elif task == "overlap" or task == "out_of_bounds":
        return judge_answer_refinement(
            api_calls=api_calls,
            ground_truth=ground_truth,
            presentation_json=presentation_json,
        )
    else:
        raise ValueError(f"Unknown task type: {task}")


def main():
    csv_path = "data/modification_results.csv"
    judge_answer_df(csv_path, overwrite=True)
    
if __name__ == "__main__":
    main()