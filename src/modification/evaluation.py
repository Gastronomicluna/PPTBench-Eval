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
    Excludes rows where llm_answer is None.

    Args:
        answers_df (pd.DataFrame): The DataFrame containing the answers.

    Returns:
        pd.DataFrame: The DataFrame with evaluation metrics, including per-task
            metrics if task column exists.
    """
    if "is_correct" not in answers_df.columns:
        raise ValueError("The input DataFrame must contain 'is_correct' column.")

    # Filter out timed out requests
    valid_df = answers_df[answers_df["llm_answer"].notnull()].copy()

    # Calculate overall metrics
    overall_metrics = {
        "category": "overall",
        "accuracy": float(calculate_accuracy(valid_df)),
        "precision": float(calculate_precision(valid_df)),
        "recall": float(calculate_recall(valid_df)),
        "f1_score": float(calculate_f1_score(valid_df)),
    }

    # Calculate per-task metrics if task exists
    if "task" in valid_df.columns:
        task_metrics = []
        for task, group in valid_df.groupby("task"):
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
