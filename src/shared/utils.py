import csv
import hashlib
import logging
import os
import subprocess
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

import httpx
import pandas as pd
from pdf2image import convert_from_path
from thefuzz import fuzz

from .pptx_api.api_doc import API


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
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    # Create presentation-specific directory
    pptx_name = os.path.splitext(os.path.basename(pptx_path))[0]
    ppt_output_dir = os.path.join(output_dir, pptx_name)
    os.makedirs(ppt_output_dir, exist_ok=True)

    # 1. Convert PPTX -> PDF using unoconv
    # -------------------------------------------------
    # By default, unoconv will create a PDF with the same base filename
    # but with a .pdf extension in the same folder as the input PPTX.
    base_name, _ = os.path.splitext(pptx_path)
    pdf_path = f"{base_name}.pdf"

    print(f"Converting {pptx_path} to PDF...")
    subprocess.run(["unoconv", "-f", "pdf", pptx_path], check=True)
    print(f"Created PDF: {pdf_path}")

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
    json_dir: Path = Path("dataset/json"),
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

    target_dir = destination_dir / dataset_name.split("/")[-1]
    # Check if directory already exists
    if new_dir_name is not None:
        target_dir = destination_dir / new_dir_name
        print(f"Downloading dataset to {target_dir}")
        
    if target_dir.exists() and not force_download:
        print(f"Directory {target_dir} already exists, skipping download")
        return

    # Download and unzip dataset
    os.system(
        f"kaggle datasets download -d {dataset_name} -p {destination_dir} --unzip"
    )

    # Delete metadata file if requested
    if delete_metadata:
        metadata_files = ["dataset-metadata.json"]
        for metadata_file in metadata_files:
            metadata_path = destination_dir / metadata_file
            if metadata_path.exists():
                os.remove(metadata_path)

    # Rename directory if new_dir_name is provided
    if new_dir_name:
        source_dir = destination_dir / dataset_name.split("/")[-1]
        target_dir = destination_dir / new_dir_name

        if target_dir.exists():
            import shutil

            shutil.rmtree(target_dir)

        if source_dir.exists():
            os.rename(source_dir, target_dir)


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


def main() -> None:
    json_data = {
        "slide_width": 9144000,
        "slide_height": 6858000,
        "measurement_unit": "emu",
        "slide": {
            "slide_id": 264,
            "slide_name": "",
            "shapes": [
                {
                    "name": "PlaceHolder 1",
                    "shape_id": 177,
                    "shape_type": "PLACEHOLDER",
                    "measurement_unit": "emu",
                    "height": 830160,
                    "width": 8391600,
                    "left": 488880,
                    "top": 639720,
                    "text": "NEOGOV Insight – Online Hiring Center",
                    "font_details": [
                        {
                            "paragraph_index": 0,
                            "run_index": 0,
                            "text": "NEOGOV Insight – Online Hiring Center",
                            "font_name": "Arial Black",
                            "font_size": 28.0,
                        }
                    ],
                    "placeholder_type": "TITLE",
                },
                {
                    "name": "Content Placeholder 5",
                    "shape_id": 178,
                    "shape_type": "PICTURE",
                    "measurement_unit": "emu",
                    "height": 3849840,
                    "width": 7932600,
                    "left": 797040,
                    "top": 1938240,
                    "auto_shape_type": "RECTANGLE",
                    "image_path": "dataset/extracted_images/MZQPJKFSDHY2HXUX7CLFFQSHYDC5O3RV/8/image_8_2.jpg",
                },
                {
                    "name": "Slide Number Placeholder 4",
                    "shape_id": 179,
                    "shape_type": "AUTO_SHAPE",
                    "measurement_unit": "emu",
                    "height": 476280,
                    "width": 2133720,
                    "left": 6553080,
                    "top": 6245280,
                    "text": "<number>",
                    "font_details": [],
                },
            ],
            "notes": {
                "text": "This slide shows the OHC roles – note there are several roles available to agencies.\nEach agency must have a minimum of 1 person with the following 2 roles: Recruiter/Analyst (which is an Insight role) and HR Liaison (which is an OHC role).\nLiaisons can set up other Liaisons and the other roles within your agency only.\nIf you decide to involve hiring managers/supervisors or even admin to do some tasks, you may opt to use other roles.\n\nNote: If you have OHC and Insight-HR access, you may have two different passwords. When you are granted initial access, your password will be the same for both.",
                "font_details": [
                    {
                        "paragraph_index": 0,
                        "run_index": 0,
                        "text": "This slide shows the OHC roles – note there are several roles available to agencies.",
                        "font_name": "Arial",
                        "font_size": 12.0,
                    },
                    {
                        "paragraph_index": 1,
                        "run_index": 0,
                        "text": "Each agency must have a minimum of 1 person with the following 2 roles: Recruiter/Analyst (which is an Insight role) and HR Liaison (which is an OHC role).",
                        "font_name": "Arial",
                        "font_size": 12.0,
                    },
                    {
                        "paragraph_index": 2,
                        "run_index": 0,
                        "text": "Liaisons can set up other Liaisons and the other roles within your agency only.",
                        "font_name": "Arial",
                        "font_size": 12.0,
                    },
                    {
                        "paragraph_index": 3,
                        "run_index": 0,
                        "text": "If you decide to involve hiring managers/supervisors or even admin to do some tasks, you may opt to use other roles.",
                        "font_name": "Arial",
                        "font_size": 12.0,
                    },
                    {
                        "paragraph_index": 5,
                        "run_index": 0,
                        "text": "Note: If you have OHC and Insight-HR access, you may have two different passwords. When you are granted initial access, your password will be the same for both.",
                        "font_name": "Arial",
                        "font_size": 12.0,
                    },
                ],
            },
        },
    }
    notes = get_notes_from_json_data(json_data)
    print(notes)


if __name__ == "__main__":
    main()
