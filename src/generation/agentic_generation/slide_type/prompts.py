from typing import Any, Dict

from src.shared.pptx_api.api_doc import (
    ADD_SHAPE_API_LIST,
    CHOOSE_API_LIST,
    INSERT_API_LIST,
)

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

    # Adding CHOOSE_API_LIST to the available APIs
    for api in CHOOSE_API_LIST:
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


def build_fill_content_prompt(input_data: str, slide_json: Dict[str, Any]) -> str:
    """
    Generate a prompt for filling content into a predefined slide layout.

    Args:
        input_data (str): The content that needs to be placed into the slide.
        slide_json (Dict[str, Any]): The JSON representation of the slide layout.

    Returns:
        str: A well-structured prompt to guide content placement into the layout.
    """
    prompt = ""
    prompt += "Your task is to fill the provided slide layout with the given content. "
    prompt += "You need to distribute the content appropriately among the available shapes and text boxes in the layout.\n\n"

    prompt += f"{DIVIDER}\n\n"

    # Adding the content of the slide as part of the prompt
    prompt += "### Content to Place in the Slide:\n"
    prompt += f"{input_data}\n\n"

    prompt += f"{DIVIDER}\n\n"

    # Adding the slide layout information
    prompt += "### Slide Layout Structure:\n"
    prompt += "Below is the current layout of the slide with placeholders for content. "
    prompt += (
        "You need to determine what content goes where based on the structure.\n\n"
    )
    prompt += f"{slide_json}\n\n"

    prompt += f"{DIVIDER}\n\n"

    # Adding available APIs for content insertion and selection
    prompt += "### Available APIs for Content Placement:\n"
    prompt += (
        "You can use the following APIs to place content into the slide layout:\n\n"
    )

    # Adding CHOOSE_API_LIST to the available APIs
    prompt += "#### Selection APIs:\n"
    for api in CHOOSE_API_LIST:
        prompt += f"- **{api.name}**\n"
        prompt += f"  - **Description**: {api.description}\n"
        prompt += f"  - **Parameters**: {api.parameters_description}\n"
        prompt += f"  - **Notes**: {api.notes}\n"
        prompt += f"  - **Example**: {api.example}\n"
        prompt += "\n"

    # Adding INSERT_API_LIST to the available APIs
    prompt += "#### Insertion APIs:\n"
    for api in INSERT_API_LIST:
        prompt += f"- **{api.name}**\n"
        prompt += f"  - **Description**: {api.description}\n"
        prompt += f"  - **Parameters**: {api.parameters_description}\n"
        prompt += f"  - **Notes**: {api.notes}\n"
        prompt += f"  - **Example**: {api.example}\n"
        prompt += "\n"

    prompt += f"{DIVIDER}\n\n"

    prompt += "### Content Placement Instructions:\n"
    prompt += "- Analyze the slide layout and identify appropriate places for different parts of the content.\n"
    prompt += "- Use the Selection APIs to choose where to place content and the Insertion APIs to add content.\n"
    prompt += "- Ensure that the content is distributed logically across the slide.\n"
    prompt += (
        "- Maintain readability and visual hierarchy in your placement decisions.\n"
    )
    prompt += "- If there's any content that doesn't fit naturally, suggest modifications to either the content or layout.\n"
    prompt += "- Return a structured response indicating what content should go in which placeholder.\n\n"

    prompt += "Answer: "

    return prompt


def build_feedback_prompt(slide_json: Dict[str, Any]) -> str:
    """
    Generate a prompt for providing feedback on a slide layout.

    Args:
        slide_json (Dict[str, Any]): The JSON representation of the slide layout.

    Returns:
        str: A well-structured prompt to guide feedback on the slide layout.
    """
    prompt = ""
    prompt += "Your task is to provide feedback on the given slide layout. "
    prompt += "Analyze the structure, design, and content placement in the slide and provide constructive feedback based on best practices.\n\n"

    prompt += f"{DIVIDER}\n\n"

    # Adding the slide layout information
    prompt += "### Slide Layout Structure:\n"
    prompt += "Below is the current layout of the slide with placeholders for content. "
    prompt += "Analyze the structure and design elements to provide feedback on the layout.\n\n"
    prompt += f"{slide_json}\n\n"

    prompt += f"{DIVIDER}\n\n"

    # Adding available APIs for content insertion and selection
    prompt += "### Feedback Guidelines:\n"
    prompt += "When providing feedback, consider the following aspects of the slide layout:\n\n"
    prompt += "- **Content Placement**: Evaluate how well the content is distributed across the slide.\n"
    prompt += "- **Visual Hierarchy**: Assess the visual hierarchy of the content and design elements.\n"
    prompt += (
        "- **Readability**: Check if the content is easy to read and understand.\n"
    )
    prompt += "- **Design Elements**: Comment on the use of shapes, text boxes, images, and other design elements.\n"
    prompt += "- **Consistency**: Look for consistency in design, font usage, color schemes, etc.\n"
    prompt += "- **Overall Impact**: Consider the overall impact and effectiveness of the slide layout.\n\n"

    prompt += "Provide detailed feedback on the layout, highlighting both strengths and areas for improvement. "
    prompt += "Suggest specific changes or modifications that could enhance the layout's visual appeal and effectiveness.\n\n"

    prompt += "Feedback: "

    return prompt
