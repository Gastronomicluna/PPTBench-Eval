import logging
import time
import traceback
from typing import Any, Dict, Optional

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
    timeout: Optional[int] = None,
    retry: Optional[int] = None,
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
        timeout (Optional[int]): Request timeout in seconds. None for no timeout.
        retry (Optional[int]): Number of retries on timeout. None for no retries.

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
            retry=retry,
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
    timeout: Optional[int] = None,
    retry: Optional[int] = None,
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
        timeout (Optional[int]): Request timeout in seconds. None for no timeout.
        retry (Optional[int]): Number of retries on timeout. None for no retries.

    Returns:
        Dict[str, Any]: Dictionary containing hash, ground_truth, and llm_answer.
    """
    attempts = 0
    max_attempts = retry if retry is not None else 0

    while attempts <= max_attempts:
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
            kwargs = {
                "model_name": model_name,
                "provider": provider,
                "prompt": prompt,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "images": image_bytes,
                "json": json,
            }
            if timeout is not None:
                kwargs["timeout"] = timeout

            llm_answer = call_vision_model(**kwargs)

            return {
                "hash": hash_value,
                "task": task,
                "ground_truth": ground_truth,
                "llm_answer": llm_answer,
            }
        except TimeoutError as e:
            attempts += 1
            if attempts <= max_attempts:
                logging.warning(
                    f"Timeout occurred, attempt {attempts} of {max_attempts}"
                )
                time.sleep(1)  # Add a small delay between retries
                continue
            logging.error(f"All retry attempts failed: {str(e)}")
            return {
                "hash": row["hash"],
                "ground_truth": row.get("ground_truth", ""),
                "llm_answer": f"Timeout error after {max_attempts} attempts: {str(e)}",
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
