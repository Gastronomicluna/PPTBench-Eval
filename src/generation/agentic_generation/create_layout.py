import json
import logging
from pathlib import Path
from typing import List, Literal

from src.shared.llm import call_vision_model
from src.shared.pptx_api.api_doc import API
from src.shared.utils import str_to_list

from .prompts import build_create_layout_prompt


def create_presentation(
    text_input: str,
    image_path: Path,
    model_name: str,
    presentation_path: Path,
    provider: Literal["api", "ollama", "openai", "anthropic"] = "ollama",
    temperature: float = 0.5,
    max_tokens: int = 3200,
    json_mode: bool = False,
) -> None:
    pass


def generate_api_list(
    text_input: str,
    image_path: Path,
    model_name: str,
    provider: Literal["api", "ollama", "openai", "anthropic"] = "ollama",
    temperature: float = 0.5,
    max_tokens: int = 3200,
    json_mode: bool = False,
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
        except Exception as e:
            raise RuntimeError(f"Error calling vision model: {str(e)}")

        # Process the model response
        if llm_answer is None:
            raise ValueError("Received empty response from vision model")

        llm_answer_str = (
            json.dumps(llm_answer) if isinstance(llm_answer, dict) else llm_answer
        )

        # Parse the API calls from the response
        api_calls = str_to_list(llm_answer_str)

        if not api_calls:
            raise ValueError("No API calls generated from model response")

        return api_calls

    except json.JSONDecodeError as e:
        raise ValueError(f"Error parsing model response as JSON: {str(e)}")
    except Exception as e:
        logging.error(f"Unexpected error in generate_api_list: {str(e)}")
        raise


def run_api_list(
    api_list: List[str],
    presentation_path: Path,
) -> None:
    pass


def main() -> None:
    text_input = """
    All ETA Grantees are expected to report outcomes achieved through the Grant. I\u2019d like to take just a minute here to mention that in addition to the ROI that I will discuss here, outcomes should include those tracked for the purpose of reporting on the Common Measures which are include entered employment, job retention, and average earnings for Adults and for youth, the Common Measures include placement in employment or education, attainment of a degree or certificate, and literacy and numeracy gains. 
    """
    image_path = Path("datasets/w18.jpg")
    model_name = "gpt-4o"
    provider = "api"
    
    api_list = generate_api_list(
        text_input=text_input,
        image_path=image_path,
        model_name=model_name,
        provider=provider,
    )
    
    print(api_list)
    
if __name__ == "__main__":
    main()