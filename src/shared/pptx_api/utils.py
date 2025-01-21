import os
import subprocess
from typing import List

from pdf2image import convert_from_path
from pptx.presentation import Presentation
from pptx.slide import Slide

from .api_doc import api_list


def pptx_to_png(
    pptx_path: str,
    output_dir: str,
    dpi: int = 300,
    remove_pdf: bool = True,
) -> None:
    """
    Convert a PowerPoint file to PNG images.

    Args:
        pptx_path (str): The path to the PowerPoint file.
        output_dir (str): The directory to save the PNG images.
        dpi (int, optional): The DPI of the PNG images. Defaults to 300.
        remove_pdf (bool, optional): Whether to remove the PDF file after conversion. Defaults to True.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    # Create presentation-specific directory
    pptx_name = os.path.splitext(os.path.basename(pptx_path))[0]
    ppt_output_dir = os.path.join(output_dir, pptx_name)
    os.makedirs(ppt_output_dir, exist_ok=True)

    # 1. Convert PPTX -> PDF using unoconv
    # -------------------------------------------------
    # By default, unoconv will create a PDF with the same base filename
    # but with a .pdf extension in the same folder as the input PPTX.
    base_name, _ = os.path.splitext(pptx_path)
    pdf_path = f"{base_name}.pdf"

    print(f"Converting {pptx_path} to PDF...")
    subprocess.run(["unoconv", "-f", "pdf", pptx_path], check=True)
    print(f"Created PDF: {pdf_path}")

    # 2. Convert PDF -> Images (one per PDF page) using pdf2image
    # -----------------------------------------------------------
    print(f"Converting PDF pages to images at {dpi} DPI...")
    pages = convert_from_path(pdf_path, dpi=dpi)

    for i, page in enumerate(pages):
        # Save each page as a PNG (you could choose 'JPEG' if preferred)
        output_filename = os.path.join(ppt_output_dir, f"slide_{i+1}.png")
        page.save(output_filename, "PNG")
        print(f"Saved image: {output_filename}")

    # 3. Optionally remove the intermediate PDF
    # -----------------------------------------
    if remove_pdf and os.path.exists(pdf_path):
        os.remove(pdf_path)
        print(f"Removed intermediate PDF: {pdf_path}")

    print("Conversion complete!")


def get_slide_ids(
    presentation: Presentation,
) -> List[int]:
    """Get the slide ids of a presentation.

    Args:
        presentation: The presentation to get the slide ids of.

    Returns:
        The slide ids of the presentation.
    """
    slide_ids = []
    for slide in presentation.slides:
        slide_ids.append(slide.slide_id)
    return slide_ids


def get_shape_ids(
    slide: Slide,
) -> List[int]:
    """Get the shape ids of a slide.

    Args:
        slide: The slide to get the shape ids of.

    Returns:
        The shape ids of the slide.
    """
    shape_ids = []
    for shape in slide.shapes:
        shape_ids.append(shape.shape_id)
    return shape_ids


def api_in_list(
    line: str,
) -> bool:
    """Parse an API from a line.

    Args:
        line: The line to parse the API from.

    Returns:
        The parsed API.
    """
    for api in api_list:
        if api.name == line:
            return True
    return False
