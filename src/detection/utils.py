import csv
import logging
from pathlib import Path
from typing import Optional

import pandas as pd

from .judge import compare_coordinate, exact_match, fuzzy_match

SUBCATEGORY_JUDGE_FUNCTION = {
    "content extraction": fuzzy_match,
    "layout detection": compare_coordinate,
    "style detection": exact_match,
}

def csv_to_df(
    csv_path: Path, 
    encoding: str = "utf-8"
) -> Optional[pd.DataFrame]:
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
