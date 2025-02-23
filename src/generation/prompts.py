import json
from pathlib import Path
from typing import Any, Dict, List, Literal

from ..shared.pptx_api.api_doc import api_list
from ..shared.utils import (
    api_to_string,
    get_notes_from_json_data,
    get_texts_from_json_data,
)

# JSON templates for examples
GENERATION_EXAMPLES = {
    "function1": "choose_slide(0)",
    "function2": "choose_shape(1)",
    "function3": "set_width(1000000)",
    "function4": "insert_text('Hello, World!')",
}


def get_slide_layout_examples(template_dir: Path) -> str:
    """
    Get slide layout examples from the given template directory.

    Args:
        template_dir (Path): The path to the template directory.

    Returns:
        str: The slide layout examples as a formatted string.

    Raises:
        FileNotFoundError: If template_dir doesn't exist or required JSON files are missing.
        json.JSONDecodeError: If any JSON file is malformed.
    """
    if not template_dir.exists():
        raise FileNotFoundError(f"Template directory not found: {template_dir}")

    required_files = [
        "title_slide.json",
        "title_and_content.json",
        "section_header.json",
        "two_content.json",
        "picture_with_caption.json"
    ]

    # Verify all required files exist
    missing_files = [f for f in required_files if not (template_dir / f).exists()]
    if missing_files:
        raise FileNotFoundError(
            f"Missing required template files: {', '.join(missing_files)}"
        )

    example_str = "You can choose to use the following slide layouts:\n"
    try:
        # Load and append each layout section
        example_str += "1. Title Slide\n"
        example_str += json.load(open(template_dir / "title_slide.json"))
        example_str += "2. Title and Content\n"
        example_str += json.load(open(template_dir / "title_and_content.json"))
        example_str += "3. Section Header\n"
        example_str += json.load(open(template_dir / "section_header.json"))
        example_str += "4. Two Content\n"
        example_str += json.load(open(template_dir / "two_content.json"))
        example_str += "5. Picture with Caption\n"
        example_str += json.load(open(template_dir / "picture_with_caption.json"))
        
        return example_str
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(
            f"Error parsing JSON template file: {e.doc}", e.doc, e.pos
        ) from e


def build_prompt(
    query: str,
    task: Literal[
        "note_to_slide", "multimedia_to_slide", "screenshot_to_slide", "text_to_slide"
    ],
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
        notes = get_notes_from_json_data(slide_json)
        return build_prompt_for_note_to_slide(
            query=query, notes=notes, content_images=content_images
        )
    if task == "multimedia_to_slide":
        texts = get_texts_from_json_data(slide_json)
        return build_prompt_for_multimedia_to_slide(
            query=query, content_images=content_images, texts=texts
        )
    if task == "screenshot_to_slide":
        return build_prompt_for_screenshot_to_slide(
            query=query, content_images=content_images
        )
    if task == "text_to_slide":
        texts = get_texts_from_json_data(slide_json)
        return build_prompt_for_text_to_slide(query=query, texts=texts)
    raise ValueError(f"Invalid task: {task}")


def build_prompt_for_text_to_slide(
    query: str,
    texts: List[str],
) -> str:
    """
    Build the prompt for the given query for the text_to_slide task.

    Args:
        query (str): The query to build the prompt for.
        texts (List[str]): The list of texts.

    Returns:
        str: The prompt for the query.
    """
    divider = "#" * 80
    example_json_str = json.dumps(GENERATION_EXAMPLES, indent=2)
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
    prompt += "Texts:\n"
    for text in texts:
        prompt += f"{text}\n"
    prompt += "\n"
    prompt += f"Query: {query}\n"
    prompt += "Answer:\n"

    return prompt


def build_prompt_for_screenshot_to_slide(
    query: str,
    content_images: List[str] = [],
) -> str:
    """
    Build the prompt for the given query for the screenshot_to_slide task.

    Args:
        query (str): The query to build the prompt for.
        content_images (List[str], optional): The list of content images. Defaults to [].

    Returns:
        str: The prompt for the query.
    """
    divider = "#" * 80
    example_json_str = json.dumps(GENERATION_EXAMPLES, indent=2)
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
    if content_images != []:
        prompt += "The first image is the screenshot you need to convert to a slide.\n"
        prompt += "The remaining images are materials you can use, and their paths are "
        prompt += f"{content_images}"
        prompt += "\n"
    prompt += f"Query: {query}\n"
    prompt += "Answer:\n"

    return prompt


def build_prompt_for_multimedia_to_slide(
    query: str,
    content_images: List[str] = [],
    texts: List[str] = [],
) -> str:
    """
    Build the prompt for the given query for the multimedia_to_slide task.

    Args:
        query (str): The query to build the prompt for.
        slide_json (Dict[str, Any]): The JSON data for the slide.
        content_images (List[str], optional): The list of content images. Defaults to [].

    Returns:
        str: The prompt for the query.
    """
    divider = "#" * 80
    example_json_str = json.dumps(GENERATION_EXAMPLES, indent=2)
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
    if texts != []:
        prompt += "Texts:\n"
        for text in texts:
            prompt += f"{text}\n"
        prompt += "\n"
    if content_images != []:
        prompt += "The images given are materials you can use, and their paths are "
        prompt += f"{content_images}"
        prompt += "\n"
    prompt += f"Query: {query}\n"
    prompt += "Answer:\n"

    return prompt


def build_prompt_for_note_to_slide(
    query: str,
    notes: str,
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
    example_json_str = json.dumps(GENERATION_EXAMPLES, indent=2)
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
