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

# Add this near the top of the file, after imports
BASE_DIR = Path(__file__).parent.parent.parent


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
            # Skip if error cell is not empty
            if "error" in row and pd.notna(row["error"]):
                return False, "Skipped due to existing error"
                
            answer = row["answer"]
            if answer is pd.NA or None:
                return False
            if not isinstance(answer, List):
                api_calls = parse_api_calls(row["answer"])
            else:
                api_calls = answer
            # assert row["task"] == "reposition_shape"
            # assert row["file_hash"] == "LAZMY7ZW7GNF43JIMDAHTBRZWW4S5TIV"
            # assert api_calls == ['choose_slide(257)', 'choose_shape(19)', 'set_top(0)']
            task = row["task"]
            file_hash = row["file_hash"]
            ground_truth = json.loads(row["ground_truth"])
            shape_to_modify = json.loads(row["shape_to_modify"])
            json_data = json.loads(row["json_data"])
            # print("task: ", task)
            # print("ground_truth: ", ground_truth)
            # print("shape_to_modify: ", shape_to_modify)
            # print("json_data: ", json_data)
            # assert isinstance(ground_truth, dict)
            # assert isinstance(shape_to_modify, dict)
            # assert isinstance(json_data, dict)
            return judge_answer(
                task=task,
                api_calls=api_calls,
                file_hash=file_hash,
                json_data=json_data,
                ground_truth=ground_truth,
                shape_to_modify=shape_to_modify,
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
        "add_shape",
        "change_font",
        "reposition_shape",
        "resize_shape",
        "overlap",
        "out_of_bounds",
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
        json_dir=BASE_DIR / "dataset" / "json",  # Use absolute path with BASE_DIR
    )
    if not json_path.exists():
        raise FileNotFoundError(f"JSON file not found at {json_path}")
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
        # print("api_calls: ", api_calls)
        # print("shape_to_modify: ", shape_to_modify)
        # print("json_data: ", json_data)
        # print("presentation_json: ", presentation_json)
        return judge_answer_reposition(
            api_calls=api_calls,
            shape_to_modify=shape_to_modify,
            json_data=json_data,
            ground_truth=ground_truth,
            presentation_json=presentation_json,
        )
    elif task == "resize_shape":
        return judge_answer_resize(
            api_calls=api_calls,
            shape_to_modify=shape_to_modify,
            ground_truth=ground_truth,
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
    result = judge_answer(
        task="resize_shape",
        api_calls=["choose_slide(270)", "choose_shape(148)", "set_width(7772400)"],
        file_hash="MHCZTSXYQDJE3Z6SN7SXERSO63VU3CGK",
        json_data={
            "slide_width": 9144000,
            "slide_height": 6858000,
            "measurement_unit": "emu",
            "slide": {
                "slide_id": 270,
                "slide_name": "",
                "shapes": [
                    {
                        "name": "PlaceHolder 2",
                        "shape_id": 148,
                        "shape_type": "PLACEHOLDER",
                        "measurement_unit": "emu",
                        "height": 4114800,
                        "width": 5978769,
                        "left": 1582615,
                        "top": 1981080,
                        "text": "Gentner AP400 or AP800 Echo Cancel box\\nGenelec speakers (2)\\nMicrophones \\u2013 4 Maximum on the Gentner\\nFor table top use, Crown pcc 160\\nWireless, Vega R22/T25\\nRoom use \\u2013 Crown PZM-30D\\n\\n",
                        "font_details": [
                            {
                                "paragraph_index": 0,
                                "run_index": 0,
                                "text": "Gentner AP400 or AP800 Echo Cancel box",
                                "font_name": "Arial",
                                "font_size": 24.0,
                            },
                            {
                                "paragraph_index": 1,
                                "run_index": 0,
                                "text": "Genelec speakers (2)",
                                "font_name": "Arial",
                                "font_size": 24.0,
                            },
                            {
                                "paragraph_index": 2,
                                "run_index": 0,
                                "text": "Microphones \\u2013 4 Maximum on the Gentner",
                                "font_name": "Arial",
                                "font_size": 24.0,
                            },
                            {
                                "paragraph_index": 3,
                                "run_index": 0,
                                "text": "For table top use, Crown pcc 160",
                                "font_name": "Arial",
                                "font_size": 20.0,
                            },
                            {
                                "paragraph_index": 4,
                                "run_index": 0,
                                "text": "Wireless, Vega R22/T25",
                                "font_name": "Arial",
                                "font_size": 20.0,
                            },
                            {
                                "paragraph_index": 5,
                                "run_index": 0,
                                "text": "Room use \\u2013 Crown PZM-30D",
                                "font_name": "Arial",
                                "font_size": 20.0,
                            },
                        ],
                        "placeholder_type": "OBJECT",
                    },
                    {
                        "name": "PlaceHolder 1",
                        "shape_id": 147,
                        "shape_type": "PLACEHOLDER",
                        "measurement_unit": "emu",
                        "height": 1143000,
                        "width": 7772400,
                        "left": 685800,
                        "top": 609120,
                        "text": "Equipment - Sound",
                        "font_details": [
                            {
                                "paragraph_index": 0,
                                "run_index": 0,
                                "text": "Equipment - Sound",
                                "font_name": "Arial",
                                "font_size": 36.0,
                            }
                        ],
                        "placeholder_type": "TITLE",
                    },
                ],
            },
        },
        ground_truth={
            "slide_width": 9144000,
            "slide_height": 6858000,
            "measurement_unit": "emu",
            "slide": {
                "slide_id": 270,
                "slide_name": "",
                "shapes": [
                    {
                        "name": "PlaceHolder 2",
                        "shape_id": 148,
                        "shape_type": "PLACEHOLDER",
                        "measurement_unit": "emu",
                        "height": 4114800,
                        "width": 7772400,
                        "left": 685800,
                        "top": 1981080,
                        "text": "Gentner AP400 or AP800 Echo Cancel box\\nGenelec speakers (2)\\nMicrophones \\u2013 4 Maximum on the Gentner\\nFor table top use, Crown pcc 160\\nWireless, Vega R22/T25\\nRoom use \\u2013 Crown PZM-30D\\n\\n",
                        "font_details": [
                            {
                                "paragraph_index": 0,
                                "run_index": 0,
                                "text": "Gentner AP400 or AP800 Echo Cancel box",
                                "font_name": "Arial",
                                "font_size": 24.0,
                            },
                            {
                                "paragraph_index": 1,
                                "run_index": 0,
                                "text": "Genelec speakers (2)",
                                "font_name": "Arial",
                                "font_size": 24.0,
                            },
                            {
                                "paragraph_index": 2,
                                "run_index": 0,
                                "text": "Microphones \\u2013 4 Maximum on the Gentner",
                                "font_name": "Arial",
                                "font_size": 24.0,
                            },
                            {
                                "paragraph_index": 3,
                                "run_index": 0,
                                "text": "For table top use, Crown pcc 160",
                                "font_name": "Arial",
                                "font_size": 20.0,
                            },
                            {
                                "paragraph_index": 4,
                                "run_index": 0,
                                "text": "Wireless, Vega R22/T25",
                                "font_name": "Arial",
                                "font_size": 20.0,
                            },
                            {
                                "paragraph_index": 5,
                                "run_index": 0,
                                "text": "Room use \\u2013 Crown PZM-30D",
                                "font_name": "Arial",
                                "font_size": 20.0,
                            },
                        ],
                        "placeholder_type": "OBJECT",
                    },
                    {
                        "name": "PlaceHolder 1",
                        "shape_id": 147,
                        "shape_type": "PLACEHOLDER",
                        "measurement_unit": "emu",
                        "height": 1143000,
                        "width": 7772400,
                        "left": 685800,
                        "top": 609120,
                        "text": "Equipment - Sound",
                        "font_details": [
                            {
                                "paragraph_index": 0,
                                "run_index": 0,
                                "text": "Equipment - Sound",
                                "font_name": "Arial",
                                "font_size": 36.0,
                            }
                        ],
                        "placeholder_type": "TITLE",
                    },
                ],
            },
        },
        shape_to_modify={
            "name": "PlaceHolder 2",
            "shape_id": 148,
            "shape_type": "PLACEHOLDER",
            "measurement_unit": "emu",
            "height": 4114800,
            "width": 5978769,
            "left": 1582615,
            "top": 1981080,
            "text": "Gentner AP400 or AP800 Echo Cancel box\\nGenelec speakers (2)\\nMicrophones \\u2013 4 Maximum on the Gentner\\nFor table top use, Crown pcc 160\\nWireless, Vega R22/T25\\nRoom use \\u2013 Crown PZM-30D\\n\\n",
            "font_details": [
                {
                    "paragraph_index": 0,
                    "run_index": 0,
                    "text": "Gentner AP400 or AP800 Echo Cancel box",
                    "font_name": "Arial",
                    "font_size": 24.0,
                },
                {
                    "paragraph_index": 1,
                    "run_index": 0,
                    "text": "Genelec speakers (2)",
                    "font_name": "Arial",
                    "font_size": 24.0,
                },
                {
                    "paragraph_index": 2,
                    "run_index": 0,
                    "text": "Microphones \\u2013 4 Maximum on the Gentner",
                    "font_name": "Arial",
                    "font_size": 24.0,
                },
                {
                    "paragraph_index": 3,
                    "run_index": 0,
                    "text": "For table top use, Crown pcc 160",
                    "font_name": "Arial",
                    "font_size": 20.0,
                },
                {
                    "paragraph_index": 4,
                    "run_index": 0,
                    "text": "Wireless, Vega R22/T25",
                    "font_name": "Arial",
                    "font_size": 20.0,
                },
                {
                    "paragraph_index": 5,
                    "run_index": 0,
                    "text": "Room use \\u2013 Crown PZM-30D",
                    "font_name": "Arial",
                    "font_size": 20.0,
                },
            ],
            "placeholder_type": "OBJECT",
        },
    )
    print(result)
    # judge_answer_df(
    #     csv_path="data/modification_results/gpt-4o-2024-11-20.csv",
    #     overwrite=True,
    # )


if __name__ == "__main__":
    main()
