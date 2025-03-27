import json
import logging
from pathlib import Path
from typing import List, Literal

from src.shared.llm import call_vision_model
from src.shared.parse_answer import parse_api_calls

from ..generate_pptx import generate_pptx
from .prompts import build_create_layout_prompt


def create_presentation(
    text_input: str,
    image_path: Path,
    model_name: str,
    presentation_path: Path,
    output_path: Path,
    provider: Literal["api", "ollama", "openai", "anthropic"] = "ollama",
    temperature: float = 0.5,
    max_tokens: int = 3200,
    json_mode: bool = True,
    slide_width: int = 9144000,
    slide_height: int = 6858000,
) -> None:
    """Create a PowerPoint presentation based on text input and an image.

    This function generates a list of API calls based on the text input and image,
    and then creates a PowerPoint presentation using the API calls.

    Args:
        text_input: The textual input to guide presentation creation.
        image_path: Path to the image file to be processed.
        model_name: The name of the vision model to use.
        presentation_path: Path to save the generated PowerPoint presentation.
        provider: The provider of the vision model. Options are "api", "ollama",
            "openai", or "anthropic". Defaults to "ollama".
        temperature: Sampling temperature for the model. Defaults to 0.5.
        max_tokens: Maximum number of tokens for the response. Defaults to 3200.
        json_mode: Whether to use JSON mode for the model response.
            Defaults to False.

    Raises:
        ValueError: If no API calls could be generated or the model response
            is invalid.
        FileNotFoundError: If the image file does not exist.
        RuntimeError: If there's an issue with the model call.
    """
    try:
        # Generate a list of API calls
        api_calls = generate_api_calls(
            text_input=text_input,
            image_path=image_path,
            model_name=model_name,
            provider=provider,
            temperature=temperature,
            max_tokens=max_tokens,
            json_mode=json_mode,
            slide_width=slide_width,
            slide_height=slide_height,
        )
        print(api_calls)
        # Create the PowerPoint presentation
        generate_pptx(
            api_calls=api_calls,
            pptx_path=presentation_path,
            output_path=output_path,
        )

    except Exception as e:
        logging.error(f"Unexpected error in create_presentation: {str(e)}")
        raise


def generate_api_calls(
    text_input: str,
    image_path: Path,
    model_name: str,
    provider: Literal["api", "ollama", "openai", "anthropic"] = "ollama",
    temperature: float = 0.5,
    max_tokens: int = 3200,
    json_mode: bool = False,
    slide_width: int = 9144000,
    slide_height: int = 6858000,
) -> List[str]:
    """Generate a list of API calls based on text input and an image.

    This function creates a prompt based on the text input, sends it along with
    the image to a vision model, and processes the response to extract API calls.

    Args:
        text_input: The textual input to guide presentation creation.
        image_path: Path to the image file to be processed.
        model_name: The name of the vision model to use.
        provider: The provider of the vision model. Options are "api", "ollama",
            "openai", or "anthropic". Defaults to "ollama".
        temperature: Sampling temperature for the model. Defaults to 0.5.
        max_tokens: Maximum number of tokens for the response. Defaults to 3200.
        json_mode: Whether to use JSON mode for the model response.
            Defaults to False.

    Returns:
        A list of API call strings.

    Raises:
        ValueError: If no API calls could be generated or the model response
            is invalid.
        FileNotFoundError: If the image file does not exist.
        RuntimeError: If there's an issue with the model call.
    """
    try:
        # Validate image path exists
        if not image_path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")

        # Create the prompt
        prompt = build_create_layout_prompt(
            input_data=text_input,
            slide_height=slide_height,
            slide_width=slide_width,
        )

        # Call the vision model
        try:
            llm_answer = call_vision_model(
                prompt=prompt,
                model_name=model_name,
                provider=provider,
                temperature=temperature,
                max_tokens=max_tokens,
                images=[image_path],
                json_mode=json_mode,
            )
            # print(llm_answer)
        except Exception as e:
            raise RuntimeError(f"Error calling vision model: {str(e)}")

        # Process the model response
        if llm_answer is None:
            raise ValueError("Received empty response from vision model")

        api_calls = parse_api_calls(llm_answer)

        if not api_calls:
            raise ValueError("No API calls generated from model response")

        return api_calls

    except json.JSONDecodeError as e:
        raise ValueError(f"Error parsing model response as JSON: {str(e)}")
    except Exception as e:
        logging.error(f"Unexpected error in generate_api_calls: {str(e)}")
        raise


def main() -> None:
    text_input = """
Deep within the heart of the Whispering Forest, where sunlight danced through emerald leaves and the air hummed with secrets, there stood an ancient oak. Its gnarled roots twisted like serpents, and its branches reached skyward as if yearning to touch the stars.    """
    image_path = Path("datasets/Picture1.jpg")
    model_name = "gpt-4o"
    provider = "api"

    presentation_path = Path("datasets/Presentation1.pptx")
    output_path = Path("datasets/output.pptx")
    create_presentation(
        text_input=text_input,
        image_path=image_path,
        model_name=model_name,
        presentation_path=presentation_path,
        provider=provider,
        output_path=output_path,
    )


if __name__ == "__main__":
    main()
