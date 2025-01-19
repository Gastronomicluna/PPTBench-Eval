import json
from typing import Any, Dict, Literal

# JSON templates for examples
CONTENT_EXTRACTION_EXAMPLE = {
    "answer": "Emergency Clean Water Grant Fund Prop 84, Chapter 2 Public Resources Code Section 75021"
}

STYLE_FONT_EXAMPLE = {"answer": "Arial"}
STYLE_SIZE_EXAMPLE = {"answer": 2.0}

LAYOUT_TEMPLATE = {
    "left": "<integer>",
    "top": "<integer>",
    "width": "<integer>",
    "height": "<integer>",
}


def build_prompt(
    query: str,
    slide_json: Dict[str, Any],
    subcategory: Literal["content extraction", "layout detection", "style detection"],
) -> str:
    """
    Builds a prompt for the model based on the query and slide JSON.

    Args:
        query (str): The query text.
        slide_json (dict): The JSON data for the slide.
        subcategory (str): The subcategory of the detection task.

    Returns:
        str: The prompt text.
    """
    if subcategory == "content extraction":
        return build_prompt_for_content_extraction(query, slide_json)
    elif subcategory == "layout detection":
        return build_prompt_for_layout_detection(query, slide_json)
    elif subcategory == "style detection":
        return build_prompt_for_style_detection(query, slide_json)
    else:
        raise ValueError(f"Invalid subcategory: {subcategory}")


def build_prompt_for_content_extraction(
    query: str,
    slide_json: Dict[str, Any],
) -> str:
    """
    Builds a prompt for the model based on the query and slide JSON.

    Args:
        query (str): The query text.
        slide_json (dict): The JSON data for the slide.

    Returns:
        str: The prompt text.
    """
    divider = "#" * 80
    example_json_str = json.dumps(CONTENT_EXTRACTION_EXAMPLE, indent=2)

    prompt = "\n"
    prompt += f"{divider}\n"
    prompt += "Task: You are given a slide from a presentation in the form of an image and JSON data.\n"
    prompt += f"{query}\n\n"
    prompt += "**Instructions:**\n"
    prompt += "- Extract **only** the requested information based on the query.\n"
    prompt += "- Do **not** include any additional text, explanations, or labels.\n"
    prompt += '- Provide the response in JSON format with the key "answer" and the value being the extracted content.\n\n'
    prompt += "**Example:**\n"
    prompt += 'If the query is "title_extraction" and the ground truth is "Emergency Clean Water Grant Fund Prop 84, Chapter 2 Public Resources Code Section 75021",\n'
    prompt += f"Answer:\n{example_json_str}\n"
    prompt += f"{divider}\n"
    prompt += "Slide JSON:\n"
    prompt += json.dumps(slide_json, indent=2) + "\n\n"
    prompt += f"{divider}\n"
    prompt += 'Answer (Please provide a JSON object with the key "answer" and the value being the extracted content, without any additional text):\n'
    return prompt


def build_prompt_for_style_detection(
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
    font_example_str = json.dumps(STYLE_FONT_EXAMPLE, indent=2)
    size_example_str = json.dumps(STYLE_SIZE_EXAMPLE, indent=2)

    prompt = "\n"
    prompt += f"{divider}\n"
    prompt += "Task: You are given a slide from a presentation in the form of an image and JSON data.\n\n"
    prompt += f"{query}. Provide only the requested information in JSON format without any additional text or explanations.\n\n"
    prompt += "Examples:\n"
    prompt += "Query: Identify the dominant font in the slide.\n"
    prompt += f"Answer:\n{font_example_str}\n\n"
    prompt += "Query: Identify the difference of the largest and the smallest font size excluding the notes section.\n"
    prompt += f"Answer:\n{size_example_str}\n\n"
    prompt += f"{divider}\n"
    prompt += f"Slide JSON: {json.dumps(slide_json, indent=2)}\n\n"
    prompt += f"{divider}\n"
    prompt += f"Query: {query}\n"
    prompt += 'Answer (Please provide a JSON object with the key "answer" and the value being the answer to the query, without any additional text):\n'
    return prompt


def build_prompt_for_layout_detection(
    query: str,
    slide_json: Dict[str, Any],
) -> str:
    """
    Builds a prompt for the model based on the query and slide JSON,
    ensuring the response is in a specific JSON format.

    Args:
        query (str): The query text.
        slide_json (dict): The JSON data for the slide.

    Returns:
        str: The prompt text.
    """
    divider = "#" * 80
    layout_template_str = json.dumps(LAYOUT_TEMPLATE, indent=2)

    prompt = "\n"
    prompt += f"{divider}\n"
    prompt += "Task: You are given a slide from a presentation in the form of an image and JSON data.\n"
    prompt += f"{query}. Only return the requested information in the following JSON format:\n"
    prompt += f"{layout_template_str}\n"
    prompt += (
        "Ensure that all values are integers and the JSON is properly formatted.\n\n"
    )
    prompt += f"{divider}\n"
    prompt += f"Slide: {json.dumps(slide_json, indent=2)}\n\n"
    prompt += f"{divider}\n"
    prompt += f"Query: {query}\n"
    prompt += "Answer:\n"
    return prompt


def main() -> None:
    from src.shared.load_save_dataset import load_save_huggingface_dataset_df

    dataset_name = "tyrionhuu/PPTBench-Detection"
    dataset_path = "data/PPTBench-Detection"

    df = load_save_huggingface_dataset_df(
        dataset_name=dataset_name,
        dataset_path=dataset_path,
        force_download=False,
    )
    # Print complete header
    # print(df.columns)
    seed = 42
    row = df.sample(random_state=seed).iloc[0]
    description = row["description"]
    json_data = row["json_data"]
    # print(json_data)
    prompt = build_prompt(description, json_data)
    print(prompt)


if __name__ == "__main__":
    main()
