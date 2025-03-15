from .prompts import build_create_layout_prompt

from src.shared.llm import call_vision_model
from src.shared.pptx_api.api_doc import API
from typing import List
from pathlib import Path
def create_layout(text_input: str, image_path: Path) -> List[API]:
    pass
