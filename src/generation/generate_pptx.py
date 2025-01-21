import logging
import os
from typing import Optional

import pandas as pd

from ..shared.pptx_api.api_executor import api_executor
from ..shared.utils import generate_hash, pptx_to_png

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_pptx_files_with_png_files(
    df: pd.DataFrame,
    base_dir: str,
) -> pd.DataFrame:
    """
    Generate the PowerPoint files based on the DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame containing the API calls.
        base_dir (str): The base directory for the PowerPoint files.

    Returns:
        pd.DataFrame: The DataFrame with the generated PowerPoint files.
    """
    for index, row in df.iterrows():
        try:
            api_calls = row["api_calls"]
            task = row["task"]
            hash = row["hash"]
            hash_str = generate_hash(api_calls, task, hash)
            
            pptx_path = build_pptx_path(base_dir=base_dir, hash_str=hash_str)
            png_path = build_png_path(base_dir=base_dir, hash_str=hash_str)
            
            os.makedirs(os.path.dirname(pptx_path), exist_ok=True)
            os.makedirs(os.path.dirname(png_path), exist_ok=True)
            
            if not generate_pptx(api_calls=api_calls, pptx_path=pptx_path):
                logger.error(f"Failed to generate PPTX for index {index}")
                continue
                
            if not pptx_to_png(pptx_path=pptx_path, png_path=png_path):
                logger.error(f"Failed to convert PPTX to PNG for index {index}")
                continue
                
            df.at[index, "pptx_path"] = pptx_path
            df.at[index, "png_path"] = png_path
            
        except Exception as e:
            logger.error(f"Error processing index {index}: {str(e)}")
            continue
            
    return df

def generate_pptx(
    api_calls: list[str],
    pptx_path: str,
) -> bool:
    """
    Generate a PowerPoint file based on the API calls.

    Args:
        api_calls (List[str]): The API calls to execute.
        pptx_path (str): The path to the PowerPoint file to generate.

    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        api_executor(
            lines=api_calls,
            pptx_path=pptx_path,
            mode="pptx",
        )
        return True
    except Exception as e:
        logger.error(f"Error generating PPTX {pptx_path}: {str(e)}")
        return False

def build_png_path(
    base_dir: str,
    file_name: str,
) -> Optional[str]:
    """
    Build the path to the PNG file based on the hash.

    Args:
        base_dir (str): The base directory for the PNG file.
        file_name (str): The hash string.

    Returns:
        Optional[str]: The path to the PNG file, or None if invalid input.
    """
    try:
        if not base_dir or not file_name:
            raise ValueError("base_dir and file_name must not be empty")
        return f"{base_dir}/png/{file_name}.png"
    except Exception as e:
        logger.error(f"Error building PNG path: {str(e)}")
        return None

def build_pptx_path(
    base_dir: str,
    file_name: str,
) -> Optional[str]:
    """
    Build the path to the PowerPoint file based on the task and hash.

    Args:
        base_dir (str): The base directory for the PowerPoint file.
        file_name (str): The hash string.

    Returns:
        Optional[str]: The path to the PowerPoint file, or None if invalid input.
    """
    try:
        if not base_dir or not file_name:
            raise ValueError("base_dir and file_name must not be empty")
        return f"{base_dir}/pptx/{file_name}.pptx"
    except Exception as e:
        logger.error(f"Error building PPTX path: {str(e)}")
        return None
