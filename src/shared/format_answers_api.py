from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

from .parse_answer import parse_json_answer
from .utils import csv_to_df, df_to_csv


def format_answer_csv(
    csv_path: Path,
    overwrite: bool = False,
) -> pd.DataFrame:
    """
    Format the answers in the CSV file.

    Args:
        csv_path (Path): Path to the CSV file.
        overwrite (bool, optional): Whether to overwrite existing answers.
            If False and answer column exists with values, skip processing.
            Defaults to False.

    Returns:
        pd.DataFrame: DataFrame with formatted answers.
    """
    try:
        df = csv_to_df(csv_path)
        if df is None:
            raise ValueError("The CSV file is empty.")

        # Initialize error column with string dtype if it doesn't exist
        if "error" not in df.columns:
            df["error"] = pd.Series(dtype="string")
        else:
            # Ensure existing error column is string type
            df["error"] = df["error"].astype("string")

        # Only check for existing answers if overwrite is False
        if "answer" in df.columns and not overwrite:
            if not df["answer"].isna().all():
                return df

        def apply_format_safely(row):
            # Skip if there's already an error
            if pd.notna(row["error"]):
                return pd.NA

            try:
                result = format_answer(row["llm_answer"])
                # Convert list to string representation for safe storage
                return str(result) if result is not None else pd.NA
            except Exception as e:
                df.at[row.name, "error"] = str(e)
                return pd.NA

        # Ensure answer column is string type
        df["answer"] = df.apply(apply_format_safely, axis=1).astype("string")

        if not df_to_csv(df, csv_path):
            raise ValueError("Failed to save the formatted answers.")

        return df

    except Exception as e:
        raise Exception(f"Error processing CSV file: {e}")


def format_answer(answer: str) -> List[str]:
    """
    Format the extracted functions for the detection tasks.

    Args:
        answer (str): The extracted functions.

    Returns:
        List[str]: The formatted list of functions.

    Raises:
        TypeError: If answer is not a string.
        ValueError: If answer is empty or invalid JSON format.
    """
    if not isinstance(answer, str):
        raise TypeError(f"Expected string input, got {type(answer)}")

    if not answer.strip():
        raise ValueError("Empty input string")

    try:
        json_answer = parse_json_answer(answer)
        functions = extract_functions_from_json(json_answer)
        return functions
    except Exception as e:
        raise ValueError(f"Error formatting answer: {str(e)}")


def extract_functions_from_json(
    json_data: Dict[str, Any],
) -> List[str]:
    """
    Extract the functions from the JSON data and escape newlines.

    Args:
        json_data (Dict[str, Any]): The JSON data containing numbered function keys
            (e.g., "function1", "function2", etc.) with function call strings as values.

    Returns:
        List[str]: The list of function call strings in order, with escaped newlines.
            Returns empty list only for empty dictionary.

    Raises:
        TypeError: If json_data is not a dictionary.
        ValueError: If no valid function keys found in non-empty dictionary,
            or if function values are invalid.
    """
    if not isinstance(json_data, dict):
        raise TypeError(f"Expected dictionary input, got {type(json_data)}")

    # Special case: empty dictionary returns empty list
    if not json_data:
        return []

    function_keys = sorted(
        key for key in json_data.keys() if key.startswith("function")
    )

    # For non-empty dictionaries, require valid function keys
    if not function_keys:
        raise ValueError("No valid function keys found in non-empty input")

    functions = []
    for key in function_keys:
        value = json_data[key]
        if not isinstance(value, str):
            raise ValueError(
                f"Function value must be string, got {type(value)} for {key}"
            )
        if not value.strip():
            raise ValueError(f"Empty function value for {key}")
        # Replace \n with \\n in the function string
        escaped_value = value.replace("\n", "\\n")
        functions.append(escaped_value)

    return functions


def main() -> None:
    llm_answer = {
        "function1": "create_slide()",
        "function2": "add_text_box(50000, 50000, 8000000, 1000000, 'Are there any time limits for filing?')",
        "function3": "set_font('Times New Roman')",
        "function4": "set_font_size(440000)",
        "function5": "set_font_style('bold')",
        "function6": "add_text_box(50000, 150000, 8000000, 3000000, 'Complainants must contact an EEO counselor within 45 days of the effective date of the personnel action or within 45 days of the occurrence of the action which led to EEO contact.')",
        "function7": "set_font('Arial')",
        "function8": "set_font_size(360000)",
    }
    answers = extract_functions_from_json(llm_answer)
    print(answers)


if __name__ == "__main__":
    main()
