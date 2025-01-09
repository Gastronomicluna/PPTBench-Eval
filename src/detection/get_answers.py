import logging
import time
import traceback
from pathlib import Path
from typing import Any, Dict, Literal, Optional

import pandas as pd
from tqdm import tqdm

from src.shared.llm import call_vision_model

from .prompts import build_prompt
from .utils import csv_to_df, df_to_csv


def load_existing_answers(csv_path: Path) -> Dict[str, Dict[str, Any]]:
    """
    Load existing answers from CSV file using the utility function.

    Args:
        csv_path (Path): Path to the CSV file.

    Returns:
        Dict[str, Dict[str, Any]]: Dictionary of existing answers keyed by hash.
    """
    df = csv_to_df(csv_path)
    if df is None:
        return {}

    return {row["hash"]: row.to_dict() for _, row in df.iterrows()}


def get_image_bytes(image_data: dict | bytes) -> bytes:
    """Extract image bytes from dataset row.

    Args:
        image_data: Image data from dataset row, either dict or bytes

    Returns:
        bytes: Raw image bytes
    """
    if isinstance(image_data, dict):
        return image_data["bytes"]
    return image_data


def get_answers(
    df: pd.DataFrame,
    model_name: str = "llama3.2-vision:11b",
    provider: Literal["api", "ollama", "openai", "anthropic"] = "ollama",
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
        load_existing_answers(csv_path) if csv_path and not overwrite else {}
    )
    result_data = []
    total = len(df)

    # Add progress bar with model name in description
    with tqdm(total=total, desc=f"Processing with {model_name}") as pbar:
        for _, row in df.iterrows():
            hash_value = row["hash"]
            if not overwrite and hash_value in existing_answers:
                result_data.append(existing_answers[hash_value])
                pbar.update(1)
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
                try:
                    # Convert newlines to literal \n in the text
                    safe_result = {
                        k: str(v).replace("\n", "\\n") if isinstance(v, str) else v
                        for k, v in result.items()
                    }
                    success = df_to_csv(
                        pd.DataFrame([safe_result]),
                        csv_path,
                        mode="a",
                    )
                    if not success:
                        logging.warning(f"Failed to save result for hash {hash_value}")
                except Exception as e:
                    logging.error(f"Error preparing data for CSV: {str(e)}")

            pbar.update(1)

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
            subcategory = row["subcategory"]
            task = row["task"]
            description = row["description"]
            image_data = row["image"]
            json_data = row["json_data"]
            ground_truth = row.get("ground_truth", "")

            # Extract image bytes from dictionary format
            image_bytes = get_image_bytes(image_data)

            prompt = build_prompt(
                query=description,
                subcategory=subcategory,
                slide_json=json_data,
            )

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
                "category": row.get("category", ""),
                "subcategory": row.get("subcategory", ""),
                "ground_truth": row.get("ground_truth", ""),
                "llm_answer": str(e),
            }


def main() -> None:
    from src.shared.load_save_dataset import load_save_dataset_df
    target_subcategories = [
        "content extraction",
        "layout detection",
        "style detection",
    ]
    target_subcategory = target_subcategories[1]
    dataset_name = "tyrionhuu/PPTBench-Detection"
    dataset_path = "data/PPTBench-Detection"
    csv_path = "data/" + target_subcategory + " results.csv"

    df = load_save_dataset_df(
        dataset_name=dataset_name,
        dataset_path=dataset_path,
        force_download=False,
        source="huggingface",
    )

    df = df[df["subcategory"] == target_subcategory]

    results_df = get_answers(
        df=df,
        model_name="llama3.2-vision:11b",
        provider="ollama",
        temperature=0.0,
        max_tokens=3200,
        json=False,
        timeout=60,
        csv_path=Path(csv_path),
        overwrite=True,
    )
    print(results_df)


if __name__ == "__main__":
    main()
