import pandas as pd

from ..shared.pptx_api.api_executor import api_executor
from ..shared.utils import pptx_to_png, generate_hash



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
        api_calls = row["api_calls"]
        task = row["task"]
        hash = row["hash"]
        hash_str = generate_hash(api_calls, task, hash)
        pptx_path = build_pptx_path(
            base_dir=base_dir,
            hash_str=hash_str,
        )
        png_path = build_png_path(
            base_dir=base_dir,
            hash_str=hash_str,
        )
        generate_pptx(
            api_calls=api_calls,
            pptx_path=pptx_path,
        )
        pptx_to_png(
            pptx_path=pptx_path,
            png_path=png_path,
        )
        df.at[index, "pptx_path"] = pptx_path
        df.at[index, "png_path"] = png_path
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
    file_name: str,
) -> str:
    """
    Build the path to the PNG file based on the hash.
    
    Args:
        base_dir (str): The base directory for the PNG file.
        file_name (str): The hash string.
        
    Returns:
        str: The path to the PNG file.
    """
    return f"{base_dir}/png/{file_name}.png"
def build_pptx_path(
    base_dir: str,
    file_name: str,
) -> str:
    """
    Build the path to the PowerPoint file based on the task and hash.

    Args:
        base_dir (str): The base directory for the PowerPoint file.
        task (str): The task name.
        file_name (str): The hash string.

    Returns:
        str: The path to the PowerPoint file.
    """
    return f"{base_dir}/pptx/{file_name}.pptx"
