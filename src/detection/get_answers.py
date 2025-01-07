import logging
from typing import Any, Dict

import dask.dataframe as dd
import pandas as pd

from src.shared.llm import call_vision_model

from .prompts import build_prompt


def get_answers(
    df: dd.DataFrame,
    model_name: str = "llama3.2-vision:11b",
    provider: str = "ollama",
    temperature: float = 0.1,
    max_tokens: int = 3200,
    json: bool = False,
    timeout: int = 30,
) -> pd.DataFrame:
    """
    Get answers to the questions in the DataFrame.

    Args:
        df (dd.DataFrame): The DataFrame containing the questions.
        model_name (str): Name of the model to use.
        provider (str): Provider of the model (ollama, api, etc.).
        temperature (float): Sampling temperature.
        max_tokens (int): Maximum tokens in response.
        json (bool): Whether to return JSON format.
        timeout (int): Request timeout in seconds.

    Returns:
        pd.DataFrame: The DataFrame with the answers.
    """
    if "hash" not in df.columns:
        raise ValueError("The input DataFrame must contain a 'hash' column.")

    pandas_df = df.compute()
    
    result_data = [
        get_answer_single(
            row,
            model_name=model_name,
            provider=provider,
            temperature=temperature,
            max_tokens=max_tokens,
            json=json,
            timeout=timeout
        ) for _, row in pandas_df.iterrows()
    ]
    return pd.DataFrame(result_data)


def get_answer_single(
    row: pd.Series,
    model_name: str,
    provider: str,
    temperature: float,
    max_tokens: int,
    json: bool,
    timeout: int,
) -> Dict[str, Any]:
    """
    Get the answer to a single description and return the result.

    Args:
        row (pd.Series): The row containing the description and image data.
        model_name (str): Name of the model to use.
        provider (str): Provider of the model.
        temperature (float): Sampling temperature.
        max_tokens (int): Maximum tokens in response.
        json (bool): Whether to return JSON format.
        timeout (int): Request timeout in seconds.

    Returns:
        Dict[str, Any]: Dictionary containing hash, ground_truth, and llm_answer.
    """
    try:
        hash_value = row['hash']
        description = row['description']
        image_path = row['image_path']
        json_content = row['json_content']
        ground_truth = row.get('ground_truth', '')
        
        prompt = build_prompt(description, json_content)
        llm_answer = call_vision_model(
            model_name=model_name,
            provider=provider,
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            image_paths=image_path,
            json=json,
            timeout=timeout
        )

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
