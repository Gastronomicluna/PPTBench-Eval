from pathlib import Path
from typing import Any, Dict, List, Union

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
    Handles both list and dictionary formats.

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
    json_data: Union[Dict[str, Any], List[str]],
) -> List[str]:
    """
    Extract the functions from the JSON data and escape newlines.
    Handles various formats:
    1. Dictionary with "functions" key (new preferred format)
    2. List of function strings
    3. Dictionary with "function1", "function2", etc. keys (legacy format)

    Args:
        json_data: The parsed JSON data.

    Returns:
        List[str]: The list of function call strings in order, with escaped newlines.

    Raises:
        TypeError: If json_data is not a dictionary or list.
        ValueError: If no valid functions found in non-empty input.
    """
    # Handle dictionary with "functions" key (new preferred format)
    if isinstance(json_data, dict) and "functions" in json_data:
        functions_list = json_data["functions"]
        if not isinstance(functions_list, list):
            raise ValueError(
                f"'functions' key must contain a list, got {type(functions_list)}"
            )
        if not all(isinstance(item, str) for item in functions_list):
            raise ValueError("All items in the functions list must be strings")

        # Escape newlines in each function string
        return [value.replace("\n", "\\n") for value in functions_list]

    # Handle list format (direct list of functions)
    elif isinstance(json_data, list):
        if not all(isinstance(item, str) for item in json_data):
            raise ValueError("All items in the list must be strings")

        # Escape newlines in each function string
        return [value.replace("\n", "\\n") for value in json_data]

    # Handle dictionary format (legacy format with function1, function2, etc.)
    elif isinstance(json_data, dict):
        # Special case: empty dictionary returns empty list
        if not json_data:
            return []

        function_keys = sorted(
            key for key in json_data.keys() if key.startswith("function")
        )

        # For non-empty dictionaries without functions key, require valid function keys
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

    else:
        raise TypeError(f"Expected dictionary or list input, got {type(json_data)}")


def main() -> None:
    # Test with different formats
    dict_functions_example = {
        "functions": [
            "create_slide()",
            "add_text_box(50000, 50000, 8000000, 1000000, 'Text')",
            "set_font('Arial')",
        ]
    }

    list_example = [
        "create_slide()",
        "add_text_box(50000, 50000, 8000000, 1000000, 'Text')",
        "set_font('Arial')",
    ]

    legacy_dict_example = {
        "function1": "create_slide()",
        "function2": "add_text_box(50000, 50000, 8000000, 1000000, 'Text')",
        "function3": "set_font('Arial')",
    }

    print("Dictionary with 'functions' key (new format):")
    print(extract_functions_from_json(dict_functions_example))

    print("\nList format:")
    print(extract_functions_from_json(list_example))

    print("\nLegacy dictionary format:")
    print(extract_functions_from_json(legacy_dict_example))


if __name__ == "__main__":
    main()
