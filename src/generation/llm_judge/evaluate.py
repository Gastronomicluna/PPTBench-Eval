import logging
from pathlib import Path
from typing import Union

import pandas as pd
from tqdm import tqdm

from src.shared.llm import call_vision_model

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

from .prompts import PROMPT_TEMPLATE
from .utils import extract_score


def evaluate_single_image(
    image_path: Union[str, Path],
    model_name: str = "gemini-2.0-flash",
    provider: str = "api",
    temperature: float = 0.0,
    max_tokens: int = 2048,
) -> int:
    """
    Evaluate a single image using the specified model and provider.

    Args:
        image_path (Union[str, Path]): Path to the image file.
        model_name (str): Name of the model to use for evaluation.
        provider (str): Provider of the model (e.g., "openai", "huggingface").
        temperature (float, optional): Temperature for the model. Defaults to 0.0.
        max_tokens (int, optional): Maximum tokens for the model. Defaults to 2048.

    Returns:
        int: The evaluation score.
    """
    # Ensure the image path is a string
    image_path = str(image_path)
    logging.info(
        f"Evaluating image: {image_path} with model: {model_name}, provider: {provider}"
    )

    # Call the model with the image and prompt
    response = call_vision_model(
        model_name=model_name,
        provider=provider,
        temperature=temperature,
        max_tokens=max_tokens,
        prompt=PROMPT_TEMPLATE,
        images=image_path,
    )

    # Extract the score from the response
    score = extract_score(response)
    if score is None:
        logging.error(
            f"Failed to extract a valid score from the response for image: {image_path}"
        )
        raise ValueError("Failed to extract a valid score from the response.")

    logging.info(f"Score for {image_path}: {score}")
    return score


def evaluate_df(
    dataframe: pd.DataFrame,
    image_dir_model: str,
    image_base_dir: Union[str, Path] = "data/generation_results",
    model_name: str = "gemini-2.0-flash",
    provider: str = "api",
    temperature: float = 0.0,
    max_tokens: int = 2048,
    output_csv_base_dir: Union[str, Path] = "data/generation_results",
    overwrite: bool = False,
) -> pd.DataFrame:
    """
    Evaluate a DataFrame of images using the specified model and provider.
    Args:
        dataframe (pd.DataFrame): DataFrame containing image paths.
        model_name (str): Name of the model to use for evaluation.
        provider (str): Provider of the model (e.g., "openai", "huggingface").
        temperature (float, optional): Temperature for the model. Defaults to 0.0.
        max_tokens (int, optional): Maximum tokens for the model. Defaults to 2048.

    Returns:
        pd.DataFrame: DataFrame with the evaluation scores added.
    """
    logging.info("Starting evaluation of DataFrame with %d rows.", len(dataframe))
    if "hash" not in dataframe.columns:
        logging.error("The DataFrame must contain a 'hash' column for evaluation.")
        raise ValueError("The DataFrame must contain a 'hash' column for evaluation.")

    image_base_dir = Path(image_base_dir)
    scores = []

    for _, row in tqdm(
        dataframe.iterrows(), total=len(dataframe), desc="Evaluating generation tasks"
    ):
        image_hash = row["hash"]
        slide_number = row["slide_number"]
        slide_filename = f"slide_{slide_number}.png"
        image_path = (
            image_base_dir / image_dir_model / "png" / image_hash / slide_filename
        )
        if not image_path.exists():
            logging.warning(f"Image not found: {image_path}. Assigning score 0.")
            score = 0
        else:
            try:
                score = evaluate_single_image(
                    image_path=image_path,
                    model_name=model_name,
                    provider=provider,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
            except Exception as e:
                logging.error(
                    f"Error evaluating image {image_path}: {e}", exc_info=True
                )
                score = None
        scores.append(score)

    dataframe = dataframe.copy()
    dataframe["score"] = scores
    output_df = dataframe[["hash", "slide_number", "score"]]
    output_csv_path = Path(output_csv_base_dir) / image_dir_model + "_scores.csv"
    output_csv_path = Path(output_csv_path)
    if output_csv_path.exists() and not overwrite:
        logging.error(
            f"{output_csv_path} already exists. Use overwrite=True to overwrite."
        )
        raise FileExistsError(
            f"{output_csv_path} already exists. Use overwrite=True to overwrite."
        )
    output_df.to_csv(output_csv_path, index=False)
    logging.info(f"Saved evaluation results to {output_csv_path}")
    return output_df


def df_score_0_100(df: pd.DataFrame, score_column: str = "score") -> float:
    """
    Convert a DataFrame of 0-5 scores to a single float in the 0-100 range.

    Args:
        df (pd.DataFrame): DataFrame containing the score column.
        score_column (str): Name of the score column.

    Returns:
        float: The mean score mapped to 0-100.
    """
    valid_scores = df[score_column].dropna()
    if valid_scores.empty:
        return 0.0
    mean_0_5 = valid_scores.mean()
    score_0_100 = (mean_0_5 / 5) * 100
    return score_0_100


if __name__ == "__main__":
    # Example usage
    # image_path = "data/generation_results/gpt-4o-2024-11-20/png/ec08174b0e10decc19058921a5bce7ad/slide_1.png"
    # model_name = "gemini-2.0-flash"
    # provider = "api"
    # score = evaluate_single_image(image_path, model_name=model_name, provider=provider)
    # print(f"Score for {score}")

    from src.shared.load_save_dataset import load_save_dataset_df

    dataset_name = "tyrionhuu/PPTBench-Generation"
    dataset_path = "data/PPTBench-Generation"
    csv_path = "data/" + "generation_results.csv"

    df = load_save_dataset_df(
        dataset_name=dataset_name,
        dataset_path=dataset_path,
        force_download=False,
        source="huggingface",
    )

    df = df.head(5)
    image_base_dir = Path("data/generation_results")
    model_name = "gemini-2.0-flash"
    provider = "api"
    temperature = 0.0
    max_tokens = 8096
    output_csv_base_dir = "data/generation_results"
    overwrite = True
    output = evaluate_df(
        dataframe=df,
        image_dir_model="gpt-4o-2024-11-20",
        image_base_dir=image_base_dir,
        model_name=model_name,
        provider=provider,
        temperature=temperature,
        max_tokens=max_tokens,
        output_csv_base_dir=output_csv_base_dir,
        overwrite=overwrite,
    )
    
    score = df_score_0_100(output, score_column="score")
    print(f"Score: {score}")
