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
    Evaluate the answers in the DataFrame.

    Args:
        answers_df (pd.DataFrame): The DataFrame containing the answers.

    Returns:
        pd.DataFrame: The DataFrame with evaluation metrics.
    """
    if "is_correct" not in answers_df.columns:
        raise ValueError("The input DataFrame must contain 'is_correct' column.")

    accuracy = calculate_accuracy(answers_df)
    precision = calculate_precision(answers_df)
    recall = calculate_recall(answers_df)
    f1_score = calculate_f1_score(answers_df)

    evaluation_metrics = {
        "accuracy": [accuracy],
        "precision": [precision],
        "recall": [recall],
        "f1_score": [f1_score],
    }

    evaluation_df = pd.DataFrame(evaluation_metrics)
    return evaluation_df
