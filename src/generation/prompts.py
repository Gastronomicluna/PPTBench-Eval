from typing import Any, Dict, Literal


def build_prompt(
    query: str,
    slide_json: Dict[str, Any],
) -> str:
    """
    Build the prompt for the given query.

    Args:
        query (str): The query to build the prompt for.
        slide_json (Dict[str, Any]): The JSON data for the slide.

    Returns:
        str: The prompt for the query.
    """
