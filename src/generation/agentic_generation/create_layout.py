from pathlib import Path
from typing import List

from src.shared.llm import call_vision_model
from src.shared.pptx_api.api_doc import API

from .prompts import build_create_layout_prompt


def create_layout(text_input: str, image_path: Path) -> List[API]:
    pass
