import csv
import hashlib
import logging
import os
import shutil
import subprocess
import threading
from ast import literal_eval
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union

import httpx
import pandas as pd
from pdf2image import convert_from_path
from thefuzz import fuzz
from .pptx_api.api_doc import API, api_list

T = TypeVar("T")

def get_api_list_prompt() -> str:
    """
    Get the API list prompt with emphasis on using only the provided functions.

    Returns:
        str: The API list as a formatted string with usage restrictions.
    """
    api_list_str = api_to_string(api_list)
    prompt = (
        "IMPORTANT: You must use ONLY the following functions. "
        "Any other functions or operations are not allowed:\n"
        f"{api_list_str}\n"
        "These are the only valid functions you can use. "
        "Do not attempt to use any other functions or operations.\n\n"
    )
    return prompt
class TimeoutException(Exception):
    """Raised when a function execution time exceeds the timeout."""

    pass


def with_timeout(timeout: Optional[int] = None) -> Callable:
    """Thread-based timeout decorator.

    Args:
        timeout: Maximum execution time in seconds. None means no timeout.
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            if timeout is None:
                return func(*args, **kwargs)

            result = []
            error = []

            def worker():
                try:
                    result.append(func(*args, **kwargs))
                except Exception as e:
                    error.append(e)

            thread = threading.Thread(target=worker)
            thread.daemon = True
            thread.start()
            thread.join(timeout)

            if thread.is_alive():
                thread.join(0)  # Don't wait for thread
                raise TimeoutException(
                    f"Function call timed out after {timeout} seconds"
                )

            if error:
                raise error[0]

            return result[0]

        return wrapper

    return decorator


def generate_hash(
    *args: Any,
) -> str:
    """Generate a hash from variable number of arguments.

    Args:
        *args (Any): Variable number of arguments to be hashed.
            All arguments will be converted to strings and concatenated.

    Returns:
        str: MD5 hash of the concatenated string arguments.
    """
    # Convert all arguments to strings and join with a separator
    text = "_".join(str(arg) for arg in args)
    return hashlib.md5(text.encode()).hexdigest()


def get_texts_from_json_data(
    json_data: Dict[str, Any],
) -> List[str]:
    """
    Extract text from a slide's JSON data.

    Args:
        json_data (Dict[str, Any]): A dictionary containing slide data,
            expected to have a 'slide' key containing slide information.

    Returns:
        List[str]: The text content from the slide data.
    """
    slide = json_data.get("slide", {})
    shapes = slide.get("shapes", [])
    texts = [shape.get("text", "") for shape in shapes]
    return texts


def check_unoconv_installation() -> bool:
    """Check if unoconv is installed and accessible.

    Returns:
        bool: True if unoconv is installed and accessible, False otherwise.
    """
    try:
        subprocess.run(["unoconv", "--version"], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def pptx_to_png(
    pptx_path: str,
    output_dir: str,
    dpi: int = 300,
    remove_pdf: bool = True,
) -> None:
    """
    Convert a PowerPoint file to PNG images.

    Args:
        pptx_path (str): The path to the PowerPoint file.
        output_dir (str): The directory to save the PNG images.
        dpi (int, optional): The DPI of the PNG images. Defaults to 300.
        remove_pdf (bool, optional): Whether to remove the PDF file after conversion. Defaults to True.

    Raises:
        RuntimeError: If unoconv is not installed or accessible
        subprocess.CalledProcessError: If conversion fails
    """
    if not os.path.exists(pptx_path):
        raise FileNotFoundError(f"PPTX file does not exist: {pptx_path}")

    if not check_unoconv_installation():
        raise RuntimeError(
            "unoconv is not installed or not accessible. "
            "Please install it using: sudo apt-get install unoconv"
        )

    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    # Create presentation-specific directory
    pptx_name = os.path.splitext(os.path.basename(pptx_path))[0]
    ppt_output_dir = os.path.join(output_dir, pptx_name)
    os.makedirs(ppt_output_dir, exist_ok=True)

    # Convert PPTX -> PDF using unoconv
    base_name, _ = os.path.splitext(pptx_path)
    pdf_path = f"{base_name}.pdf"

    try:
        print(f"Converting {pptx_path} to PDF...")
        result = subprocess.run(
            ["unoconv", "-f", "pdf", pptx_path],
            check=True,
            capture_output=True,
            text=True,
        )
        if result.stderr:
            print(f"Warning during conversion: {result.stderr}")
        print(f"Created PDF: {pdf_path}")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to convert PPTX to PDF: {str(e)}")

    # 2. Convert PDF -> Images (one per PDF page) using pdf2image
    # -----------------------------------------------------------
    print(f"Converting PDF pages to images at {dpi} DPI...")
    pages = convert_from_path(pdf_path, dpi=dpi)

    for i, page in enumerate(pages):
        # Save each page as a PNG (you could choose 'JPEG' if preferred)
        output_filename = os.path.join(ppt_output_dir, f"slide_{i+1}.png")
        page.save(output_filename, "PNG")
        print(f"Saved image: {output_filename}")

    # 3. Optionally remove the intermediate PDF
    # -----------------------------------------
    if remove_pdf and os.path.exists(pdf_path):
        os.remove(pdf_path)
        print(f"Removed intermediate PDF: {pdf_path}")

    print("Conversion complete!")


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


def csv_to_df(
    csv_path: Path,
    encoding: str = "utf-8",
    list_columns: Optional[List[str]] = None,
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

        if list_columns:
            for column in list_columns:
                df[column] = df[column].apply(
                    lambda x: literal_eval(x) if pd.notna(x) else x
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
            na_rep="NULL",
        )
        return True
    except Exception:
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
    json_mode: bool,
    timeout: int,
    csv_path: Union[str, Path],
    overwrite: bool = False,
) -> pd.DataFrame:
    """Process a single model's answers.

    Args:
        df: Input dataframe containing questions
        model_name: Name of the model to use
        provider: Provider of the model
        temperature: Sampling temperature
        max_tokens: Maximum tokens in response
        json_mode: Whether to return JSON format
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
            json_mode=json_mode,
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


