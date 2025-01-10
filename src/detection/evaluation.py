from pathlib import Path
import pandas as pd
from ..shared.utils import csv_to_df, df_to_csv
from ..shared.evaluation import evaluate_answers

def evaluation_answer_df(
    csv_path: Path,
    overwrite: bool = False,
) -> pd.DataFrame:
    """
    Evaluate the answers in the CSV file and save results back to the same file.

    Args:
        csv_path (Path): Path to CSV file for input and output.
        overwrite (bool): Whether to overwrite existing output file.

    Returns:
        pd.DataFrame: DataFrame with evaluated answers.
    """
    csv_path = Path(csv_path)
    answers_df = csv_to_df(csv_path)

    if answers_df is None:
        raise ValueError("The input DataFrame is empty.")
    
    evaluation_df = evaluate_answers(answers_df)
    
    if overwrite:
        df_to_csv(evaluation_df, csv_path)
        
    return evaluation_df