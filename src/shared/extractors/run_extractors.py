# pptbench/extractors/run_extractors.py

import logging
import os

from pptx import Presentation

from pptbench.extractors.ppt_extractor import PowerPointShapeExtractor

# Configure logging to include DEBUG level
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_extractors(pptx_path: str, measurement_unit: str = "pt") -> dict:
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
    import json
    from pathlib import Path

    # Directory containing PowerPoint files
    input_dir = Path(
        "/Users/tyrionhuu/projects/research_projects/PPTBench-Eval/layout_examples"
    )

    # Directory to save extraction results
    output_dir = Path(
        "/Users/tyrionhuu/projects/research_projects/PPTBench-Eval//extracted_data"
    )
    output_dir.mkdir(exist_ok=True)

    # Get all PowerPoint files
    pptx_files = list(input_dir.glob("*.pptx"))
    logger.info(f"Found {len(pptx_files)} PowerPoint files to process")

    # Process each file
    for pptx_file in pptx_files:
        logger.info(f"Processing {pptx_file.name}")

        try:
            # Extract data
            extracted_data = run_extractors(str(pptx_file))

            # Save as JSON
            output_file = output_dir / f"{pptx_file.stem}.json"
            with open(output_file, "w") as f:
                json.dump(extracted_data, f, indent=2)

            logger.info(f"Saved to {output_file}")

        except Exception as e:
            logger.error(f"Error processing {pptx_file.name}: {str(e)}")

    logger.info("All files processed")
