import logging
import traceback
from typing import Any, Dict

import pandas as pd

from src.shared.llm import call_vision_model

from .prompts import build_prompt


def get_answers(
    df: pd.DataFrame,
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
        df (pd.DataFrame): The DataFrame containing the questions.
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

    result_data = [
        get_answer_single(
            row,
            model_name=model_name,
            provider=provider,
            temperature=temperature,
            max_tokens=max_tokens,
            json=json,
            timeout=timeout,
        )
        for _, row in df.iterrows()
    ]
    return pd.DataFrame(result_data)


def get_answer_single(
    row: pd.Series,
    model_name: str,
    provider: str,
    temperature: float,
    max_tokens: int,
    json: bool,
    timeout: int = 30,
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
        hash_value = row["hash"]
        task = row["task"]
        description = row["description"]
        image_data = row["image"]
        json_data = row["json_data"]
        ground_truth = row.get("ground_truth", "")

        # Extract image bytes from dictionary format
        image_bytes = (
            image_data["bytes"] if isinstance(image_data, dict) else image_data
        )

        prompt = build_prompt(description, json_data)
        llm_answer = call_vision_model(
            model_name=model_name,
            provider=provider,
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            images=image_bytes,  # Pass image bytes directly
            json=json,
            timeout=timeout,
        )

        return {
            "hash": hash_value,
            "task": task,
            "ground_truth": ground_truth,
            "llm_answer": llm_answer,
        }
    except Exception as e:
        logging.error(f"Error in get_answer_single: {str(e)}")
        traceback.print_exc()
        return {
            "hash": row["hash"],
            "ground_truth": row.get("ground_truth", ""),
            "llm_answer": str(e),
        }


if __name__ == "__main__":
    from src.shared.load_save_huggingface_dataset import (
        load_save_huggingface_dataset_df,
    )

    dataset_name = "tyrionhuu/PPTBench-Detection"
    dataset_path = "data/PPTBench-Detection"
    df = load_save_huggingface_dataset_df(
        dataset_name=dataset_name,
        dataset_path=dataset_path,
        force_download=False,
    )
    row = df.sample(random_state=1).iloc[0]
    # print(row)
    result = get_answer_single(
        row,
        model_name="gpt-4o",
        provider="api",
        temperature=0.1,
        max_tokens=3200,
        json=False,
        # timeout=30,
    )
    print(result)