def load_existing_answers(csv_path: Path) -> pd.DataFrame:
    """
    Load existing answers from CSV file using the utility function.

    Args:
        csv_path (Path): Path to the CSV file.

    Returns:
        pd.DataFrame: DataFrame containing existing answers, empty if file not found.
    """
    df = csv_to_df(csv_path)
    if df is None:
        return pd.DataFrame()
    return df


def build_json_path(
    file_hash: str,
    json_dir: Path = Path("dataset/json"),  # Changed from data/json to dataset/json
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
    if ground_truth == answer:
        return True

    ratio = fuzz.ratio(ground_truth, answer) / 100
    return ratio >= threshold


def download_kaggle_dataset(
    dataset_name: str,
    destination_dir: Union[str, Path] = "data",
    new_dir_name: Optional[str] = None,
    delete_metadata: bool = True,
    force_download: bool = False,
) -> None:
    """
    Download a Kaggle dataset to the specified directory.

    Args:
        dataset_name (str): Name of the Kaggle dataset.
        destination_dir (Union[str, Path]): Path to the destination directory.
            Defaults to "data".
        new_dir_name (Optional[str]): Name of the new directory to create.
            Defaults to None.
        delete_metadata (bool): Whether to delete metadata files.
            Defaults to True.
        force_download (bool): Whether to force download even if directory exists.
            Defaults to False.
    """
    destination_dir = Path(destination_dir).resolve()
    os.makedirs(destination_dir, exist_ok=True)

    # Determine the target directory
    dataset_default_name = dataset_name.split("/")[-1]
    target_dir = destination_dir / new_dir_name
    # print(target_dir)
    if target_dir.exists() and not force_download:
        print(f"Directory {target_dir} already exists, skipping download")
        return

    # Create temporary download directory
    temp_download_dir = destination_dir / "temp_download"
    os.makedirs(temp_download_dir, exist_ok=True)

    # Download to temporary directory
    os.system(
        f"kaggle datasets download -d {dataset_name} -p {temp_download_dir} --unzip"
    )

    # Delete metadata file if requested
    if delete_metadata:
        metadata_file = temp_download_dir / "dataset-metadata.json"
        if metadata_file.exists():
            os.remove(metadata_file)

    if target_dir.exists():
        shutil.rmtree(target_dir)

    temp_dataset_dir = temp_download_dir / dataset_default_name
    if temp_dataset_dir.exists():
        shutil.move(str(temp_dataset_dir), str(target_dir))
    else:
        # If dataset was extracted directly into temp_download_dir
        os.makedirs(target_dir, exist_ok=True)
        for item in temp_download_dir.iterdir():
            if item.name != "dataset-metadata.json":
                shutil.move(str(item), str(target_dir / item.name))

    # Clean up temporary directory
    shutil.rmtree(temp_download_dir)


def api_to_string(
    api_list: List[API],
) -> str:
    """
    Convert a list of API objects to a string representation.

    Args:
        api_list (list): List of API objects.

    Returns:
        str: String representation of the API list.
    """
    api_strings = []
    for api in api_list:
        # Format each API with essential information only
        api_str = (
            f"{api.name}({api.parameters}) "
            + f"Description: {api.description} "
            + f"Notes: {api.notes}"
        )

        api_strings.append(api_str)

    # Join all API strings with clear separation
    return "\n".join(api_strings)


def get_notes_from_json_data(json_data: Dict[str, Any]) -> str:
    """Extract notes from a slide's JSON data.

    Args:
        json_data (Dict[str, Any]): A dictionary containing slide data,
            expected to have a 'slide' key containing slide information.

    Returns:
        str: The notes text from the slide data. Empty string if no notes found.
    """
    slide = json_data.get("slide", {})
    notes = slide.get("notes", {})
    note = notes["text"]
    return note


def str_to_list(s: str) -> List[str]:
    """
    Safely convert string representation of list back to list.

    Args:
        s (str): String representation of a list.

    Returns:
        List[str]: Converted list of strings.

    Raises:
        ValueError: If input is not a valid list representation.
    """
    try:
        # Remove potential whitespace and verify format
        s = s.strip()
        if not (s.startswith("[") and s.endswith("]")):
            raise ValueError("Invalid list format")

        # Use ast.literal_eval for safe evaluation
        result = literal_eval(s)
        if not isinstance(result, list):
            raise ValueError("Parsed result is not a list")

        return result
    except Exception as e:
        raise ValueError(f"Failed to convert string to list: {str(e)}")
