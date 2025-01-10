import pandas as pd

from ..shared.evaluation import (
    calculate_accuracy,
    calculate_f1_score,
    calculate_precision,
    calculate_recall,
)


def evaluate_answers(
    answers_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Evaluate the answers in the DataFrame, both overall and by subcategory.

    Args:
        answers_df (pd.DataFrame): The DataFrame containing the answers.

    Returns:
        pd.DataFrame: The DataFrame with evaluation metrics, including per-subcategory
            metrics if subcategory column exists.
    """
    if "is_correct" not in answers_df.columns:
        raise ValueError("The input DataFrame must contain 'is_correct' column.")

    # Calculate overall metrics
    overall_metrics = {
        "category": ["overall"],
        "accuracy": [calculate_accuracy(answers_df)],
        "precision": [calculate_precision(answers_df)],
        "recall": [calculate_recall(answers_df)],
        "f1_score": [calculate_f1_score(answers_df)],
    }

    # Calculate per-subcategory metrics if subcategory exists
    if "subcategory" in answers_df.columns:
        subcategory_metrics = []
        for subcategory, group in answers_df.groupby("subcategory"):
            metrics = {
                "category": subcategory,
                "accuracy": calculate_accuracy(group),
                "precision": calculate_precision(group),
                "recall": calculate_recall(group),
                "f1_score": calculate_f1_score(group),
            }
            subcategory_metrics.append(metrics)
        
        # Combine overall and subcategory metrics
        evaluation_df = pd.DataFrame(
            [overall_metrics] + subcategory_metrics
        ).explode("category")
    else:
        evaluation_df = pd.DataFrame(overall_metrics)

    return evaluation_df
