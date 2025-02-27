import json
from pathlib import Path
from typing import Any, Dict, List, Literal

from ..shared.pptx_api.api_doc import SLIDE_LAYOUTS
from ..shared.utils import (
    get_api_list_prompt,
    get_notes_from_json_data,
    get_texts_from_json_data,
)

# JSON templates for examples
GENERATION_EXAMPLES = {
    "function1": "choose_slide(0)",
    "function2": "choose_shape(1)",
    "function3": "set_width(1000000)",
    "function4": "insert_text('Hello, World!')",
    "function5": "create_slide(1)",
}

# Default template directory path
DEFAULT_TEMPLATE_DIR = Path(__file__).parent / "json_templates"


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

    # Use layout indices from 0 to 10
    layout_indices = list(range(11))  # 0 to 10 inclusive

    # Build filenames based on layout indices
    layout_files = {idx: f"{idx}.json" for idx in layout_indices}

    # Verify all required files exist
    required_files = list(layout_files.values())
    missing_files = [f for f in required_files if not (template_dir / f).exists()]
    if missing_files:
        raise FileNotFoundError(
            f"Missing required template files: {', '.join(missing_files)}"
        )

    example_str = "Here is some example slide layouts:\n\n"
    try:
        # Use SLIDE_LAYOUTS to get the proper names when building examples
        for layout_idx, filename in layout_files.items():
            with open(template_dir / filename) as f:
                layout_data = json.load(f)
                layout_name = SLIDE_LAYOUTS.get(layout_idx, f"Layout {layout_idx}")
                example_str += f"{layout_idx}. {layout_name}\n"
                example_str += json.dumps(layout_data, indent=2) + "\n\n"

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
    template_dir: Path = DEFAULT_TEMPLATE_DIR,
) -> str:
    """
    Build the prompt for the given query.

    Args:
        query (str): The query to build the prompt for.
        slide_json (Dict[str, Any]): The JSON data for the slide.
        task (Literal["note_to_slide", "multimedia_to_slide", "screenshot_to_slide", "text_to_slide"]):
            The task to build the prompt for.
        content_images (List[str], optional): The list of content images. Defaults to
        template_dir (Path, optional): The path to the template directory. Defaults to None.

    Returns:
        str: The prompt for the query.
    """
    if task == "note_to_slide":
        notes = get_notes_from_json_data(slide_json)
        return build_prompt_for_note_to_slide(
            query=query,
            notes=notes,
            content_images=content_images,
            template_dir=template_dir,
        )
    if task == "multimedia_to_slide":
        texts = get_texts_from_json_data(slide_json)
        return build_prompt_for_multimedia_to_slide(
            query=query,
            content_images=content_images,
            texts=texts,
            template_dir=template_dir,
        )
    if task == "screenshot_to_slide":
        return build_prompt_for_screenshot_to_slide(
            query=query, content_images=content_images, template_dir=template_dir
        )
    if task == "text_to_slide":
        texts = get_texts_from_json_data(slide_json)
        return build_prompt_for_text_to_slide(
            query=query, texts=texts, template_dir=template_dir
        )
    raise ValueError(f"Invalid task: {task}")


def build_prompt_for_text_to_slide(
    query: str,
    texts: List[str],
    template_dir: Path = DEFAULT_TEMPLATE_DIR,
) -> str:
    """
    Build the prompt for the given query for the text_to_slide task.

    Args:
        query (str): The query to build the prompt for.
        texts (List[str]): The list of texts.
        template_dir (Path): The path to the template directory.

    Returns:
        str: The prompt for the query.
    """
    divider = "#" * 80
    example_json_str = json.dumps(GENERATION_EXAMPLES, indent=2)
    prompt = ""
    prompt += f"{query}\n"
    prompt += get_api_list_prompt()
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
    try:
        prompt += get_slide_layout_examples(template_dir) + "\n"
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Warning: Could not load slide layout examples: {e}")
    prompt += f"Query: {query}\n"
    prompt += "Answer:\n"

    return prompt


