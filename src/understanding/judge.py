import logging
from pathlib import Path
from typing import Optional

import pandas as pd
from tqdm import tqdm

from ..shared.llm import call_vision_model
from ..shared.utils import csv_to_df, df_to_csv
from .prompts import build_judge_prompt


def judge_answer_df(
    csv_path: Path | str,
    overwrite: bool = False,
    openqa_mode: bool = False,
    judge_model: Optional[str] = None,
    judge_provider: Optional[str] = None,
) -> pd.DataFrame:
    """
    Judge the answers in the CSV file and save results back to the same file.

    Args:
        csv_path (Union[Path, str]): Path to CSV file for input and output.
        overwrite (bool): Whether to overwrite existing output file.
        openqa_mode (bool): Whether to use LLM judge for OpenQA evaluation.
        judge_model (Optional[str]): Model name for LLM judge (required for OpenQA).
        judge_provider (Optional[str]): Provider for LLM judge (required for OpenQA).

    Returns:
        pd.DataFrame: DataFrame with judged answers.
    """
    csv_path = Path(csv_path)
    answers_df = csv_to_df(csv_path)

    if answers_df is None:
        raise ValueError("The input DataFrame is empty.")

    if (
        "task" not in answers_df.columns
        or "ground_truth" not in answers_df.columns
        or "answer" not in answers_df.columns
    ):
        raise ValueError(
            "The input DataFrame must contain 'task', 'ground_truth', "
            "and 'answer' columns."
        )

    # Process answers
    if openqa_mode:
        if judge_model is None or judge_provider is None:
            raise ValueError(
                "OpenQA mode requires judge_model and judge_provider to be specified."
            )
        
        is_correct_list = []
        with tqdm(total=len(answers_df), desc=f"Judging with {judge_model}") as pbar:
            for _, row in answers_df.iterrows():
                # Parse options from the row if available
                options = None
                if "options" in row and row["options"]:
                    import json
                    try:
                        options = json.loads(row["options"]) if isinstance(row["options"], str) else row["options"]
                    except json.JSONDecodeError:
                        options = None
                
                result = judge_answer_openqa(
                    row["question"] if "question" in row else "",
                    row["ground_truth"],
                    row["answer"],
                    judge_model,
                    judge_provider,
                    options,
                )
                is_correct_list.append(result)
                pbar.update(1)
        answers_df["is_correct"] = is_correct_list
    else:
        answers_df["is_correct"] = answers_df.apply(
            lambda row: judge_answer(row["ground_truth"], row["answer"]),
            axis=1,
        )

    # Save results
    if overwrite:
        df_to_csv(answers_df, csv_path)

    return answers_df


def judge_answer(
    ground_truth: str,
    answer: Optional[str],
) -> bool:
    """
    Judge the answer based on the task and the ground truth.

    Args:
        task (str): The task type.
        ground_truth (str): The ground truth answer.
        answer (str): The answer from the model.

    Returns:
        bool: Whether the answer is correct.
    """
    return str(ground_truth).strip().lower() == str(answer).strip().lower()


def judge_answer_openqa(
    question: str,
    ground_truth: str,
    answer: Optional[str],
    judge_model: str,
    judge_provider: str,
    options: Optional[dict] = None,
) -> bool:
    """
    Judge the OpenQA answer using an LLM judge.

    Args:
        question (str): The original question.
        ground_truth (str): The ground truth answer (option letter).
        answer (str): The answer from the model.
        judge_model (str): Name of the judge model.
        judge_provider (str): Provider of the judge model.
        options (Optional[dict]): Dictionary of options {letter: text} for context.

    Returns:
        bool: Whether the answer is correct according to the judge.
    """
    if answer is None or str(answer).strip() == "":
        return False

    prompt = build_judge_prompt(
        question=question,
        ground_truth=ground_truth,
        answer=answer,
        options=options,
    )

    try:
        result = call_vision_model(
            model_name=judge_model,
            provider=judge_provider,
            prompt=prompt,
            temperature=0.0,
            max_tokens=1024,
            json_mode=True,
        )

        # Parse the result
        if isinstance(result, dict) and "is_correct" in result:
            return bool(result["is_correct"])
        elif isinstance(result, str):
            import json

            parsed = json.loads(result)
            return bool(parsed.get("is_correct", False))
        return False
    except Exception as e:
        # If judging fails, log error and return False
        import logging

        logging.error(f"Error judging answer: {e}")
        return False
