import pandas as pd
from ...shared.utils import df_to_csv, csv_to_df
import os
from pathlib import Path

def add_subcategory_column(
    dataset_df: pd.DataFrame,
    csv_path: str | Path,
) -> None:
    """
    Add a subcategory column to the DataFrame and save it to a CSV file.

    Args:
        dataset_df (pd.DataFrame): The DataFrame containing the dataset.
        csv_path (str | Path): The path to save the DataFrame to as a CSV file.
    """
    path = Path(csv_path)
    df = csv_to_df(path)
    if df is None:
        raise ValueError("The CSV file is empty.")

    if "subcategory" in df.columns:
        return

    original_df = dataset_df.copy()
    df["subcategory"] = original_df.apply(
        lambda row: get_subcategory(row),
        axis=1,
    )
    df_to_csv(df, csv_path)
    return

def get_subcategory(
    row: pd.Series,
) -> str:
    """
    Get the subcategory for the answer.

    Args:
        row (pd.Series): The row containing the answer.

    Returns:
        str: The subcategory of the answer.
    """
    subcategory = row["subcategory"]
    if subcategory == "content extraction":
        return "content extraction"
    elif subcategory == "layout detection":
        return "layout detection"
    elif subcategory == "style detection":
        return "style detection"
    else:
        raise ValueError(f"Unknown subcategory: {subcategory}")
    
    
def main() -> None:
    from src.shared.load_save_dataset import load_save_dataset_df
    
    original_dataset_name = "tyrionhuu/PPTBench-Detection"
    original_dataset_path = "data/PPTBench-Detection"
    csv_dir = Path("data/detection_results")
    
    df = load_save_dataset_df(
        dataset_name=original_dataset_name,
        dataset_path=original_dataset_path,
        force_download=False,
        source="huggingface",
    )
    
    for file in os.listdir(csv_dir):
        csv_path = csv_dir / file
        add_subcategory_column(df, csv_path)
    
    
if __name__ == "__main__":
    main()