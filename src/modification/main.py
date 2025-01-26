import concurrent.futures
import logging
import os
import time
from datetime import datetime
from typing import Dict

import pandas as pd

from ..shared.format_answers_api import format_answer_csv
from ..shared.llm import API_LLM_MODELS
from ..shared.load_save_dataset import load_save_dataset_df
from ..shared.utils import download_kaggle_dataset, get_project_root, process_model
from .evaluation import evaluate_answers
from .get_answers import get_answers_modification
from .judge import judge_answer_df


def main(
    max_workers: int = 4,
    ollama_mode: bool = True,
    test_mode: bool = False,
    job_delay: float = 0.5,
) -> None:
    """Main entry point for the detection pipeline.

    This function sets up the environment, loads the dataset,
    and processes, evaluates, and saves detection results.

    Args:
        max_workers: Maximum number of concurrent workers for parallel processing.
            Defaults to 4.
        ollama_mode: Whether to only run OLLAMA models. Defaults to True.
        test_mode: Whether to run in test mode. Defaults to False.
        job_delay: Delay between job submissions in seconds. Defaults to 1.0.

    Returns:
        None
    """
    project_root = get_project_root()

    # Set up logging first thing
    log_dir = project_root / "log"
    os.makedirs(log_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"modification_{timestamp}.log"

    # Configure file handler for all logs
    file_handler = logging.FileHandler(log_file, mode="w", encoding="utf-8")
    file_handler.setLevel(logging.INFO)

    # Configure stream handler for errors only
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.ERROR)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[file_handler, console_handler],
        force=True,
    )

    dataset_name = "tyrionhuu/PPTBench-Modification"
    dataset_path = "data/PPTBench-Modification"

    # Update results_dir to be relative to project root
    results_dir = project_root / "data" / "modification_results"

    os.makedirs(results_dir, exist_ok=True)

    print("Loading dataset from Hugging Face...")
    df = load_save_dataset_df(
        dataset_name=dataset_name,
        dataset_path=dataset_path,
        # force_download=True,
        source="huggingface",
    )

    print("Downloading JSON dataset from Kaggle...")
    download_kaggle_dataset(
        dataset_name="PPTBench-JSON",
        destination_dir="dataset",
        new_dir_name="json",
    )

    # Test mode
    if test_mode:
        df = df[df["task"] == "add_shape"]
        df = df.sample(10, random_state=42)

    print(f"Dataset shape: {df.shape}")

    if ollama_mode:
        models_to_run = [
            (provider, model_name)
            for provider, model_name in API_LLM_MODELS
            if provider == "ollama"
        ]
    else:
        models_to_run = API_LLM_MODELS

    if not models_to_run:
        print("No models to run. Exiting.")
        return

    print("Generating answers...")

    results: Dict[str, pd.DataFrame] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {}
        for provider, model_name in models_to_run:
            futures[
                executor.submit(
                    process_model,
                    function=get_answers_modification,
                    df=df,
                    model_name=model_name,
                    provider=provider,
                    temperature=0.0,
                    max_tokens=2048,
                    json_mode=True,
                    timeout=60,
                    csv_path=results_dir / f"{model_name}.csv",
                    # overwrite=True,
                )
            ] = (model_name, provider)
            time.sleep(job_delay)  # Add delay between job submissions

        for future in concurrent.futures.as_completed(futures):
            _, model_name = futures[future]
            try:
                result = future.result()
                if result is not None:
                    results[model_name] = result
                else:
                    logging.error(f"Failed to process {model_name} after retries")
            except Exception as e:
                logging.error(f"Error processing {model_name}: {str(e)}")

    print("Formatting answers...")

    for _, model_name in models_to_run:
        csv_path = results_dir / f"{model_name}.csv"
        if csv_path.exists():
            results_df = format_answer_csv(
                csv_path=csv_path,
                overwrite=True,
            )
            print(f"Formatted {len(results_df)} entries for {model_name}")
        else:
            logging.warning(f"Results file not found for {model_name}")

    print("Judging answers...")

    for _, model_name in models_to_run:
        results_df = judge_answer_df(
            csv_path=results_dir / f"{model_name}.csv",
            overwrite=True,
        )
        print(f"Judged {len(results_df)} entries")

    print("Evaluating answers...")

    evaluation_results = []
    for _, model_name in models_to_run:
        judged_df = pd.read_csv(results_dir / f"{model_name}.csv")
        eval_df = evaluate_answers(judged_df)
        eval_df["model"] = model_name
        evaluation_results.append(eval_df)

    combined_results = pd.concat(evaluation_results, ignore_index=True)
    combined_results.to_csv(results_dir / "combined_evaluation.csv", index=False)
    print("Pipeline completed successfully.")


if __name__ == "__main__":
    main(
        max_workers=4,
        ollama_mode=False,
        test_mode=True,
        job_delay=0.5,
    )
