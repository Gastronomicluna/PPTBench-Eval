import concurrent.futures
import logging
import os
from datetime import datetime
from typing import Dict

import pandas as pd

from ..shared.format_answers_api import format_answer_csv
from ..shared.llm import API_LLM_MODELS
from ..shared.load_save_dataset import load_save_dataset_df
from ..shared.utils import (  # download_kaggle_dataset,
    get_project_root,
    handle_rate_limit,
    process_model,
)
from .generate_pptx import generate_pptx_files_csv
from .get_answers import get_answers_generation


def main(
    max_workers: int = 4,
    ollama_mode: bool = True,
    test_mode: bool = False,
) -> None:
    """Main entry point for the detection pipeline.

    This function sets up the environment, loads the dataset,
    and processes, evaluates, and saves detection results.

    Args:
        max_workers: Maximum number of concurrent workers for parallel processing.
            Defaults to 4.
        ollama_mode: Whether to only run OLLAMA models. Defaults to True.
        test_mode: Whether to run in test mode. Defaults to False.

    Returns:
        None
    """
    project_root = get_project_root()

    # Set up logging first thing
    log_dir = project_root / "log"
    os.makedirs(log_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"generation_{timestamp}.log"

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

    dataset_name = "tyrionhuu/PPTBench-Generation"
    dataset_path = "data/PPTBench-Generation"
    dataset_base_dir = "datasets"
    # Update results_dir to be relative to project root
    results_dir = project_root / "data" / "generation_results"
    base_dir = project_root / dataset_base_dir / "pptx"
    os.makedirs(results_dir, exist_ok=True)

    print("Loading dataset...")
    df = load_save_dataset_df(
        dataset_name=dataset_name,
        dataset_path=dataset_path,
        force_download=False,
        source="huggingface",
    )

    print("Downloading Extracted Images from Kaggle...")
    # download_kaggle_dataset(
    #     dataset_name="PPTBench-Images",
    #     dataset_path="data",
    #     new_dir_name="images",
    # )

    # Test mode
    if test_mode:
        df = df[df["task"] == "text_to_slide"]

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
        future_to_model = {
            executor.submit(
                handle_rate_limit,
                process_model,
                function=get_answers_generation,
                df=df,
                model_name=model_name,
                provider=provider,
                temperature=0.0,
                max_tokens=2048,
                json=True,
                timeout=60,
                csv_path=results_dir / f"{model_name}.csv",
                overwrite=True,
                max_retries=3,
                initial_delay=2.0,
            ): (provider, model_name)
            for provider, model_name in models_to_run
        }

        for future in concurrent.futures.as_completed(future_to_model):
            _, model_name = future_to_model[future]
            try:
                results[model_name] = future.result()
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
            print(f"Formatted {len(results_df)} entries")
        else:
            logging.warning(f"Results file not found for {model_name}")

    print("Generating PPTX files...")
    for _, model_name in models_to_run:
        csv_path = results_dir / f"{model_name}.csv"
        if csv_path.exists():
            generate_pptx_files_csv(
                csv_path=csv_path,
                base_dir=base_dir,
                overwrite=True,
            )
            print(f"Generated PPTX files for {model_name}")
        else:
            logging.warning(f"Results file not found for {model_name}")

    print("Judging answers...")
    pass
    print("Evaluating answers...")
    pass
    print("Pipeline completed successfully.")


if __name__ == "__main__":
    main(
        max_workers=4,
        ollama_mode=True,
        test_mode=False,
    )
