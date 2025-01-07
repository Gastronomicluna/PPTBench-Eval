from typing import Any, Dict


def build_prompt(
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
    divider = "#" * 10
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

