import concurrent.futures
import logging
import os
from typing import Dict
import pandas as pd

from ..shared.get_answer import get_answers
from ..shared.llm import API_LLM_MODELS
from ..shared.load_save_dataset import load_save_dataset_df
from ..shared.utils import get_project_root, process_model
from .evaluation import evaluate_answers
from .format_answers import format_answer_csv
from .get_answers import get_answer_single_detection
from .judge import judge_answer_df


def main(
    max_workers: int = 4,
    ollama_mode: bool = True,
    test_mode: bool = False,
    non_magic_mode: bool = False,
) -> None:
    """Main entry point for the detection pipeline.

    This function sets up the environment, loads the dataset,
    and processes, evaluates, and saves detection results.

    Args:
        max_workers: Maximum number of concurrent workers for parallel processing.
            Defaults to 4.
        ollama_mode: Whether to only run OLLAMA models. Defaults to True.
        test_mode: Whether to run in test mode. Defaults to False.
        non_magic_mode: Whether to run in non-magic mode. Defaults to False.

    Returns:
        None
    """
    project_root = get_project_root()
    dataset_name = "tyrionhuu/PPTBench-Detection"
    dataset_path = "data/PPTBench-Detection"

    # Update results_dir to be relative to project root
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

    if not models_to_run:
        logging.error("No models configured to run")
        return

    logging.info("Generating answers...")

    # Process models in parallel with error handling
    results: Dict[str, pd.DataFrame] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_model = {
            executor.submit(
                process_model,
                function=get_answers,
                get_answer_single=get_answer_single_detection,
                df=df,
                model_name=model_name,
                provider=provider,
                temperature=0.0,
                max_tokens=3200,
                json=True,
                timeout=60,
                csv_path=results_dir / f"{model_name}.csv",
                overwrite=False,
            ): (provider, model_name)
            for provider, model_name in models_to_run
        }

        for future in concurrent.futures.as_completed(future_to_model):
            _, model_name = future_to_model[future]
            try:
                results[model_name] = future.result()
            except Exception as e:
                logging.error(f"Model {model_name} failed: {str(e)}")

    logging.info("Formatting answers...")

    # Format answers with file existence check
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

    logging.info("Judging answers...")

    # Judge answers and save to CSV
    for _, model_name in models_to_run:
        results_df = judge_answer_df(
            csv_path=results_dir / f"{model_name}.csv",
            overwrite=True,
        )
        print(f"Judged {len(results_df)} entries")

    logging.info("Evaluating answers...")

    # Evaluate answers and combine results
    evaluation_results = []
    for _, model_name in models_to_run:
        judged_df = pd.read_csv(results_dir / f"{model_name}.csv")
        eval_df = evaluate_answers(judged_df)
        eval_df["model"] = model_name
        evaluation_results.append(eval_df)

    # Combine all results and save
    combined_results = pd.concat(evaluation_results, ignore_index=True)
    combined_results.to_csv(results_dir / "evaluation_results.csv", index=False)
    logging.info("Evaluation complete. Results saved to evaluation_results.csv")


if __name__ == "__main__":
    main(
        max_workers=4,
        ollama_mode=True,
        test_mode=False,
    )
