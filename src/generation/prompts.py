import json
from typing import Any, Dict, Literal

from ..shared.pptx_api.api_doc import api_list
from ..shared.utils import api_to_string

# JSON templates for examples
GENERATION_EXAMPLE = {
    "function1": "choose_slide(0)",
    "function2": "choose_shape(1)",
    "function3": "set_width(1000000)",
    "function4": "insert_text('Hello, World!')",
}


def build_prompt(
    query: str,
    task: Literal["note_to_slide", "multimedia_to_slide", "screenshot_to_slide", "text_to_slide"],
    slide_json: Dict[str, Any],
) -> str:
    """
    Build the prompt for the given query.

    Args:
        query (str): The query to build the prompt for.
        slide_json (Dict[str, Any]): The JSON data for the slide.

    Returns:
        str: The prompt for the query.
    """
    pass
    divider = "#" * 80
    example_json_str = json.dumps(GENERATION_EXAMPLE, indent=2)

    prompt = ""
    prompt += "Task: You are given a slide from a presentation in the form of an image and JSON data.\n"
    prompt += f"{query}\n"
    prompt += "To achieve this task, you can use the following functions:\n"
    prompt += f"{api_to_string(api_list)}\n\n"
    prompt += "Instructions:\n"
    prompt += "- Return in JSON format only the requested information without any additional text or explanations.\n"
    prompt += "- Abide by JSON formatting rules.\n\n"
    prompt += "Examples:\n"
    prompt += f"{example_json_str}\n\n"
    prompt += f"{divider}\n"
    prompt += "Slide JSON:\n"
    prompt += f"{json.dumps(slide_json, indent=2)}\n\n"
    prompt += f"{divider}\n"
    prompt += f"Query: {query}\n"
    prompt += "Answer:\n"

    return prompt
