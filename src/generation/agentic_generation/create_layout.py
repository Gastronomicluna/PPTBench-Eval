from pathlib import Path
from typing import List, Literal

from src.shared.llm import call_vision_model
from src.shared.pptx_api.api_doc import API

from .prompts import build_create_layout_prompt


def create_presentation(
    text_input: str,
    image_path: Path,
    model_name: str,
    presentation_path: Path,
    provider: Literal["api", "ollama", "openai", "anthropic"] = "ollama",
    temperature: float = 0.5,
    max_tokens: int = 3200,
) -> None:
    pass


def generate_api_list(
    text_input: str,
    image_path: Path,
    model_name: str,
    provider: Literal["api", "ollama", "openai", "anthropic"] = "ollama",
    temperature: float = 0.5,
    max_tokens: int = 3200,
) -> List[str]:
    prompt = build_create_layout_prompt(
        input_data=text_input,
    )

    api_list = call_vision_model(
        prompt=prompt,
        model_name=model_name,
        provider=provider,
        temperature=temperature,
        max_tokens=max_tokens,
        images=[image_path],
    )
    return api_list


def run_api_list(
    api_list: List[str],
    presentation_path: Path,
) -> None:
    pass
