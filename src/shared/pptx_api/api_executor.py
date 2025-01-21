from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Union

from .api_executor_json import api_executor_json
from .api_executor_pptx import api_executor_pptx


def api_executor(
    lines: List[str],
    pptx_path: Optional[Union[str, Path]] = None,
    json_path: Optional[Union[str, Path]] = None,
    output_path: Optional[Union[str, Path]] = None,
    json: Optional[Dict[str, Any]] = None,
    mode: Literal["pptx", "json"] = "pptx",
) -> Optional[Dict[str, Any]]:
    """
    Execute the API commands and return the result.

    Args:
        lines (List[str]): List of API commands.
        pptx_path (Optional[Union[str, Path]], optional): Path to the PowerPoint file. Defaults to None.
        json_path (Optional[Union[str, Path]], optional): Path to the JSON file. Defaults to None.
        output_path (Optional[Union[str, Path]], optional): Path to save the output file. Defaults to None.
        json (Optional[Dict[str, Any]], optional): JSON data to use. Defaults to None.
        mode (Literal["pptx", "json"], optional): Mode to execute the commands. Defaults to "pptx".

    Returns:
        Optional[Dict[str, Any]]: The result of the API commands.
    """
    # Convert Path objects to strings for compatibility with existing functions
    pptx_path_str = str(pptx_path) if pptx_path is not None else None
    json_path_str = str(json_path) if json_path is not None else None
    output_path_str = str(output_path) if output_path is not None else None

    if mode == "pptx":
        return api_executor_pptx(
            lines=lines,
            pptx_path=pptx_path_str,
            output_path=output_path_str,
        )
    elif mode == "json":
        return api_executor_json(
            lines=lines,
            json_path=json_path_str,
            output_path=output_path_str,
            json=json,
        )
    else:
        raise ValueError(f"Invalid mode: {mode}")
