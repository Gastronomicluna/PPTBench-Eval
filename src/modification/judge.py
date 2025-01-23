import json
import traceback
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Union

import pandas as pd

from ..shared.parse_answer import parse_api_calls
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
    answers_df = csv_to_df(
        csv_path=csv_path,
        list_columns=["answer"],
    )

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
            "The input DataFrame must contain columns: task, ground_truth, file_hash, shape_to_modify, and answer."
        )

    # print(answers_df["ground_truth"].iloc[0])
    # Process answers
    def process_row(row: pd.Series) -> bool:
        try:
            # assert isinstance(row["answer"], list)
            answer = row["answer"]
            if answer is pd.NA or None:
                return False
            api_calls = parse_api_calls(row["answer"])
            # assert isinstance(api_calls, list)
            # print(f"API calls: {api_calls}")
            return judge_answer(
                task=row["task"],
                api_calls=api_calls,
                file_hash=row["file_hash"],
                ground_truth=json.loads(row["ground_truth"]),
                shape_to_modify=json.loads(row["shape_to_modify"]),
            )
        except Exception as e:
            print(f"Error processing row: {e}")
            print(traceback.format_exc())
            return False

    # print(answers_df)
    answers_df["is_correct"] = answers_df.apply(process_row, axis=1)

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
        json_dir=Path("dataset/json"),  # Changed from data/json to dataset/json
    )
    # assert api_calls is List[str]
    assert isinstance(api_calls, list)
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
    from ..shared.format_answers_api import format_answer_csv
    from ..shared.utils import download_kaggle_dataset

    download_kaggle_dataset(
        dataset_name="tyrionhuu/PPTBench-JSON",
        destination_dir="dataset",
        force_download=False,
        new_dir_name="json",
    )

    csv_path = Path("data/modification_results.csv")
    format_answer_csv(csv_path, overwrite=True)
    judge_answer_df(csv_path, overwrite=True)


if __name__ == "__main__":
    main()
