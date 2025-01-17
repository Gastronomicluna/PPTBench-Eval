from typing import Any, Dict, List, Literal, Optional

from .api_executor_json import api_executor_json
from .api_executor_pptx import api_executor_pptx


def api_executor(
    lines: List[str],
    pptx_path: Optional[str] = None,
    json_path: Optional[str] = None,
    output_path: Optional[str] = None,
    json: Optional[Dict[str, Any]] = None,
    mode: Literal["pptx", "json"] = "pptx",
) -> Optional[Dict[str, Any]]:
    """
    Execute the API commands and return the result.

    Args:
        lines (List[str]): List of API commands.
        pptx_path (Optional[str], optional): Path to the PowerPoint file. Defaults to None.
        output_path (Optional[str], optional): Path to save the modified PowerPoint file. Defaults to None.
        mode (Literal["pptx", "json"], optional): Mode to execute the commands. Defaults to "pptx".

    Returns:
        Optional[Dict[str, Any]]: The result of the API commands.
    """
    if mode == "pptx":
        return api_executor_pptx(
            lines=lines,
            pptx_path=pptx_path,
            output_path=output_path,
        )
    elif mode == "json":
        return api_executor_json(
            lines=lines,
            json_path=json_path,
            output_path=output_path,
            json=json,
        )
    else:
        raise ValueError(f"Invalid mode: {mode}")
