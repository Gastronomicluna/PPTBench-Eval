from typing import Any, Dict, Optional

from src.shared.pptx_api.api_doc import (
    ADD_SHAPE_API_LIST,
    CHOOSE_API_LIST,
    INSERT_API_LIST,
)

DIVIDER = "*" * 50


def build_create_layout_prompt(input_data: str, image: bool = True) -> str:
    """
    Generate a detailed prompt for designing a layout using the available APIs,
    with the content serving as the input and a provided image as the background.

    Args:
        input_data (str): The content of the slide that will guide the layout design.
        image (bool, optional): Whether to include instructions about using
            the provided image as background. Defaults to True.

    Returns:
        str: A well-structured prompt to guide the layout creation using available APIs.
    """
    prompt = ""
    prompt += "Your task is to design a layout based on the provided content. "
    if image:
        prompt += "The layout should incorporate the provided image as the background, and you should structure the content in a visually appealing and organized way.\n\n"
    else:
        prompt += "You should structure the content in a visually appealing and organized way.\n\n"

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
    if image:
        prompt += "The background image is already provided, so your task is to structure the content around it, ensuring it complements the image. "
    prompt += "Use shapes, text, and other design elements to emphasize key points, create a balanced flow, and ensure readability.\n"

    prompt += "Answer: "

    return prompt


def build_fill_content_prompt(
    slide_json: Dict[str, Any], input_data: Optional[str] = None, image: bool = True
) -> str:
    """
    Generate a prompt for filling content into a predefined slide layout.

    Args:
        slide_json (Dict[str, Any]): The JSON representation of the slide layout.
        input_data (Optional[str], optional): The content that needs to be placed
            into the slide. Defaults to None.
        image (bool, optional): Whether to include instructions about
            working with images in the slide. Defaults to True.

    Returns:
        str: A well-structured prompt to guide content placement into the layout.
    """
    prompt = ""
    prompt += "Your task is to fill the provided slide layout with the given content. "
    prompt += "You need to distribute the content appropriately among the available shapes and text boxes in the layout.\n\n"

    prompt += f"{DIVIDER}\n\n"

    # Adding the content of the slide as part of the prompt
    if input_data:
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
    if image:
        prompt += "- If there are images in the layout, ensure your content complements them rather than competing with them.\n"
    prompt += (
        "- Maintain readability and visual hierarchy in your placement decisions.\n"
    )
    prompt += "- If there's any content that doesn't fit naturally, suggest modifications to either the content or layout.\n"
    prompt += "- Return a structured response indicating what content should go in which placeholder.\n\n"

    prompt += "Answer: "

    return prompt


def build_feedback_prompt(slide_json: Dict[str, Any]) -> str:
    """
    Generate a simplified prompt for providing feedback on a slide layout.
    The output should be a JSON with a clear indication if major design flaws exist,
    along with overall feedback.

    Args:
        slide_json (Dict[str, Any]): The JSON representation of the slide layout.

    Returns:
        str: A prompt that instructs the reviewer to output feedback in a simplified JSON format.
    """
    prompt = ""
    prompt += "Review the slide layout provided below and offer constructive feedback on its design.\n\n"
    prompt += "Slide Layout:\n"
    prompt += f"{slide_json}\n\n"
    prompt += "Please consider the following aspects:\n"
    prompt += "- Content placement and distribution\n"
    prompt += "- Visual hierarchy and readability\n"
    prompt += "- Use of design elements (e.g., text, images, shapes)\n"
    prompt += "- Consistency in fonts, colors, and style\n"
    prompt += "- Identification of any major flaws (e.g., unreadable text, poor contrast, overcrowding)\n"
    prompt += "- Suggestions for improvement\n\n"
    prompt += "Output your response in the following JSON format exactly:\n\n"
    prompt += "```json\n"
    prompt += "{\n"
    prompt += '  "pass": true/false,\n'
    prompt += '  "feedback": "Your overall feedback including strengths, weaknesses, and suggestions."\n'
    prompt += "}\n"
    prompt += "```\n\n"
    prompt += "Your response: "

    return prompt


def main():
    from src.shared.utils import get_texts_from_json_data

    slide_json = {
        "slide_width": 9144000,
        "slide_height": 6858000,
        "measurement_unit": "emu",
        "slide": {
            "slide_id": 288,
            "slide_name": "",
            "shapes": [
                {
                    "name": "",
                    "shape_id": 117,
                    "shape_type": "PICTURE",
                    "measurement_unit": "emu",
                    "height": 4764240,
                    "width": 7086600,
                    "left": 1066680,
                    "top": 407880,
                    "auto_shape_type": "RECTANGLE",
                    "image_path": "dataset/extracted_images/PASRENDEHQURXKYRMXJNQOK44A7UMSZV/32/image_32_1.png",
                },
                {
                    "name": "",
                    "shape_id": 118,
                    "shape_type": "AUTO_SHAPE",
                    "measurement_unit": "emu",
                    "height": 459720,
                    "width": 7467480,
                    "left": 762120,
                    "top": 5257800,
                    "text": "(page 23; section 3119B.4)",
                    "font_details": [
                        {
                            "paragraph_index": 0,
                            "run_index": 0,
                            "text": "(page 23; section 3119B.4)",
                            "font_name": "Times New Roman",
                            "font_size": 24.0,
                        }
                    ],
                },
            ],
            "notes": {
                "text": "Shall be posted in a prominent place around spa pool.\nRead spa caution sign carefully to make sure it has approved verbiage. Can be more strict- not less.",
                "font_details": [
                    {
                        "paragraph_index": 0,
                        "run_index": 0,
                        "text": "Shall be posted in a prominent place around spa pool.",
                        "font_name": "Times New Roman",
                        "font_size": 12.0,
                    },
                    {
                        "paragraph_index": 1,
                        "run_index": 0,
                        "text": "Read spa caution sign carefully to make sure it has approved verbiage. Can be more strict- not less.",
                        "font_name": "Times New Roman",
                        "font_size": 12.0,
                    },
                ],
            },
        },
    }

    input_data = get_texts_from_json_data(slide_json)
    print(build_create_layout_prompt(input_data))


if __name__ == "__main__":
    main()
