from pathlib import Path
from typing import Union

from src.shared.llm import call_vision_model

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
        image=image_path,
    )

    # Extract the score from the response
    score = extract_score(response)
    if score is None:
        raise ValueError("Failed to extract a valid score from the response.")

    return score
