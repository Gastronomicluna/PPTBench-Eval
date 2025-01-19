import json
from typing import Any, Dict, Literal, Optional

from ..shared.pptx_api.api_doc import api_list
from ..shared.utils import api_to_string

# JSON templates for examples
MODIFICATION_EXAMPLE = {
    "function1": "choose_slide(0)",
    "function2": "choose_shape(1)",
    "function3": "set_width(1000000)",
    "function4": "insert_text('Hello, World!')",
}


def build_prompt(
    query: str,
    slide_json: Dict[str, Any],
    subcategory: Literal["element_modification", "refinement", "text_modification"],
    shape_to_modify: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Builds a prompt for the model based on the query and slide JSON.

    Args:
        query (str): The query text.
        slide_json (dict): The JSON data for the slide.
        subcategory (str): The subcategory of the modification task.
        shape_to_modify (dict): The shape to modify, if applicable.

    Returns:
        str: The prompt text.
    """
    if subcategory == "element_modification":
        return build_prompt_element_modification(query, slide_json, shape_to_modify)
    elif subcategory == "refinement":
        return build_prompt_refinement(query, slide_json)
    elif subcategory == "text_modification":
        return build_prompt_text_modification(query, slide_json, shape_to_modify)
    else:
        raise ValueError(f"Invalid subcategory: {subcategory}")


def build_prompt_element_modification(
    query: str,
    slide_json: Dict[str, Any],
    shape_to_modify: Dict[str, Any],
) -> str:
    """
    Builds a prompt for the model based on the query and slide JSON, instructing the model to modify an element in the slide.

    Args:
        query (str): The query text.
        slide_json (dict): The JSON data for the slide.
        shape_to_modify (dict): The shape to modify.

    Returns:
        str: The prompt text.
    """
    divider = "#" * 80
    example_json_str = json.dumps(MODIFICATION_EXAMPLE, indent=2)

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
    prompt += f"Shape to Modify: {json.dumps(shape_to_modify, indent=2)}\n"
    prompt += "Answer:\n"

    return prompt


def build_prompt_refinement(
    query: str,
    slide_json: Dict[str, Any],
) -> str:
    """
    Builds a prompt for the model based on the query and slide JSON, instructing the model to return the answer in JSON format.

    Args:
        query (str): The query text.
        slide_json (dict): The JSON data for the slide.

    Returns:
        str: The prompt text.
    """
    divider = "#" * 80
    example_json_str = json.dumps(MODIFICATION_EXAMPLE, indent=2)

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


def build_prompt_text_modification(
    query: str,
    slide_json: Dict[str, Any],
    shape_to_modify: Dict[str, Any],
) -> str:
    """
    Builds a prompt for the model based on the query and slide JSON, instructing the model to modify the text in the slide.

    Args:
        query (str): The query text.
        slide_json (dict): The JSON data for the slide.
        shape_to_modify (dict): The shape to modify.

    Returns:
        str: The prompt text.
    """
    divider = "#" * 80
    example_json_str = json.dumps(MODIFICATION_EXAMPLE, indent=2)

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
    prompt += f"Shape to Modify: {json.dumps(shape_to_modify, indent=2)}\n"
    prompt += "Answer:\n"
    return prompt


def main() -> None:
    api_str = api_to_string(api_list)
    print(api_str)


if __name__ == "__main__":
    main()
