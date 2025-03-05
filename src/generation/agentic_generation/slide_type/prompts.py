from src.shared.pptx_api.api_doc import ADD_SHAPE_API_LIST

DIVIDER = "*" * 50


def build_create_layout_prompt(input_data: str) -> str:
    """
    Given a string of input data, return a well-structured prompt to create a layout for the content.

    Args:
        input_data (str): The input data that will inform the layout creation.

    Returns:
        str: A structured prompt requesting the layout design and the necessary elements.
    """
    prompt = ""
    prompt += "You are tasked with creating a layout with the following suggestion. "
    prompt += "You are also provided with an image as the background for the slide. "
    prompt += "Your design should be based on the structure and key message of the input data.\n"
    prompt += DIVIDER + "\n"
    prompt += "Input Data:\n"
    prompt += input_data + "\n"
    prompt += DIVIDER + "\n"
    prompt += "You can and can only use the following APIs to create the layout:\n"
    for api in ADD_SHAPE_API_LIST:
        prompt += f"- {api.name}\n"
        prompt += f"  - Description: {api.description}\n"
        prompt += f"  - Parameters: {api.parameters_description}\n"
        prompt += f"  - Notes: {api.notes}\n"
        prompt += f"  - Example: {api.example}\n"
        prompt += "\n"
    prompt += DIVIDER + "\n"
    prompt += "Please design the layout based on the input data and the provided APIs."
    prompt += "Answer: "

    return prompt
