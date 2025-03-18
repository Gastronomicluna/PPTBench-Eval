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
    pass
