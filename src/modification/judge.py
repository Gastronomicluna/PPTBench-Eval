import json
import traceback
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Tuple, Union

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
        or "json_data" not in answers_df.columns
        or "answer" not in answers_df.columns
    ):
        raise ValueError(
            "The input DataFrame must contain columns: task, ground_truth, file_hash, shape_to_modify, and answer."
        )

    # print(answers_df["ground_truth"].iloc[0])
    # Process answers
    def process_row(row: pd.Series) -> Tuple[bool, str]:
        """
        Process the row and judge the answer.

        Args:
            row (pd.Series): The row to process.

        Returns:
            Tuple[bool, str]: Whether the answer is correct and reason if incorrect.
        """
        try:
            # assert isinstance(row["answer"], list)
            answer = row["answer"]
            if answer is pd.NA or None:
                return False
            if not isinstance(answer, List):
                api_calls = parse_api_calls(row["answer"])
            else:
                api_calls = answer
            # assert isinstance(api_calls, list)
            # print("task: ", row["task"])
            # print("api_calls: ", api_calls)
            # print("file_hash: ", row["file_hash"])
            # print("ground_truth: ", json.loads(row["ground_truth"]))
            # print("shape_to_modify: ", json.loads(row["shape_to_modify"]))
            # print("json_data: ", json.loads(row["json_data"]))
            
            return judge_answer(
                task=row["task"],
                api_calls=api_calls,
                file_hash=row["file_hash"],
                ground_truth=json.loads(row["ground_truth"]),
                shape_to_modify=json.loads(row["shape_to_modify"]),
                json_data=json.loads(row["json_data"]),
            )
        except Exception as e:
            print(f"Error processing row: {e}")
            print(traceback.format_exc())
            return False

    # Apply the process to each row
    results = answers_df.apply(process_row, axis=1, result_type="expand")
    answers_df["is_correct"] = results[0]
    answers_df["reason"] = results[1]

    # Save results
    if overwrite:
        df_to_csv(answers_df, csv_path)

    return answers_df


def judge_answer(
    task: Literal[
        "add_shape", "change_font", "reposition", "resize", "overlap", "out_of_bounds"
    ],
    api_calls: Optional[List[str]],
    file_hash: str,
    json_data: Dict[str, Any],
    ground_truth: Dict[str, Any],
    shape_to_modify: Optional[Dict[str, Any]] = None,
) -> Tuple[bool, str]:
    """
    Judge the answer based on the task type.

    Args:
        task (str): The type of task.
        api_calls (List[str]): The API calls made by the model.
        ground_truth (Dict[str, Any]): The ground truth JSON data.
        presentation_json (Dict[str, Any]): The JSON data, the original
        json_path (str): The path to the JSON data.

    Returns:
        Tuple[bool, str]: Whether the answer is correct and reason if incorrect.
    """
    json_path = build_json_path(
        file_hash=file_hash,
        json_dir=Path("dataset/json"),  # Changed from data/json to dataset/json
    )
    if api_calls is None:
        return False, "No API calls found"
    presentation_json = json.load(open(json_path, "r"))
    if task == "add_shape":
        return judge_answer_add_shape(
            api_calls=api_calls,
            shape_to_modify=shape_to_modify,
            json_data=json_data,
            presentation_json=presentation_json,
        )
    elif task == "change_font":
        return judge_answer_change_font(
            api_calls=api_calls,
            ground_truth=ground_truth,
            presentation_json=presentation_json,
        )
    elif task == "reposition_shape":
        return judge_answer_reposition(
            api_calls=api_calls,
            shape_to_modify=shape_to_modify,
            json_data=json_data,
            presentation_json=presentation_json,
        )
    elif task == "resize_shape":
        return judge_answer_resize(
            api_calls=api_calls,
            shape_to_modify=shape_to_modify,
            json_data=json_data,
            presentation_json=presentation_json,
        )
    elif task == "overlap" or task == "out_of_bounds":
        return judge_answer_refinement(
            api_calls=api_calls,
            json_data=json_data,
            presentation_json=presentation_json,
        )
    else:
        raise ValueError(f"Unknown task type: {task}")


