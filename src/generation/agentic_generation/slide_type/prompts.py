from src.shared.pptx_api.api_doc import ADD_SHAPE_API_LIST

DIVIDER = "*" * 50


def build_create_layout_prompt() -> str:
    """
    Generate a detailed prompt for designing a layout using the available APIs,
    with the input data serving as a guide for the structure and layout elements.

    Returns:
        str: A well-structured prompt to guide the layout creation using available APIs.
    """
    prompt = ""
    prompt += "Your task is to design a layout based on the provided guidelines. "
    prompt += "The layout should incorporate an image as the background and should follow the structure based on the input data's key message.\n\n"

    prompt += f"{DIVIDER}\n\n"

    prompt += "### Available APIs for Layout Creation:\n"
    prompt += "You can use the following APIs to build the layout. Each API serves a specific purpose for adding various shapes, text, and other elements to the slide.\n"
    for api in ADD_SHAPE_API_LIST:
        prompt += f"- **{api.name}**\n"
        prompt += f"  - **Description**: {api.description}\n"
        prompt += f"  - **Parameters**: {api.parameters_description}\n"
        prompt += f"  - **Notes**: {api.notes}\n"
        prompt += f"  - **Example**: {api.example}\n"
        prompt += "\n"

    prompt += f"{DIVIDER}\n\n"

    prompt += "### Layout Instructions:\n"
    prompt += "Create a layout design using the APIs above. Focus on balancing elements visually while ensuring that the background image complements the overall structure. "
    prompt += "You are encouraged to utilize a variety of shapes and text elements to achieve an effective layout that aligns with the message structure of the provided content.\n"

    prompt += "Answer: "

    return prompt
