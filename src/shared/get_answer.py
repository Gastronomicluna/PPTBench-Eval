import logging
from pathlib import Path
from typing import Callable, Literal, Optional

import pandas as pd
from tqdm import tqdm

from .utils import df_to_csv, load_existing_answers


def get_answers(
    get_answer_single: Callable,
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
    pure_text: bool = False,
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
        pure_text (bool): If True, only use text data without images.

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
                pure_text=pure_text,
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
