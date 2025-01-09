from pathlib import Path

import pandas as pd


def judge_answer_df(
    df: Path | str | pd.DataFrame,
    csv_path: Path | str | None = None,
    overwrite: bool = False,
) -> pd.DataFrame:
    """
    Judge the answers in the DataFrame or CSV file.

    Args:
        df (Union[Path, str, pd.DataFrame]): Input DataFrame or path to CSV file.
        csv_path (Union[Path, str, None]): Path to save the judged results.
        overwrite (bool): Whether to overwrite existing output file.

    Returns:
        pd.DataFrame: The DataFrame with the judged results.
    """
    # Handle input
    if isinstance(df, (str, Path)):
        answers_df = pd.read_csv(df)
    else:
        answers_df = df

    if (
        "ground_truth" not in answers_df.columns
        or "llm_answer" not in answers_df.columns
    ):
        raise ValueError(
            "The input DataFrame must contain 'ground_truth' and 'llm_answer' columns."
        )

    # Process answers
    answers_df["is_correct"] = answers_df.apply(
        lambda row: judge_answer(
            ground_truth=row["ground_truth"],
            answer=row["llm_answer"],
        ),
        axis=1,
    )

    # Save results if path provided
    if csv_path is not None:
        csv_path = Path(csv_path)
        if csv_path.exists() and not overwrite:
            raise FileExistsError(
                f"Output file {csv_path} already exists. Set overwrite=True to overwrite."
            )
        answers_df.to_csv(csv_path, index=False)

    return answers_df


def judge_answer(
    ground_truth: str,
    answer: str,
) -> bool:
    """
    Exact matching function to compare the ground truth and the answer.

    Args:
        ground_truth (str): The ground truth answer.
        answer (str): The answer from the model.

    Returns:
        bool: Whether the answer is correct.
    """
    return ground_truth.strip().lower() == answer.strip().lower()
