from typing import Any, Dict, List

from ..shared.pptx_api.api_doc import API, api_list


def build_prompt(
    query: str,
    shape_to_modify: Dict[str, Any],
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
    prompt = f"""
{divider}
Task: You are given a slide from a presentation in the form of an image and JSON data.
{query}
To achieve this task, you can use the following functions:
{api_to_string(api_list)}

Instructions:
- Return in JSON format only the requested information without any additional text or explanations.
- Abide by JSON formatting rules.

Examples:
{{
    "function1": "choose_slide(0)",
    "function2": "choose_shape(1)",
    "function3": "set_width(1000000)",
    "function4": "insert_text('Hello, World!')",
}}

{divider}
Slide JSON:
{slide_json}

{divider}
Query: {query}
Shape to Modify: {shape_to_modify}

Answer:
"""
    return prompt


def api_to_string(
    api_list: List[API],
) -> str:
    """
    Convert a list of API objects to a string representation.

    Args:
        api_list (list): List of API objects.

    Returns:
        str: String representation of the API list.
    """
    api_strings = []
    for api in api_list:
        # Format each API with essential information only
        api_str = (
            f"{api.name}({api.parameters}) "
            + f"Description: {api.description} "
            + f"Notes: {api.notes}"
        )

        api_strings.append(api_str)

    # Join all API strings with clear separation
    return "\n".join(api_strings)


def main() -> None:
    api_str = api_to_string(api_list)
    print(api_str)


if __name__ == "__main__":
    main()
