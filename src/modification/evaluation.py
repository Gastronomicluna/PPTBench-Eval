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
    Evaluate the answers in the DataFrame, both overall and by task.

    Args:
        answers_df (pd.DataFrame): The DataFrame containing the answers.

    Returns:
        pd.DataFrame: The DataFrame with evaluation metrics, including per-task
            metrics if task column exists.
    """
    if "is_correct" not in answers_df.columns:
        raise ValueError("The input DataFrame must contain 'is_correct' column.")

    # Calculate overall metrics
    overall_metrics = {
        "category": "overall",
        "accuracy": float(calculate_accuracy(answers_df)),
        "precision": float(calculate_precision(answers_df)),
        "recall": float(calculate_recall(answers_df)),
        "f1_score": float(calculate_f1_score(answers_df)),
    }

    # Calculate per-task metrics if task exists
    if "task" in answers_df.columns:
        task_metrics = []
        for task, group in answers_df.groupby("task"):
            metrics = {
                "category": task,
                "accuracy": float(calculate_accuracy(group)),
                "precision": float(calculate_precision(group)),
                "recall": float(calculate_recall(group)),
                "f1_score": float(calculate_f1_score(group)),
            }
            task_metrics.append(metrics)

        # Combine overall and task metrics
        evaluation_df = pd.DataFrame([overall_metrics] + task_metrics)
    else:
        evaluation_df = pd.DataFrame([overall_metrics])

    return evaluation_df
