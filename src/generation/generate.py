from ..shared.pptx_api.api_executor import api_executor


def generate_pptx(
    api_calls: list[str],
    pptx_path: str,
) -> None:
    """
    Generate a PowerPoint file based on the API calls.

    Args:
        api_calls (List[str]): The API calls to execute.
        pptx_path (str): The path to the PowerPoint file to generate.
    """
    api_executor(
        lines=api_calls,
        pptx_path=pptx_path,
        mode="pptx",
    )


def build_pptx_path(
    base_dir: str,
    task: str,
    hash_str: str,
) -> str:
    """
    Build the path to the PowerPoint file based on the task and hash.

    Args:
        base_dir (str): The base directory for the PowerPoint file.
        task (str): The task name.
        hash_str (str): The hash string.

    Returns:
        str: The path to the PowerPoint file.
    """
    return f"{base_dir}/{task}/{hash_str}.pptx"


def take_screenshot(
    pptx_path: str,
    output_path: str,
) -> None:
    """
    Take a screenshot of the PowerPoint file.

    Args:
        pptx_path (str): The path to the PowerPoint file.
        output_path (str): The path to save the screenshot.
    """
    api_executor(
        lines=[f"take_screenshot('{pptx_path}', '{output_path}')"],
        mode="pptx",
    )