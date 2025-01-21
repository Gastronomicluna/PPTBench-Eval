import pandas as pd

from ..shared.pptx_api.api_executor import api_executor
from ..shared.utils import pptx_to_png, generate_hash


def generate_png_files_from_pptx_files(
    df: pd.DataFrame,
    base_dir: str,
) -> pd.DataFrame:
    """
    Generate the PNG files from the PowerPoint files in the DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame containing the PowerPoint files.
        base_dir (str): The base directory for the PNG files.

    Returns:
        pd.DataFrame: The DataFrame with the generated PNG files.
    """
    for index, row in df.iterrows():
        pptx_path = row["pptx_path"]
        hash_str = row["hash"]
        png_path = build_png_path(
            base_dir=base_dir,
            hash_str=hash_str,
        )
        pptx_to_png(
            pptx_path=pptx_path,
            png_path=png_path,
        )
        df.at[index, "png_path"] = png_path
    return df

def generate_pptx_files(
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
        api_calls = row["api_calls"]
        task = row["task"]
        hash = row["hash"]
        hash_str = generate_hash(api_calls, task, hash)
        pptx_path = build_pptx_path(
            base_dir=base_dir,
            hash_str=hash_str,
        )
        generate_pptx(
            api_calls=api_calls,
            pptx_path=pptx_path,
        )
        df.at[index, "pptx_path"] = pptx_path
    return df


def generate_pptx(
    api_calls: list[str],
    pptx_path: str,
) -> None:
    """
    Generate a PowerPoint file based on the API calls.

    Args:
        api_calls (List[str]): The API calls to execute.
        pptx_path (str): The path to the PowerPoint file to generate.
    """
    api_executor(
        lines=api_calls,
        pptx_path=pptx_path,
        mode="pptx",
    )



def build_png_path(
    base_dir: str,
    hash_str: str,
) -> str:
    """
    Build the path to the PNG file based on the hash.
    
    Args:
        base_dir (str): The base directory for the PNG file.
        hash_str (str): The hash string.
        
    Returns:
        str: The path to the PNG file.
    """
    return f"{base_dir}/png/{hash_str}.png"
def build_pptx_path(
    base_dir: str,
    hash_str: str,
) -> str:
    """
    Build the path to the PowerPoint file based on the task and hash.

    Args:
        base_dir (str): The base directory for the PowerPoint file.
        task (str): The task name.
        hash_str (str): The hash string.

    Returns:
        str: The path to the PowerPoint file.
    """
    return f"{base_dir}/pptx/{hash_str}.pptx"
