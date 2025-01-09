from ..shared.parse_answer import parse_json_answer
from typing import Dict, Any, Union
def format_content_extraction_answer(
    answer: str,
) -> str:
    """
    Format the extracted content for content extraction tasks.

    Args:
        answer (str): The extracted content.

    Returns:
        str: The formatted answer.
    """
    json_answer = parse_json_answer(answer)
    answer = json_answer["answer"]
    return answer

def format_style_detection_answer(
    answer: str,
) -> Union[str, int]:
    """
    Format the extracted style for style detection tasks.

    Args:
        answer (str): The extracted style.

    Returns:
        Union[str, int]: The formatted answer.
    """
    json_answer = parse_json_answer(answer)
    answer = json_answer["answer"]
    return answer

def format_layout_detection_answer(
    answer: str,
) -> Dict[str, Any]:
    """
    Format the detected layout for layout detection tasks.

    Args:
        answer (str): The detected layout.

    Returns:
        Dict[str, int]: The formatted answer.
    """
    json_answer = parse_json_answer(answer)
    return json_answer