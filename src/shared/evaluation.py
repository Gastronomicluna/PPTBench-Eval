import pandas as pd





def calculate_accuracy(
    answers_df: pd.DataFrame,
) -> float:
    """
    Calculate the accuracy of the answers in the DataFrame.

    Args:
        answers_df (pd.DataFrame): The DataFrame containing the answers.

    Returns:
        float: The accuracy of the answers.
    """
    if "is_correct" not in answers_df.columns:
        raise ValueError("The input DataFrame must contain 'is_correct' column.")

    correct_count = answers_df["is_correct"].sum()
    total_count = len(answers_df)
    accuracy = correct_count / total_count if total_count > 0 else 0.0
    return accuracy


def calculate_precision(
    answers_df: pd.DataFrame,
) -> float:
    """
    Calculate the precision of the answers in the DataFrame.

    Args:
        answers_df (pd.DataFrame): The DataFrame containing the answers.

    Returns:
        float: The precision of the answers.
    """
    if "is_correct" not in answers_df.columns:
        raise ValueError("The input DataFrame must contain 'is_correct' column.")

    true_positive = answers_df["is_correct"].sum()
    false_positive = len(answers_df) - true_positive
    precision = (
        true_positive / (true_positive + false_positive)
        if (true_positive + false_positive) > 0
        else 0.0
    )
    return precision


def calculate_recall(
    answers_df: pd.DataFrame,
) -> float:
    """
    Calculate the recall of the answers in the DataFrame.

    Args:
        answers_df (pd.DataFrame): The DataFrame containing the answers.

    Returns:
        float: The recall of the answers.
    """
    if "is_correct" not in answers_df.columns:
        raise ValueError("The input DataFrame must contain 'is_correct' column.")

    true_positive = answers_df["is_correct"].sum()
    false_negative = len(answers_df) - true_positive
    recall = (
        true_positive / (true_positive + false_negative)
        if (true_positive + false_negative) > 0
        else 0.0
    )
    return recall


def calculate_f1_score(
    answers_df: pd.DataFrame,
) -> float:
    """
    Calculate the F1 score of the answers in the DataFrame.

    Args:
        answers_df (pd.DataFrame): The DataFrame containing the answers.

    Returns:
        float: The F1 score of the answers.
    """
    precision = calculate_precision(answers_df)
    recall = calculate_recall(answers_df)

    f1_score = (
        2 * (precision * recall) / (precision + recall)
        if (precision + recall) > 0
        else 0.0
    )
    return f1_score
