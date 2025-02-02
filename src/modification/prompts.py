import json
from typing import Any, Dict, Literal, Optional

from ..shared.pptx_api.api_doc import api_list
from ..shared.utils import api_to_string
from .utils import get_font_from_shape

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
    task: Optional[str] = None,
    shape_to_modify: Optional[Any] = None,
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
    if not isinstance(slide_json, dict):
        raise ValueError("slide_json must be a dictionary.")

    if subcategory == "element_modification":
        return build_prompt_element_modification(
            query=query,
            task=task,
            slide_json=slide_json,
            shape_to_modify=shape_to_modify,
        )
    elif subcategory == "refinement":
        return build_prompt_refinement(query, slide_json)
    elif subcategory == "text_modification":
        return build_prompt_text_modification(query, slide_json)
    else:
        raise ValueError(f"Invalid subcategory: {subcategory}")


def build_prompt_element_modification(
    query: str,
    task: Literal["add_shape", "resize_shape", "reposition_shape"],
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
    if not isinstance(shape_to_modify, dict) and shape_to_modify is not None:
        raise ValueError("shape_to_modify must be a dictionary.")

    if task == "add_shape":
        return build_prompt_add_shape(query, slide_json, shape_to_modify)
    elif task == "resize_shape" or task == "reposition_shape":
        divider = "#" * 80
        example_json_str = json.dumps(MODIFICATION_EXAMPLE, indent=2)

        prompt = ""
        prompt += "Task: You are given a slide from a presentation in the form of an image and JSON data.\n"
        prompt += f"{query}\n"
        prompt += "To achieve this task, you can use the following functions:\n"
        prompt += f"{api_to_string(api_list)}\n\n"
        prompt += "Required format:\n"
        prompt += "- Return ONLY a valid JSON dictionary\n"
        prompt += "- No explanation text before or after the JSON\n"
        prompt += "- No markdown formatting\n\n"
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


def build_prompt_add_shape(
    query: str,
    slide_json: Dict[str, Any],
    shape_to_add: Dict[str, Any],
) -> str:
    """
    Builds a prompt for the model based on the query and slide JSON, instructing the model to add a shape to the slide.

    Args:
        query (str): The query text.
        slide_json (dict): The JSON data for the slide.
        shape_to_add (dict): The shape to add.

    Returns:
        str: The prompt text.
    """
    divider = "#" * 80
    example_json_str = json.dumps(MODIFICATION_EXAMPLE, indent=2)
    if "text" in shape_to_add:
        text_content = build_add_shape_text_content(shape_to_add)
    elif "image_path" in shape_to_add:
        text_content = build_add_shape_image_content(shape_to_add)
    else:
        raise ValueError("Shape to add must contain either 'text' or 'image_path'.")

    prompt = ""
    prompt += "Task: You are given a slide from a presentation in the form of an image and JSON data.\n"
    prompt += f"{query}\n"
    prompt += "To achieve this task, you can use the following functions:\n"
    prompt += f"{api_to_string(api_list)}\n\n"
    prompt += "Required format:\n"
    prompt += "- Return ONLY a valid JSON dictionary\n"
    prompt += "- No explanation text before or after the JSON\n"
    prompt += "- No markdown formatting\n\n"
    prompt += "Examples:\n"
    prompt += f"{example_json_str}\n\n"
    prompt += f"{divider}\n"
    prompt += "Slide JSON:\n"
    prompt += f"{json.dumps(slide_json, indent=2)}\n\n"
    prompt += f"{divider}\n"
    prompt += f"Query: {query}\n"
    prompt += f"{text_content}\n"
    prompt += "Answer:\n"
    return prompt


def build_add_shape_text_content(
    shape_to_add: Dict[str, Any],
) -> str:
    """
    Builds the text content for a shape to add to the slide.

    Args:
        shape_to_add (dict): The shape to add.

    Returns:
        str: The text content for the shape.
    """
    text = shape_to_add["text"]
    result = f"Add a shape to the slide with the following text: '{text}'.\n"

    font_set = get_font_from_shape(shape_to_add)

    if len(font_set) > 1:
        return result
    else:
        font_name = font_set.pop()
        result += f" The font used should be '{font_name}'."
        return result


def build_add_shape_image_content(
    shape_to_add: Dict[str, Any],
) -> str:
    """
    Builds the image content for a shape to add to the slide.

    Args:
        shape_to_add (dict): The shape to add.

    Returns:
        str: The image content for the shape.
    """
    # if not isinstance(shape_to_add, dict):
    #     raise ValueError("shape_to_add must be a dictionary.")
    image_path = shape_to_add["image_path"]
    result = f"Add a shape to the slide with the following image: '{image_path}'.\n"
    return result


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
    prompt += "Required format:\n"
    prompt += "- Return ONLY a valid JSON dictionary\n"
    prompt += "- No explanation text before or after the JSON\n"
    prompt += "- No markdown formatting\n\n"
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
    prompt += "Required format:\n"
    prompt += "- Return ONLY a valid JSON dictionary\n"
    prompt += "- No explanation text before or after the JSON\n"
    prompt += "- No markdown formatting\n\n"
    prompt += "Examples:\n"
    prompt += f"{example_json_str}\n\n"
    prompt += f"{divider}\n"
    prompt += "Slide JSON:\n"
    prompt += f"{json.dumps(slide_json, indent=2)}\n\n"
    prompt += f"{divider}\n"
    prompt += f"Query: {query}\n"
    prompt += "Answer:\n"
    return prompt


def main() -> None:
    print(build_prompt_refinement("Refine the slide.", {"slide": "data"}))


if __name__ == "__main__":
    main()
