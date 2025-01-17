import logging
import time
import traceback
from typing import Any, Dict, Optional

import pandas as pd

from ..shared.get_answer import get_answers
from ..shared.llm import call_vision_model
from ..shared.utils import get_image_bytes
from .prompts import build_prompt


def get_answer_single_modification(
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
            subcategory = row["subcategory"]
            task = row["task"]
            description = row["description"]
            image_data = row["image"]
            shape_to_modify = row["shape_to_modify"]
            json_data = row["json_data"]
            ground_truth = row["ground_truth"]

            image_bytes = get_image_bytes(image_data) if not pure_text else None

            prompt = build_prompt(
                query=description,
                slide_json=json_data,
                subcategory=subcategory,
                shape_to_modify=shape_to_modify,
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
                "subcategory": subcategory,
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
                "hash": hash_value,
                "subcategory": subcategory,
                "task": task,
                "ground_truth": ground_truth,
                "llm_answer": f"Timeout occurred after {max_attempts} attempts",
            }
        except Exception as e:
            logging.error(f"Error occurred: {str(e)}")
            logging.error(traceback.format_exc())
            return {
                "hash": hash_value,
                "subcategory": subcategory,
                "task": task,
                "ground_truth": ground_truth,
                "llm_answer": str(e),
            }


def main() -> None:
    from pathlib import Path

    from src.shared.load_save_dataset import load_save_dataset_df

    dataset_name = "tyrionhuu/PPTBench-Modification"
    dataset_path = "data/PPTBench-Modification"
    csv_path = "data/" + "modification_results.csv"

    df = load_save_dataset_df(
        dataset_name=dataset_name,
        dataset_path=dataset_path,
        force_download=False,
        source="huggingface",
    )

    sample_size = 10
    df = df.sample(sample_size, random_state=42)

    results = get_answers(
        get_answer_single=get_answer_single_modification,
        df=df,
        model_name="gpt-4o",
        provider="api",
        temperature=0.0,
        max_tokens=3200,
        json=True,
        timeout=60,
        csv_path=Path(csv_path),
        overwrite=True,
        pure_text=False,
    )
    print(results)


if __name__ == "__main__":
    main()
