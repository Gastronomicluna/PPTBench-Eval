import csv
import logging

from src.detection.get_answers import get_answers
from src.detection.judge import judge_answer_df
from src.shared.llm import API_LLM_MODELS
from src.shared.load_save_huggingface_dataset import load_save_huggingface_dataset_df

logging.basicConfig(level=logging.INFO)


def main():
    dataset_name = "tyrionhuu/PPTBench-Detection"
    dataset_path = "data/PPTBench-Detection"
    results_dir = "data/detection_results"
    if not results_dir.exists():
        results_dir.mkdir(parents=True)
    df = load_save_huggingface_dataset_df(
        dataset_name=dataset_name,
        dataset_path=dataset_path,
    )
    # print(df.head())

    logging.info("Generating answers...")

    for model_name in API_LLM_MODELS:
        print(f"Processing {model_name}...")
        results_df = get_answers(
            df=df,
            model_name=model_name,
            provider="api",
            temperature=0.0,
            max_tokens=3200,
            json=False,
            timeout=60,
            csv_path=results_dir / f"{model_name}.csv",
            overwrite=False,
        )
        print(f"Processed {len(results_df)} entries")

    logging.info("Judging answers...")

    # Evaluate and save results


if __name__ == "__main__":
    main()
