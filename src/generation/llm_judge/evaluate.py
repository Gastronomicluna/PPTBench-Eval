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
    Evaluate all images in the specified directory without checking through dataframe.
    
    Args:
        dataframe (pd.DataFrame): DataFrame used only for output structure.
        image_dir_model (str): Name of the model directory containing the images.
        image_base_dir (Union[str, Path]): Base directory containing image folders.
            Defaults to "data/generation_results".
        model_name (str): Name of the model to use for evaluation.
            Defaults to "gemini-2.0-flash".
        provider (str): Provider of the model. Defaults to "api".
        temperature (float): Temperature for the model. Defaults to 0.0.
        max_tokens (int): Maximum tokens for the model. Defaults to 2048.
        output_csv_base_dir (Union[str, Path]): Directory to save the CSV output.
            Defaults to "data/generation_results".
        overwrite (bool): Whether to overwrite existing output files.
            Defaults to False.
    
    Returns:
        pd.DataFrame: DataFrame with evaluation scores.
    """
    logging.info("Starting evaluation of images in directory")
    
    image_base_dir = Path(image_base_dir)
    model_dir = image_base_dir / image_dir_model
    png_dir = model_dir / "png"
    
    if not png_dir.exists():
        logging.error(f"Image directory not found: {png_dir}")
        raise FileNotFoundError(f"Image directory not found: {png_dir}")
    
    results = []
    
    # Walk through all hash directories
    for hash_dir in tqdm(list(png_dir.iterdir()), desc="Evaluating image directories"):
        if not hash_dir.is_dir():
            continue
            
        image_hash = hash_dir.name
        
        # Process all slides in this hash directory
        for slide_file in sorted(hash_dir.glob("slide_*.png")):
            slide_number = int(slide_file.stem.split('_')[1])
            
            try:
                score = evaluate_single_image(
                    image_path=slide_file,
                    model_name=model_name,
                    provider=provider,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
            except Exception as e:
                logging.error(
                    f"Error evaluating image {slide_file}: {e}", exc_info=True
                )
                score = None
                
            results.append({
                "hash": image_hash,
                "slide_number": slide_number,
                "score": score
            })
    
    # Create output dataframe from results
    output_df = pd.DataFrame(results)
    
    # Save output to CSV
    output_csv_path = Path(output_csv_base_dir) / f"{image_dir_model}_scores.csv"
    if output_csv_path.exists() and not overwrite:
        logging.error(
            f"{output_csv_path} already exists. Use overwrite=True to overwrite."
        )
        raise FileExistsError(
            f"{output_csv_path} already exists. Use overwrite=True to overwrite."
        )
        
    # Create output directory if it doesn't exist
    output_csv_path.parent.mkdir(parents=True, exist_ok=True)
    
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
    image_base_dir = Path("data/generation_results")
    model_name = "gemini-2.0-flash"
    provider = "api"
    temperature = 0.0
    max_tokens = 8096
    output_csv_base_dir = "data/generation_results/scores"
    overwrite = True
    output = evaluate_df(
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

    # csv_path = Path("data/generation_results/scores/gemma3:12b_scores.csv")
    # df = pd.read_csv(csv_path)
    # score = df_score_0_100(df, score_column="score")
    # print(f"Score: {score}")