import pandas as pd
from ...shared.utils import df_to_csv, csv_to_df
def add_subcategory_column(
    dataset_df: pd.DataFrame,
    csv_path: str,
) -> None:
    """
    Add a subcategory column to the DataFrame and save it to a CSV file.

    Args:
        dataset_df (pd.DataFrame): The DataFrame containing the dataset.
        csv_path (str): The path to save the DataFrame to as a CSV file.
    """
    df = csv_to_df(csv_path)
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