import logging
import time
import traceback
from typing import Any, Dict, Optional
from pathlib import Path

import pandas as pd

from src.shared.llm import call_vision_model

from .prompts import build_prompt

def load_existing_answers(csv_path: Path) -> Dict[str, Dict[str, Any]]:
    """
    Load existing answers from CSV file.

    Args:
        csv_path (Path): Path to the CSV file.

    Returns:
        Dict[str, Dict[str, Any]]: Dictionary of existing answers keyed by hash.
    """
    if not csv_path.exists():
        return {}
    
    df = pd.read_csv(csv_path)
    return {row["hash"]: row.to_dict() for _, row in df.iterrows()}

def get_answers(
    df: pd.DataFrame,
    model_name: str = "llama3.2-vision:11b",
    provider: str = "ollama",
    temperature: float = 0.1,
    max_tokens: int = 3200,
    json: bool = False,
    timeout: Optional[int] = None,
    retry: Optional[int] = None,
    csv_path: Optional[Path] = None,
    overwrite: bool = False,
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
        csv_path (Optional[Path]): Path to save/load results. If provided, 
            will skip existing entries and save new results incrementally.
        overwrite (bool): If True, overwrites existing entries in CSV.
            If False, skips existing entries. Defaults to False.

    Returns:
        pd.DataFrame: The DataFrame with the answers.
    """
    if "hash" not in df.columns:
        raise ValueError("The input DataFrame must contain a 'hash' column.")

    # Handle CSV file setup
    if csv_path and csv_path.exists() and overwrite:
        csv_path.unlink()  # Delete existing file if overwrite is True
    
    # Load existing results if csv_path provided and not overwriting
    existing_answers = (
        load_existing_answers(csv_path) 
        if csv_path and not overwrite 
        else {}
    )
    result_data = []

    for _, row in df.iterrows():
        hash_value = row["hash"]
        if not overwrite and hash_value in existing_answers:
            result_data.append(existing_answers[hash_value])
            continue

        result = get_answer_single(
            row,
            model_name=model_name,
            provider=provider,
            temperature=temperature,
            max_tokens=max_tokens,
            json=json,
            timeout=timeout,
            retry=retry,
        )
        result_data.append(result)

        # Save incrementally if csv_path provided
        if csv_path:
            pd.DataFrame([result]).to_csv(
                csv_path,
                mode='a',
                header=not csv_path.exists(),
                index=False
            )

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
                "task": row.get("task", ""),
                "ground_truth": row.get("ground_truth", ""),
                "llm_answer": str(e),
                "subcategory": row.get("subcategory", ""),
            }


if __name__ == "__main__":
    from src.shared.load_save_huggingface_dataset import (
        load_save_huggingface_dataset_df,
    )

    dataset_name = "tyrionhuu/PPTBench-Detection"
    dataset_path = "data/PPTBench-Detection"
    csv_path = Path("data/detection_results.csv")
    
    df = load_save_huggingface_dataset_df(
        dataset_name=dataset_name,
        dataset_path=dataset_path,
        force_download=False,
    )
    sampled_df = df.sample(n=2, random_state=42)
    
    results = get_answers(
        sampled_df,
        model_name="gpt-4o",
        provider="api",
        temperature=0.1,
        max_tokens=3200,
        json=False,
        csv_path=csv_path,
        overwrite=True,
    )
    
    print(results)
    
    # results = get_answers(
    #     df,
    #     model_name="gpt-4o",
    #     provider="api",
    #     temperature=0.1,
    #     max_tokens=3200,
    #     json=False,
    #     csv_path=csv_path,
    #     overwrite=True,  # Set to True to rewrite existing results
    # )
    # print(f"Processed {len(results)} entries")
