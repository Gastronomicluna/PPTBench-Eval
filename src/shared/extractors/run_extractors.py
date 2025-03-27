# pptbench/extractors/run_extractors.py

import logging
import os

from pptx import Presentation

from .ppt_extractor import PowerPointShapeExtractor

# Configure logging to include DEBUG level
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_extractors(pptx_path: str, measurement_unit: str = "emu") -> dict:
    """Run extractors on the given PowerPoint file.

    Args:
        pptx_path (str): Path to the PowerPoint file.
        measurement_unit (str, optional): Unit of measurement for extraction. Defaults to "pt".

    Returns:
        dict: Extracted information from the PowerPoint file.

    Raises:
        ValueError: If pptx_path is not provided.
        FileNotFoundError: If the file at pptx_path does not exist.
    """
    if not pptx_path:
        raise ValueError("pptx_path is required")
    if not os.path.exists(pptx_path):
        raise FileNotFoundError(f"File not found: {pptx_path}")
    ppt = Presentation(pptx_path)
    shape_extractor = PowerPointShapeExtractor(ppt, measurement_unit)
    extracted_info = shape_extractor.extract_ppt()
    return extracted_info


# Example usage
if __name__ == "__main__":
    pptx_path = "datasets/output.pptx"
    extracted_info = run_extractors(pptx_path)
    print(extracted_info)
