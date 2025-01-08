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