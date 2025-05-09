from pathlib import Path
from typing import Union
import pandas as pd
from src.shared.llm import call_vision_model
from tqdm import tqdm

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
        raise ValueError("Failed to extract a valid score from the response.")

    return score

def evaluate_df(
    dataframe: pd.DataFrame,
    image_base_dir: Union[str, Path],
    model_name: str = "gemini-2.0-flash",
    provider: str = "api",
    temperature: float = 0.0,
    max_tokens: int = 2048,
    output_csv_path: Union[str, Path] = "data/generation_results/scores.csv",\
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
    if "hash" not in dataframe.columns:
        raise ValueError(
            "The DataFrame must contain a 'hash' column for evaluation."
        )
        
    image_base_dir = Path(image_base_dir)
    scores = []

    for idx, row in tqdm(dataframe.iterrows(), total=len(dataframe), desc="Evaluating generation tasks"):
        image_hash = row["hash"]
        slide_number = row["slide_number"]
        slide_filename = f"slide_{slide_number}.png"
        image_path = image_base_dir / image_hash / slide_filename
        try:
            score = evaluate_single_image(
                image_path=image_path,
                model_name=model_name,
                provider=provider,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        except Exception as e:
            score = None
        scores.append(score)

    dataframe = dataframe.copy()
    dataframe["score"] = scores
    output_df = dataframe[["hash", "slide_number", "score"]]
    output_csv_path = Path(output_csv_path)
    if output_csv_path.exists() and not overwrite:
        raise FileExistsError(
            f"{output_csv_path} already exists. Use overwrite=True to overwrite."
        )
    output_df.to_csv(output_csv_path, index=False)
    return output_df

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
    
    df.sample(5)
    image_base_dir = Path("data/generation_results/gpt-4o-2024-11-20/png")
    model_name = "gemini-2.0-flash"
    provider = "api"
    temperature = 0.0
    max_tokens = 2048
    output_csv_path = "data/generation_results/scores.csv"
    overwrite = True
    evaluate_df(
        dataframe=df,
        image_base_dir=image_base_dir,
        model_name=model_name,
        provider=provider,
        temperature=temperature,
        max_tokens=max_tokens,
        output_csv_path=output_csv_path,
        overwrite=overwrite,
    )