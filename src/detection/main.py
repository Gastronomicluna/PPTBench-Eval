import logging
import os
from pathlib import Path

import pandas as pd

from ..shared.evaluation import evaluate_answers
from ..detection.get_answers import get_answers
from ..detection.judge import judge_answer_df
from ..shared.llm import API_LLM_MODELS
from ..shared.load_save_dataset import load_save_dataset_df

logging.basicConfig(level=logging.INFO)


def get_project_root() -> Path:
    """Get the absolute path to the project root directory.

    Returns:
        Path: Absolute path to the project root directory.
    """
    current_file = Path(__file__).resolve()
    return current_file.parent.parent.parent


def main() -> None:
    """Main entry point for the detection pipeline.

    This function sets up the environment, loads the dataset,
    and processes, evaluates, and saves detection results.
    """
    ollama_mode = True
    test_mode = True
    non_magic_mode = False
    dataset_name = "tyrionhuu/PPTBench-Detection"
    dataset_path = "data/PPTBench-Detection"

    # Update results_dir to be relative to project root
    project_root = get_project_root()
    results_dir = project_root / "data" / "detection_results"

    os.makedirs(results_dir, exist_ok=True)

    if non_magic_mode:
        df = load_save_dataset_df(
            dataset_name=dataset_name,
            dataset_path=dataset_path,
            force_download=False,
            source="modelscope",
        )
    else:
        df = load_save_dataset_df(
            dataset_name=dataset_name,
            dataset_path=dataset_path,
            force_download=False,
            source="huggingface",
        )

    # only get category == "content extraction"
    if test_mode:
        df = df[df["subcategory"] == "content extraction"]

    # print(df.head())
    if ollama_mode:
        models_to_run = [
            (provider, model_name)
            for provider, model_name in API_LLM_MODELS
            if provider == "ollama"
        ]
    else:
        models_to_run = API_LLM_MODELS

    logging.info("Generating answers...")

    for provider, model_name in models_to_run:
        print(f"Processing {model_name}...")
        results_df = get_answers(
            df=df,
            model_name=model_name,
            provider=provider,
            temperature=0.0,
            max_tokens=3200,
            json=False,
            timeout=60,
            csv_path=results_dir / f"{model_name}.csv",
            overwrite=True,
        )
        print(f"Processed {len(results_df)} entries")

    logging.info("Judging answers...")

    # Judge answers and save to CSV
    for _, model_name in models_to_run:
        results_df = judge_answer_df(
            df=results_dir / f"{model_name}.csv",
            csv_path=results_dir / f"{model_name}_judged.csv",
            overwrite=True,
        )
        print(f"Judged {len(results_df)} entries")

    logging.info("Evaluating answers...")

    # Evaluate answers and combine results
    evaluation_results = []
    for _, model_name in models_to_run:
        judged_df = pd.read_csv(results_dir / f"{model_name}_judged.csv")
        eval_df = evaluate_answers(judged_df)
        eval_df["model"] = model_name
        evaluation_results.append(eval_df)

    # Combine all results and save
    combined_results = pd.concat(evaluation_results, ignore_index=True)
    combined_results.to_csv(results_dir / "evaluation_results.csv", index=False)
    logging.info("Evaluation complete. Results saved to evaluation_results.csv")


if __name__ == "__main__":
    main()
