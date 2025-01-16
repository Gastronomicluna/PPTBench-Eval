import logging
import time
import traceback
from pathlib import Path
from typing import Any, Callable, Dict, Literal, Optional

import pandas as pd
from tqdm import tqdm

from ..shared.get_answer import get_answers
from ..shared.llm import call_vision_model
from ..shared.utils import df_to_csv, get_image_bytes, load_existing_answers
from .prompts import build_prompt


def get_answer_single(
    row: pd.Series,
    model_name: str,
    provider: str,
    temperature: float,
    max_tokens: int,
    json: bool,
    timeout: Optional[int] = None,
    retry: Optional[int] = None,
    pure_text: bool = False,
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
        pure_text (bool): If True, only use text data without images.

    Returns:
        Dict[str, Any]: Dictionary containing hash, ground_truth, and llm_answer.
    """
    attempts = 0
    max_attempts = retry if retry is not None else 0

    while attempts <= max_attempts:
        try:
            hash_value = row["hash"]
            task = row["task"]
            question = row["question"]
            options = row["options"]
            image_data = row["image"]
            json_content = row["json_content"]
            ground_truth = row["ground_truth"]

            # Extract image bytes from dictionary format
            image_bytes = get_image_bytes(image_data) if not pure_text else None

            prompt = build_prompt(
                question=question,
                options=options,
                slide_json=json_content,
            )

            kwargs = {
                "model_name": model_name,
                "provider": provider,
                "prompt": prompt,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "json": json,
            }
            if timeout is not None:
                kwargs["timeout"] = timeout
            if not pure_text:
                kwargs["images"] = image_bytes

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
                "category": row.get("category", ""),
                "task": row.get("task", ""),
                "ground_truth": row.get("ground_truth", ""),
                "llm_answer": str(e),
            }


def main() -> None:
    from src.shared.load_save_dataset import load_save_dataset_df

    tasks = [
        "chart understanding",
        "table understanding",
        "text understanding",
    ]
    target_task = tasks[1]
    dataset_name = "tyrionhuu/PPTBench-Understanding"
    dataset_path = "data/PPTBench-Understanding"
    csv_path = "data/" + target_task + " results.csv"

    df = load_save_dataset_df(
        dataset_name=dataset_name,
        dataset_path=dataset_path,
        force_download=False,
        source="huggingface",
    )

    df = df[df["task"] == target_task]
    sample_size = 20
    df = df.sample(sample_size, random_state=42)

    results_df = get_answers(
        get_answer_single=get_answer_single,
        df=df,
        model_name="llama3.2-vision:11b",
        provider="ollama",
        temperature=0.0,
        max_tokens=3200,
        json=True,
        timeout=60,
        csv_path=Path(csv_path),
        overwrite=True,
        pure_text=False,
    )
    print(results_df)


if __name__ == "__main__":
    main()