def build_prompt_for_screenshot_to_slide(
    query: str,
    content_images: List[str] = [],
    template_dir: Path = DEFAULT_TEMPLATE_DIR,
) -> str:
    """
    Build the prompt for the given query for the screenshot_to_slide task.

    Args:
        query (str): The query to build the prompt for.
        content_images (List[str], optional): The list of content images. Defaults to [].
        template_dir (Path, optional): The path to the template directory. Defaults to None.

    Returns:
        str: The prompt for the query.
    """
    divider = "#" * 80
    example_json_str = json.dumps(GENERATION_EXAMPLES, indent=2)
    prompt = ""
    prompt += f"{query}\n"
    prompt += get_api_list_prompt()
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
    if template_dir:
        try:
            prompt += get_slide_layout_examples(template_dir) + "\n"
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Warning: Could not load slide layout examples: {e}")
    prompt += f"Query: {query}\n"
    prompt += "Answer:\n"

    return prompt


def build_prompt_for_multimedia_to_slide(
    query: str,
    content_images: List[str] = [],
    texts: List[str] = [],
    template_dir: Path = DEFAULT_TEMPLATE_DIR,
) -> str:
    """
    Build the prompt for the given query for the multimedia_to_slide task.

    Args:
        query (str): The query to build the prompt for.
        slide_json (Dict[str, Any]): The JSON data for the slide.
        content_images (List[str], optional): The list of content images. Defaults to [].
        template_dir (Path, optional): The path to the template directory. Defaults to None.

    Returns:
        str: The prompt for the query.
    """
    divider = "#" * 80
    example_json_str = json.dumps(GENERATION_EXAMPLES, indent=2)
    prompt = ""
    prompt += f"{query}\n"
    prompt += get_api_list_prompt()
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
    if template_dir:
        try:
            prompt += get_slide_layout_examples(template_dir) + "\n"
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Warning: Could not load slide layout examples: {e}")
    prompt += f"Query: {query}\n"
    prompt += "Answer:\n"

    return prompt


def build_prompt_for_note_to_slide(
    query: str,
    notes: str,
    content_images: List[str] = [],
    template_dir: Path = DEFAULT_TEMPLATE_DIR,
) -> str:
    """
    Build the prompt for the given query for the note_to_slide task.

    Args:
        query (str): The query to build the prompt for.
        slide_json (Dict[str, Any]): The JSON data for the slide.
        content_images (List[str], optional): The list of content images. Defaults to [].
        template_dir (Path, optional): The path to the template directory. Defaults to None.

    Returns:
        str: The prompt for the query.
    """
    divider = "#" * 80
    example_json_str = json.dumps(GENERATION_EXAMPLES, indent=2)
    prompt = ""
    prompt += f"{query}\n"
    prompt += get_api_list_prompt()
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
    if template_dir:
        try:
            prompt += get_slide_layout_examples(template_dir) + "\n"
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Warning: Could not load slide layout examples: {e}")
    prompt += f"Query: {query}\n"
    prompt += "Answer:\n"

    return prompt


def main() -> None:
    """Test the prompt generation functionality with a sample input."""
    test_case = {
        "task": "text_to_slide",
        "query": "Create a slide about Python programming",
        "texts": [
            "Python is a popular programming language.",
            "It's known for its simplicity and readability.",
        ],
        "slide_json": {"texts": ["Sample text"]},
        "content_images": [],
    }

    print(f"\n{'='*40} Test Case: {test_case['task']} {'='*40}")
    print(f"Task: {test_case['task']}")
    try:
        prompt = build_prompt(
            query=test_case["query"],
            task=test_case["task"],
            slide_json=test_case["slide_json"],
            content_images=test_case["content_images"],
        )
        print("\nGenerated Prompt:")
        print(f"{'-'*80}\n{prompt}\n{'-'*80}")
    except Exception as e:
        print(f"Error generating prompt: {str(e)}")


if __name__ == "__main__":
    main()
