import csv
import logging
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Union
import os
import httpx
import pandas as pd
from thefuzz import fuzz


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


def process_model(
    function: Callable,
    df: pd.DataFrame,
    model_name: str,
    provider: str,
    temperature: float,
    max_tokens: int,
    json: bool,
    timeout: int,
    csv_path: Union[str, Path],
    overwrite: bool,
) -> pd.DataFrame:
    """Process a single model's answers.

    Args:
        df: Input dataframe containing questions
        model_name: Name of the model to use
        provider: Provider of the model
        temperature: Sampling temperature
        max_tokens: Maximum tokens in response
        json: Whether to return JSON format
        timeout: Timeout in seconds
        csv_path: Path to save results
        overwrite: Whether to overwrite existing results

    Returns:
        pd.DataFrame: Results dataframe
    """
    try:
        print(f"Processing {model_name}...")
        results_df = function(
            df=df,
            model_name=model_name,
            provider=provider,
            temperature=temperature,
            max_tokens=max_tokens,
            json=json,
            timeout=timeout,
            csv_path=csv_path,
            overwrite=overwrite,
        )
        print(f"Processed {len(results_df)} entries")
        return results_df
    except httpx.ConnectError as e:
        logging.error("Ollama not running. Please start the server. %s", e)
        return pd.DataFrame()
    except Exception as e:
        logging.error(f"Error processing {model_name}: {str(e)}")
        return pd.DataFrame()  # Return empty DataFrame on error


def load_existing_answers(csv_path: Path) -> Dict[str, Dict[str, Any]]:
    """
    Load existing answers from CSV file using the utility function.

    Args:
        csv_path (Path): Path to the CSV file.

    Returns:
        Dict[str, Dict[str, Any]]: Dictionary of existing answers keyed by hash.
    """
    df = csv_to_df(csv_path)
    if df is None:
        return {}

    return {row["hash"]: row.to_dict() for _, row in df.iterrows()}


def build_json_path(
    file_hash: str,
    json_dir: Path = Path("data/json"),
) -> Path:
    """
    Build the JSON path for the given file hash.

    Args:
        json_dir (Path): Path to the JSON directory.
        file_hash (str): Hash of the file.

    Returns:
        Path: Path to the JSON file.
    """
    return json_dir / f"{file_hash}.json"


def fuzzy_match(
    ground_truth: str,
    answer: str,
    threshold: float = 0.9,
) -> bool:
    """
    Fuzzy matching function to compare the ground truth and the answer.

    Args:
        ground_truth (str): The ground truth answer.
        answer (str): The answer from the model.
        threshold (float): The threshold for the fuzzy matching
    Returns:
        bool: Whether the answer is correct.
    """
    ratio = fuzz.ratio(ground_truth, answer) / 100
    return ratio >= threshold


def download_kaggle_dataset(
    dataset_name: str,
    destination_dir: Union[str, Path] = "data",
    new_dir_name: Optional[str] = None,
) -> None:
    """
    Download a Kaggle dataset to the specified directory.

    Args:
        dataset_name (str): Name of the Kaggle dataset.
        destination_dir (Union[str, Path]): Path to the destination directory.
            Defaults to "data".
        new_dir_name (Optional[str]): Name of the new directory to create.
            Defaults to None.
    """
    os.system(f"kaggle datasets download -d {dataset_name} -p {destination_dir} --unzip")
    
    # Delete metadata file
    metadata_files = ["dataset-metadata.json"]
    for metadata_file in metadata_files:
        metadata_path = Path(destination_dir) / dataset_name / metadata_file
        if metadata_path.exists():
            os.remove(metadata_path)
    
    if new_dir_name:
        os.system(f"mv {destination_dir}/{dataset_name} {destination_dir}/{new_dir_name}")
        