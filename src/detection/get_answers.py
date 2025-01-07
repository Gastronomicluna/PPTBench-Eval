import logging
from typing import Any, Dict, List

import dask.dataframe as dd
import pandas as pd

from src.shared.llm import call_vision_model, generate_api_messages

from .prompts import build_prompt


def get_answers(
    df: dd.DataFrame,
) -> pd.DataFrame:
    """
    Get answers to the questions in the DataFrame.

    Args:
        df (dd.DataFrame): The DataFrame containing the questions.

    Returns:
        pd.DataFrame: The DataFrame with the answers.
    """
    if "hash" not in df.columns:
        raise ValueError("The input DataFrame must contain a 'hash' column.")

    # Convert Dask DataFrame to Pandas for iteration
    pandas_df = df.compute()
    
    result_data = [get_answer_single(row) for _, row in pandas_df.iterrows()]
    return pd.DataFrame(result_data)


def get_answer_single(row: pd.Series) -> Dict[str, Any]:
    """
    Get the answer to a single question and return the result.

    Args:
        row (pd.Series): The row containing the question and image data.

    Returns:
        Dict[str, Any]: Dictionary containing hash, ground_truth, and llm_answer.
    """
    try:
        hash_value = row['hash']
        question = row['question']
        image_path = row['image_path']
        ground_truth = row.get('ground_truth', '')

        messages = generate_api_messages([image_path], question)
        llm_answer = call_vision_model(messages)

        return {
            'hash': hash_value,
            'ground_truth': ground_truth,
            'llm_answer': llm_answer
        }
    except Exception as e:
        logging.error(f"Error in get_answer_single: {str(e)}")
        return {
            'hash': row['hash'],
            'ground_truth': row.get('ground_truth', ''),
            'llm_answer': str(e)
        }
