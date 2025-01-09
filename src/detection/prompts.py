from typing import Any, Dict, Literal


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
    prompt = f"""
{divider}
Task: You are given a slide from a presentation in the form of an image and JSON data.
{query}

**Instructions:**
- Extract **only** the requested information based on the query.
- Do **not** include any additional text, explanations, or labels.
- Provide the response in plain text without any formatting.

**Example:**
If the query is "title_extraction" and the ground truth is "Emergency Clean Water Grant Fund Prop 84, Chapter 2 Public Resources Code Section 75021",
**Do not respond with:** "The title of the slide is: Emergency Clean Water Grant Fund Prop 84, Chapter 2 Public Resources Code Section 75021."
**Instead, respond with:** "Emergency Clean Water Grant Fund Prop 84, Chapter 2 Public Resources Code Section 75021."

{divider}
Slide JSON:
{slide_json}

{divider}
Answer:
"""
    return prompt


def build_prompt_for_style_detection(
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
    prompt = f"""
{divider}
Task: You are given a slide from a presentation in the form of an image and JSON data.

{query}. Provide only the requested information without any additional text or explanations.

Examples:
Query: Identify the dominant font in the slide.
Answer: Arial

Query: Identify the difference of the largest and the smallest font size excluding the notes section.
Answer: 2.0

{divider}
Slide JSON: {slide_json}

{divider}
Answer:
"""
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
    prompt = f"""
{divider}
Task: You are given a slide from a presentation in the form of an image and JSON data.
{query}. Only return the requested information in the following JSON format:
{{
    "left": <integer>,
    "top": <integer>,
    "width": <integer>,
    "height": <integer>
}}
Ensure that all values are integers and the JSON is properly formatted.

{divider}
Slide: {slide_json}

{divider}
Answer:
"""
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
