import csv
import logging
from pathlib import Path
from typing import Optional

import pandas as pd


def get_image_bytes(image_data: dict | bytes) -> bytes:
    """Extract image bytes from dataset row.

    Args:
        image_data: Image data from dataset row, either dict or bytes

    Returns:
        bytes: Raw image bytes
    """
    if isinstance(image_data, dict):
        return image_data["bytes"]
    return image_data


def csv_to_df(csv_path: Path, encoding: str = "utf-8") -> Optional[pd.DataFrame]:
    """
    Convert CSV file to pandas DataFrame with proper error handling.

    Args:
        csv_path (Path): Path to the CSV file.
        encoding (str): File encoding. Defaults to "utf-8".

    Returns:
        Optional[pd.DataFrame]: DataFrame if successful, None if failed.
    """
    if not csv_path.exists():
        logging.warning(f"CSV file not found: {csv_path}")
        return None

    try:
        df = pd.read_csv(
            csv_path,
            quoting=csv.QUOTE_ALL,
            escapechar="\\",
            encoding=encoding,
            lineterminator="\n",
            on_bad_lines="warn",
        )
        return df
    except Exception as e:
        logging.error(f"Error reading CSV {csv_path}: {str(e)}")
        return None


def df_to_csv(
    df: pd.DataFrame,
    csv_path: Path,
    mode: str = "w",
    encoding: str = "utf-8",
) -> bool:
    """
    Save DataFrame to CSV file with proper error handling.

    Args:
        df (pd.DataFrame): DataFrame to save.
        csv_path (Path): Path to save the CSV file.
        mode (str): Write mode ('w' for write, 'a' for append).
            Defaults to 'w'.
        encoding (str): File encoding. Defaults to "utf-8".

    Returns:
        bool: True if successful, False if failed.
    """
    try:
        df.to_csv(
            csv_path,
            mode=mode,
            header=(mode == "w" or not csv_path.exists()),
            index=False,
            quoting=csv.QUOTE_ALL,
            escapechar="\\",
            encoding=encoding,
            lineterminator="\n",
        )
        return True
    except Exception as e:
        logging.error(f"Error writing CSV {csv_path}: {str(e)}")
        return False

def get_project_root() -> Path:
    """Get the absolute path to the project root directory.

    Returns:
        Path: Absolute path to the project root directory.
    """
    current_file = Path(__file__).resolve()
    return current_file.parent.parent.parent