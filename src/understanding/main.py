import concurrent.futures
import logging
import os
import time
from datetime import datetime
from typing import Dict, Optional

import pandas as pd

from .format_answers import format_answer_csv
from ..shared.llm import API_LLM_MODELS
from ..shared.load_save_dataset import load_save_dataset_df
from ..shared.utils import get_project_root, process_model
from .evaluation import evaluate_answers
from .get_answers_understanding import get_answers_understanding
from .judge import judge_answer_df


def main(
    max_workers: int = 4,
    ollama_mode: bool = True,
    test_mode: bool = False,
    target_task: Optional[str] = "table understanding",
    job_delay: float = 0.5,
) -> None:
    project_root = get_project_root()

    # Set up logging first thing
    log_dir = project_root / "log"
    os.makedirs(log_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"understanding_{timestamp}.log"

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

    dataset_name = "tyrionhuu/PPTBench-Understanding"
    dataset_path = "data/PPTBench-Understanding"
    results_dir = project_root / "data" / "understanding_results"
    os.makedirs(results_dir, exist_ok=True)

    print("Loading dataset...")
    df = load_save_dataset_df(
        dataset_name=dataset_name,
        dataset_path=dataset_path,
        force_download=True,
        source="huggingface",
    )

    # Filter for specific task

    if test_mode:
        df = df[df["task"] == target_task]
        sample_size = 20
        df = df.sample(sample_size, random_state=42)

    if ollama_mode:
        models_to_run = [
            (provider, model_name)
            for provider, model_name in API_LLM_MODELS
            if provider == "ollama"
        ]
    else:
        models_to_run = API_LLM_MODELS

    if not models_to_run:
        print("No models configured to run")
        return

    print("Generating answers...")
    results: Dict[str, pd.DataFrame] = {}

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {}
        for provider, model_name in models_to_run:
            futures[
                executor.submit(
                    process_model,
                    function=get_answers_understanding,
                    df=df,
                    model_name=model_name,
                    provider=provider,
                    temperature=0.0,
                    max_tokens=2048,
                    json_mode=True,
                    timeout=60,
                    csv_path=results_dir / f"{model_name.replace('.', '-')}.csv",
                    overwrite=True,
                )
            ] = (provider, model_name)
            time.sleep(job_delay)  # Add delay between job submissions

        for future in concurrent.futures.as_completed(futures):
            _, model_name = futures[future]
            try:
                results[model_name] = future.result()
            except Exception as e:
                logging.error(f"Model {model_name} failed: {str(e)}")

    print("Formatting answers...")

    # for _, model_name in models_to_run:
    #     csv_path = results_dir / f"{model_name.replace('.', '-')}.csv"
    #     if csv_path.exists():
    #         results_df = format_answer_csv(
    #             csv_path=csv_path,
    #             overwrite=True,
    #         )
    #         print(f"Formatted {len(results_df)} entries")
    #     else:
    #         logging.warning(f"Results file not found for {model_name}")

    print("Judging answers...")

    # Judge answers and save to CSV
    # for _, model_name in models_to_run:
    #     results_df = judge_answer_df(
    #         csv_path=results_dir / f"{model_name.replace('.', '-')}.csv",
    #         overwrite=True,
    #     )
    #     print(f"Judged {len(results_df)} entries")

    print("Evaluating answers...")

    # Evaluate answers and combine results
    # evaluation_results = []
    # for _, model_name in models_to_run:
    #     judged_df = pd.read_csv(results_dir / f"{model_name.replace('.', '-')}.csv")
    #     eval_df = evaluate_answers(judged_df)
    #     eval_df["model"] = model_name
    #     evaluation_results.append(eval_df)

    # Combine all results and save
    # combined_results = pd.concat(evaluation_results, ignore_index=True)
    # combined_results.to_csv(results_dir / "evaluation_results.csv", index=False)

    print("Evaluation complete. Results saved to evaluation_results.csv")
    print("Pipeline completed successfully.")


if __name__ == "__main__":
    main(
        max_workers=4,
        ollama_mode=True,
        test_mode=False,
        # target_task="table understanding",
        job_delay=0.5,
    )
