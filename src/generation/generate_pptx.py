import logging
import os
import traceback
from pathlib import Path
from typing import Optional

import pandas as pd

from ..shared.pptx_api.api_executor import api_executor
from ..shared.utils import csv_to_df, df_to_csv, generate_hash, pptx_to_png

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_pptx_files_csv(
    csv_path: Path,
    base_dir: Path,
    overwrite: bool = False,
) -> pd.DataFrame:
    """
    Generate PowerPoint files from a CSV file containing API calls.

    Args:
        csv_path (Path): Path to the CSV file containing API calls.
        overwrite (bool, optional): Whether to overwrite existing files. Defaults to False.

    Returns:
        pd.DataFrame: DataFrame with generated PowerPoint and PNG files information.
    """
    try:
        if not csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")

        df = csv_to_df(csv_path=csv_path)
        # print(df.info())
        if not overwrite:
            # Filter out rows that already have generated files
            df = df[df["pptx_path"].isna() | df["png_path"].isna()]
            if df.empty:
                logger.info("No new files to generate")
                return df

        result_df = generate_pptx_files_with_png_files(df=df, base_dir=base_dir)

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
) -> pd.DataFrame:
    """
    Generate the PowerPoint files based on the DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame containing the API calls.
        base_dir (Path): The base directory for the PowerPoint files.

    Returns:
        pd.DataFrame: The DataFrame with the generated PowerPoint files.
    """
    png_dir = base_dir / "png"
    os.makedirs(png_dir, exist_ok=True)

    for index, row in df.iterrows():
        try:
            api_calls = row["answer"]
            task = row["task"]
            hash = row["hash"]
            hash_str = generate_hash(api_calls, task, hash)

            pptx_path = build_pptx_path(base_dir=base_dir, file_name=hash_str)
            os.makedirs(pptx_path.parent, exist_ok=True)

            if not generate_pptx(api_calls=api_calls, pptx_path=pptx_path):
                logger.error(f"Failed to generate PPTX for index {index}")
                continue

            # Convert PPTX to PNGs in the shared png directory
            try:
                pptx_to_png(
                    pptx_path=str(pptx_path),
                    output_dir=str(png_dir),
                    dpi=300,
                    remove_pdf=True,
                )
                # Store the base directory path for PNGs
                df.at[index, "pptx_path"] = str(pptx_path)
                df.at[index, "png_path"] = str(png_dir / hash_str)

            except Exception as e:
                logger.error(
                    f"Failed to convert PPTX to PNG for index {index}: {str(e)}"
                )
                continue

        except Exception as e:
            logger.error(
                f"Error processing index {index}: {str(e)}\n"
                f"Traceback:\n{traceback.format_exc()}"
            )
            continue

    return df


def generate_pptx(
    api_calls: list[str],
    pptx_path: Path,
) -> bool:
    """
    Generate a PowerPoint file based on the API calls.

    Args:
        api_calls (List[str]): The API calls to execute.
        pptx_path (Path): The path to the PowerPoint file to generate.

    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        api_executor(
            lines=api_calls,
            pptx_path=str(pptx_path),
            mode="pptx",
        )
        return True
    except Exception as e:
        logger.error(
            f"Error generating PPTX {pptx_path}: {str(e)}\n"
            f"Traceback:\n{traceback.format_exc()}"
        )
        return False


def build_png_path(
    base_dir: Path,
    file_name: str,
) -> Optional[Path]:
    """
    Build the path to the PNG file based on the hash.

    Args:
        base_dir (Path): The base directory for the PNG file.
        file_name (str): The hash string.

    Returns:
        Optional[Path]: The path to the PNG file, or None if invalid input.
    """
    try:
        if not base_dir or not file_name:
            raise ValueError("base_dir and file_name must not be empty")
        return base_dir / "png" / f"{file_name}.png"
    except Exception as e:
        logger.error(f"Error building PNG path: {str(e)}")
        return None


def build_pptx_path(
    base_dir: Path,
    file_name: str,
) -> Optional[Path]:
    """
    Build the path to the PowerPoint file based on the task and hash.

    Args:
        base_dir (Path): The base directory for the PowerPoint file.
        file_name (str): The hash string.

    Returns:
        Optional[Path]: The path to the PowerPoint file, or None if invalid input.
    """
    try:
        if not base_dir or not file_name:
            raise ValueError("base_dir and file_name must not be empty")
        return base_dir / "pptx" / f"{file_name}.pptx"
    except Exception as e:
        logger.error(f"Error building PPTX path: {str(e)}")
        return None