def main():
    judge_answer(
        task="reposition_shape",
        api_calls=['choose_slide(257)', 'choose_shape(19)', 'set_top(0)'],
        file_hash="LAZMY7ZW7GNF43JIMDAHTBRZWW4S5TIV",
        json_data={"slide_width": 9144000, "slide_height": 6858000, "measurement_unit": "emu", "slide": {"slide_id": 257, "slide_name": "", "shapes": [{"name": "PlaceHolder 1", "shape_id": 19, "shape_type": "PLACEHOLDER", "measurement_unit": "emu", "height": 603360, "width": 7864560, "left": 903240, "top": 217440, "text": "Agenda", "font_details": [{"paragraph_index": 0, "run_index": 0, "text": "Agenda", "font_name": "Arial", "font_size": 24.0}], "placeholder_type": "TITLE"}, {"name": "PlaceHolder 2", "shape_id": 20, "shape_type": "PLACEHOLDER", "measurement_unit": "emu", "height": 5216400, "width": 8458200, "left": 431280, "top": 1216080, "text": "Mission Overview\\nNetwork Test\\nInterim Support Instructions (ISI)\\nC-band Tracking\\nFDF Support\\nFDF Staffing\\nNIC Staffing\\nSN Support\\nWSC TOA Staffing\\nProposed Activities/Open Discussions", "font_details": [{"paragraph_index": 0, "run_index": 0, "text": "Mission Overview", "font_name": "Arial", "font_size": 18.0}, {"paragraph_index": 1, "run_index": 0, "text": "Network Test", "font_name": "Arial", "font_size": 18.0}, {"paragraph_index": 2, "run_index": 0, "text": "Interim Support Instructions (ISI)", "font_name": "Arial", "font_size": 18.0}, {"paragraph_index": 3, "run_index": 0, "text": "C-band Tracking", "font_name": "Arial", "font_size": 18.0}, {"paragraph_index": 4, "run_index": 0, "text": "FDF Support", "font_name": "Arial", "font_size": 18.0}, {"paragraph_index": 5, "run_index": 0, "text": "FDF Staffing", "font_name": "Arial", "font_size": 18.0}, {"paragraph_index": 6, "run_index": 0, "text": "NIC Staffing", "font_name": "Arial", "font_size": 18.0}, {"paragraph_index": 7, "run_index": 0, "text": "SN Support", "font_name": "Arial", "font_size": 18.0}, {"paragraph_index": 8, "run_index": 0, "text": "WSC TOA Staffing", "font_name": "Arial", "font_size": 18.0}, {"paragraph_index": 9, "run_index": 0, "text": "Proposed Activities/Open Discussions", "font_name": "Arial", "font_size": 18.0}], "placeholder_type": "OBJECT"}]}},
        ground_truth={"slide_width": 9144000, "slide_height": 6858000, "measurement_unit": "emu", "slide": {"slide_id": 257, "slide_name": "", "shapes": [{"name": "PlaceHolder 1", "shape_id": 19, "shape_type": "PLACEHOLDER", "measurement_unit": "emu", "height": 603360, "width": 7864560, "left": 903240, "top": 0, "text": "Agenda", "font_details": [{"paragraph_index": 0, "run_index": 0, "text": "Agenda", "font_name": "Arial", "font_size": 24.0}], "placeholder_type": "TITLE"}, {"name": "PlaceHolder 2", "shape_id": 20, "shape_type": "PLACEHOLDER", "measurement_unit": "emu", "height": 5216400, "width": 8458200, "left": 431280, "top": 1216080, "text": "Mission Overview\\nNetwork Test\\nInterim Support Instructions (ISI)\\nC-band Tracking\\nFDF Support\\nFDF Staffing\\nNIC Staffing\\nSN Support\\nWSC TOA Staffing\\nProposed Activities/Open Discussions", "font_details": [{"paragraph_index": 0, "run_index": 0, "text": "Mission Overview", "font_name": "Arial", "font_size": 18.0}, {"paragraph_index": 1, "run_index": 0, "text": "Network Test", "font_name": "Arial", "font_size": 18.0}, {"paragraph_index": 2, "run_index": 0, "text": "Interim Support Instructions (ISI)", "font_name": "Arial", "font_size": 18.0}, {"paragraph_index": 3, "run_index": 0, "text": "C-band Tracking", "font_name": "Arial", "font_size": 18.0}, {"paragraph_index": 4, "run_index": 0, "text": "FDF Support", "font_name": "Arial", "font_size": 18.0}, {"paragraph_index": 5, "run_index": 0, "text": "FDF Staffing", "font_name": "Arial", "font_size": 18.0}, {"paragraph_index": 6, "run_index": 0, "text": "NIC Staffing", "font_name": "Arial", "font_size": 18.0}, {"paragraph_index": 7, "run_index": 0, "text": "SN Support", "font_name": "Arial", "font_size": 18.0}, {"paragraph_index": 8, "run_index": 0, "text": "WSC TOA Staffing", "font_name": "Arial", "font_size": 18.0}, {"paragraph_index": 9, "run_index": 0, "text": "Proposed Activities/Open Discussions", "font_name": "Arial", "font_size": 18.0}], "placeholder_type": "OBJECT"}]}},
        shape_to_modify={"name": "PlaceHolder 1", "shape_id": 19, "shape_type": "PLACEHOLDER", "measurement_unit": "emu", "height": 603360, "width": 7864560, "left": 903240, "top": 217440, "text": "Agenda", "font_details": [{"paragraph_index": 0, "run_index": 0, "text": "Agenda", "font_name": "Arial", "font_size": 24.0}], "placeholder_type": "TITLE"}            
    )
    # judge_answer_df(
    #     csv_path="data/modification_results/gpt-4o-2024-11-20.csv",
    #     overwrite=True,
    # )

if __name__ == "__main__":
    main()
