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
Task: You are given a slide from a presentation in the form of an image and json data.
{query}. Only return the requested information.
{divider}
Slide: {slide_json}
{divider}
Answer:
"""
    return prompt


def build_prompt_for_layout_detection(
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
Task: You are given a slide from a presentation in the form of an image and json data.
{query}. Only return the requested information.
{divider}
Slide: {slide_json}
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
Task: You are given a slide from a presentation in the form of an image and json data.
{query}. Only return the requested information.
{divider}
Slide: {slide_json}
{divider}
Answer:
"""
    return prompt


if __name__ == "__main__":
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
