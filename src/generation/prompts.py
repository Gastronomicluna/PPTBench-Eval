import json
from typing import Any, Dict, Literal, List

from ..shared.pptx_api.api_doc import api_list
from ..shared.utils import api_to_string, get_notes_from_json_data

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
    content_images: List[str] = [],
) -> str:
    """
    Build the prompt for the given query.

    Args:
        query (str): The query to build the prompt for.
        slide_json (Dict[str, Any]): The JSON data for the slide.
        task (Literal["note_to_slide", "multimedia_to_slide", "screenshot_to_slide", "text_to_slide"]): 
            The task to build the prompt for.
        content_images (List[str], optional): The list of content images. Defaults to
        
    Returns:
        str: The prompt for the query.
    """
    if task == "note_to_slide":
        return build_prompt_for_note_to_slide(query=query, slide_json=slide_json, content_images=content_images)



def build_prompt_for_note_to_slide(
    query: str,
    slide_json: Dict[str, Any],
    content_images: List[str] = [],
) -> str:
    """
    Build the prompt for the given query for the note_to_slide task.

    Args:
        query (str): The query to build the prompt for.
        slide_json (Dict[str, Any]): The JSON data for the slide.
        content_images (List[str], optional): The list of content images. Defaults to [].
        
    Returns:
        str: The prompt for the query.
    """
    divider = "#" * 80
    example_json_str = json.dumps(GENERATION_EXAMPLE, indent=2)
    notes = get_notes_from_json_data(slide_json)
    prompt = ""
    prompt += f"{query}\n"
    prompt += "To achieve this task, you can use the following functions:\n"
    prompt += f"{api_to_string(api_list)}\n\n"
    prompt += "Instructions:\n"
    prompt += "- Return in JSON format only the requested information without any additional text or explanations.\n"
    prompt += "- Abide by JSON formatting rules.\n\n"
    prompt += "Examples:\n"
    prompt += f"{example_json_str}\n\n"
    prompt += f"{divider}\n"
    prompt += "Notes:\n"
    prompt += f"{notes}\n\n"
    prompt += f"{divider}\n"
    if content_images != []:
        prompt += "The images given are materials you can use, and their paths are "
        prompt += f"{content_images}"
        prompt += "\n"
    prompt += f"Query: {query}\n"
    prompt += "Answer:\n"

    return prompt