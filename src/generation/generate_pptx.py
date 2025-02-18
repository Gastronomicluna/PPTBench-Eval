import ast
import logging
import os
import traceback
from pathlib import Path
from typing import List, Optional

import pandas as pd

from ..shared.pptx_api.api_executor import api_executor
from ..shared.utils import csv_to_df, df_to_csv, pptx_to_png, str_to_list

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


def generate_pptx_files_csv(
    csv_path: Path,
    base_dir: Path,
    output_dir: Path,
    overwrite: bool = False,
) -> pd.DataFrame:
    """
    Generate PowerPoint files from a CSV file containing API calls.

    Args:
        csv_path (Path): Path to the CSV file containing API calls.
        base_dir (Path): Base directory for input files.
        output_dir (Path): Directory where generated files will be saved.
        overwrite (bool, optional): Whether to overwrite existing files. Defaults to False.

    Returns:
        pd.DataFrame: DataFrame with generated PowerPoint and PNG files information.
    """
    try:
        if not csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")

        df = csv_to_df(csv_path=csv_path)

        if not overwrite:
            df = df[df["pptx_path"].isna() | df["png_path"].isna()]
            if df.empty:
                logger.info("No new files to generate")
                return df

        model_name = csv_path.stem  # derive model_name from CSV file name

        result_df = generate_pptx_files_with_png_files(
            df=df, base_dir=base_dir, output_dir=output_dir, model_name=model_name
        )

        if df_to_csv(df=result_df, csv_path=csv_path):
            return result_df
        else:
            logger.error("Failed to save the updated CSV file")
            return pd.DataFrame()
    except Exception as e:
        logger.error(f"Error processing CSV file: {str(e)}")
        return pd.DataFrame()


def generate_pptx_files_with_png_files(
    df: pd.DataFrame,
    base_dir: Path,
    output_dir: Path,
    model_name: str,
) -> pd.DataFrame:
    """
    Generate the PowerPoint files based on the DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame containing the API calls.
        base_dir (Path): Base directory for input files.
        output_dir (Path): Directory where generated files will be saved.
        model_name (str): Name of the model being evaluated.

    Returns:
        pd.DataFrame: The DataFrame with the generated PowerPoint files.
    """
    model_dir = output_dir / model_name
    png_dir = model_dir / "png"
    os.makedirs(png_dir, exist_ok=True)

    for index, row in df.iterrows():
        try:
            # Convert string representation back to list
            api_calls = str_to_list(row["answer"]) if pd.notna(row["answer"]) else []

            if not api_calls:
                df.at[index, "error"] = "Empty or invalid API calls list"
                continue

            file_hash = row["file_hash"]

            pptx_path = build_pptx_path(base_dir=base_dir, file_name=file_hash, model_name=model_name)
            output_dir = build_pptx_path(base_dir=output_dir, file_name=file_hash, model_name=model_name)
            os.makedirs(output_dir.parent, exist_ok=True)

            if not generate_pptx(
                api_calls=api_calls,
                pptx_path=pptx_path,
                output_path=output_dir,
            ):
                error_msg = f"Failed to generate PPTX"
                logger.error(f"{error_msg} for index {index}")
                df.at[index, "error"] = error_msg
                continue

            try:
                pptx_to_png(
                    pptx_path=str(pptx_path),
                    output_dir=str(png_dir),
                    dpi=300,
                    remove_pdf=True,
                )
                df.at[index, "pptx_path"] = str(pptx_path)
                df.at[index, "png_path"] = str(png_dir / file_hash)
                # Only clear error if there wasn't one before
                if pd.isna(row.get("error")):
                    df.at[index, "error"] = None

            except Exception as e:
                error_msg = f"Failed to convert PPTX to PNG: {str(e)}"
                logger.error(f"{error_msg} for index {index}")
                df.at[index, "error"] = error_msg
                continue

        except Exception as e:
            error_msg = f"Error processing row: {str(e)}"
            logger.error(
                f"{error_msg} for index {index}\n"
                f"Traceback:\n{traceback.format_exc()}"
            )
            df.at[index, "error"] = error_msg
            continue

    return df


def generate_pptx(
    api_calls: List[str],
    pptx_path: Path,
    output_path: Optional[Path] = None,
) -> bool:
    """
    Generate a PowerPoint file based on the API calls.

    Args:
        api_calls (List[str]): The API calls to execute.
        pptx_path (Path): The path to the PowerPoint file to generate.

    Returns:
        bool: True if successful, False otherwise.
    """
    # Check if pptx exists
    if not pptx_path.exists():
        print(f"pptx_path does not exist: {pptx_path}")

    if isinstance(api_calls, list):
        # print(f"api_calls is a list: {api_calls}")
        try:
            api_executor(
                lines=api_calls,
                pptx_path=pptx_path,
                output_path=output_path,
                mode="pptx",
            )
            return True
        except Exception as e:
            logger.error(
                f"Error generating PPTX {pptx_path}: {str(e)}\n"
                f"Traceback:\n{traceback.format_exc()}"
            )
            # print(f"Error generating PPTX {pptx_path}: {str(e)}")
            return False
    else:
        # print(f"api_calls is not a list: {api_calls}")
        return False


def build_png_path(
    output_dir: Path,
    file_name: str,
    model_name: str,
) -> Optional[Path]:
    """
    Build the path to the PNG file based on the hash.

    Args:
        output_dir (Path): Directory where generated files will be saved.
        file_name (str): The hash string.
        model_name (str): Name of the model being evaluated.

    Returns:
        Optional[Path]: The path to the PNG file, or None if invalid input.
    """
    try:
        if not output_dir or not file_name or not model_name:
            raise ValueError("output_dir, file_name and model_name must not be empty")
        return output_dir / model_name / "png" / f"{file_name}.png"
    except Exception as e:
        logger.error(f"Error building PNG path: {str(e)}")
        return None


def build_pptx_path(
    base_dir: Path,
    file_name: str,
    model_name: str,
) -> Optional[Path]:
    """
    Build the path to the PowerPoint file based on the task and hash.

    Args:
        base_dir (Path): The base directory for the PowerPoint file.
        file_name (str): The hash string.
        model_name (str): Name of the model being evaluated.

    Returns:
        Optional[Path]: The path to the PowerPoint file, or None if invalid input.
    """
    try:
        if not base_dir or not file_name or not model_name:
            raise ValueError("base_dir, file_name and model_name must not be empty")
        return base_dir / model_name / "pptx" / f"{file_name}.pptx"
    except Exception as e:
        logger.error(f"Error building PPTX path: {str(e)}")
        return None
