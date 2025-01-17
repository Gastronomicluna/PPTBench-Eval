from typing import List, Optional

from ..shared.pptx_api.api_executor import api_executor


def modify_pptx(
    api_list: List[str],
    pptx_path: str,
    output_path: str,
) -> Optional[List[str]]:
    """
    Modify the presentation file in place.

    Args:
        pptx_path (Union[Path, str]): Path to the presentation file.
        overwrite (bool): Whether to overwrite the input file.

    Returns:
        None
    """
    errors = api_executor(api_list, pptx_path, output_path)
    return errors
