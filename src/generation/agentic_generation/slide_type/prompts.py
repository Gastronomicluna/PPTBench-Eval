from typing import Any, Dict

from src.shared.pptx_api.api_doc import ADD_SHAPE_API_LIST

DIVIDER = "*" * 50


def build_create_layout_prompt(input_data: str) -> str:
    """
    Generate a detailed prompt for designing a layout using the available APIs,
    with the content serving as the input and a provided image as the background.

    Args:
        input_data (str): The content of the slide that will guide the layout design.

    Returns:
        str: A well-structured prompt to guide the layout creation using available APIs.
    """
    prompt = ""
    prompt += "Your task is to design a layout based on the provided content. "
    prompt += "The layout should incorporate the provided image as the background, and you should structure the content in a visually appealing and organized way.\n\n"

    prompt += f"{DIVIDER}\n\n"

    # Adding the content of the slide as part of the prompt
    prompt += "### Slide Content:\n"
    prompt += f"{input_data}\n\n"

    prompt += f"{DIVIDER}\n\n"

    prompt += "### Available APIs for Layout Creation:\n"
    prompt += "You can use the following APIs to build the layout. These APIs will allow you to add shapes, text, and other elements to organize the content effectively.\n"
    for api in ADD_SHAPE_API_LIST:
        prompt += f"- **{api.name}**\n"
        prompt += f"  - **Description**: {api.description}\n"
        prompt += f"  - **Parameters**: {api.parameters_description}\n"
        prompt += f"  - **Notes**: {api.notes}\n"
        prompt += f"  - **Example**: {api.example}\n"
        prompt += "\n"

    prompt += f"{DIVIDER}\n\n"

    prompt += "### Layout Instructions:\n"
    prompt += "Design the layout using the provided content, ensuring the content is organized clearly and efficiently. "
    prompt += "The background image is already provided, so your task is to structure the content around it, ensuring it complements the image. "
    prompt += "Use shapes, text, and other design elements to emphasize key points, create a balanced flow, and ensure readability.\n"

    prompt += "Answer: "

    return prompt


# def build_fill_content_prompt(input_data: str, slide_json: Dict[str, Any]
