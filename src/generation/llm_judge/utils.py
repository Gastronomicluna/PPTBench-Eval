import re
from typing import Optional


def extract_score(response: str) -> Optional[int]:
    """
    Extracts the final score in the format [[x]] from the LLM response.

    Args:
        response (str): The full response from the model.

    Returns:
        int or None: The extracted score as an integer if found and valid, otherwise None.
    """
    match = re.search(r"\[\[(\d)\]\]", response)
    if match:
        score = int(match.group(1))
        if 0 <= score <= 5:
            return score
    return None
