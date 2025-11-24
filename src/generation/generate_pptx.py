import logging
import os
import traceback
from pathlib import Path
from typing import List, Optional

import pandas as pd

from ..shared.pptx_api.api_executor import api_executor
from ..shared.utils import csv_to_df, df_to_csv, pptx_to_png, str_to_list

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)


def generate_pptx_files_csv(
    csv_path: Path,
    output_dir: Path,
    overwrite: bool = False,
    input_pptx_dir: Optional[Path] = None,
) -> pd.DataFrame:
    """
    Generate PowerPoint files from a CSV file containing API calls.

    Args:
        csv_path (Path): Path to the CSV file containing API calls.
        base_dir (Path): Base directory for input files.
        output_dir (Path): Directory where generated files will be saved.
        overwrite (bool, optional): Whether to overwrite existing files. Defaults to False.

    Returns:
        pd.DataFrame: DataFrame with generated PowerPoint and PNG files information.
    """
    try:
        if not csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")

        df = csv_to_df(csv_path=csv_path)

        if not overwrite:
            df = df[df["pptx_path"].isna() | df["png_path"].isna()]
            if df.empty:
                logger.info("No new files to generate")
                return df

        model_name = csv_path.stem  # derive model_name from CSV file name

        result_df = generate_pptx_files_with_png_files(
            df=df,
            input_pptx_dir=input_pptx_dir,
            output_dir=output_dir,
            model_name=model_name,
        )

        if df_to_csv(df=result_df, csv_path=csv_path):
            return result_df
        else:
            logger.error("Failed to save the updated CSV file")
            return pd.DataFrame()
    except Exception as e:
        logger.error(f"Error processing CSV file: {str(e)}", exc_info=True)
        return pd.DataFrame()


def generate_pptx_files_with_png_files(
    df: pd.DataFrame,
    output_dir: Path,
    model_name: str,
    input_pptx_dir: Optional[Path] = None,
) -> pd.DataFrame:
    """
    Generate the PowerPoint files based on the DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame containing the API calls.
        input_pptx_dir (Path): Base directory for input files.
        output_dir (Path): Directory where generated files will be saved.
        model_name (str): Name of the model being evaluated.

    Returns:
        pd.DataFrame: The DataFrame with the generated PowerPoint files.
    """
    model_dir = output_dir / model_name
    png_dir = model_dir / "png"
    pptx_output_dir = model_dir / "pptx"
    os.makedirs(png_dir, exist_ok=True)
    os.makedirs(pptx_output_dir, exist_ok=True)

    for index, row in df.iterrows():
        try:
            # Convert string representation back to list
            api_calls = str_to_list(row["answer"]) if pd.notna(row["answer"]) else []

            if not api_calls:
                df.at[index, "error"] = "Empty or invalid API calls list"
                continue

            # file_hash = row["file_hash"]
            hash = row["hash"]

            if input_pptx_dir:
                pptx_path = input_pptx_dir / f"{hash}.pptx"
            else:
                pptx_path = None

            output_path = pptx_output_dir / f"{hash}.pptx"
            os.makedirs(output_dir.parent, exist_ok=True)

            if not generate_pptx(
                api_calls=api_calls,
                pptx_path=pptx_path,
                output_path=output_path,
            ):
                error_msg = "Failed to generate PPTX"
                logger.error(f"{error_msg} for index {index}")
                df.at[index, "error"] = error_msg
                continue

            try:
                pptx_to_png(
                    pptx_path=str(output_path),
                    output_dir=str(png_dir),
                    dpi=300,
                    remove_pdf=True,
                )
                df.at[index, "pptx_path"] = str(output_path)
                df.at[index, "png_dir"] = str(png_dir / hash)
                # Only clear error if there wasn't one before
                if pd.isna(row.get("error")):
                    df.at[index, "error"] = None

            except Exception as e:
                error_msg = f"Failed to convert PPTX to PNG: {str(e)}"
                logger.error(f"{error_msg} for index {index}")
                df.at[index, "error"] = error_msg
                continue

        except Exception as e:
            error_msg = f"Error processing row: {str(e)}"
            logger.error(
                f"{error_msg} for index {index}\n"
                f"Traceback:\n{traceback.format_exc()}"
            )
            df.at[index, "error"] = error_msg
            continue

    return df


def generate_pptx(
    api_calls: List[str],
    pptx_path: Optional[Path] = None,
    output_path: Optional[Path] = None,
) -> bool:
    """
    Generate a PowerPoint file based on the API calls.

    Args:
        api_calls (List[str]): The API calls to execute.
        pptx_path (Path): The path to the PowerPoint file to generate.

    Returns:
        bool: True if successful, False otherwise.
    """
    if isinstance(api_calls, list):
        # print(f"api_calls is a list: {api_calls}")
        try:
            api_executor(
                lines=api_calls,
                pptx_path=pptx_path,
                output_path=output_path,
                mode="pptx",
            )
            return True
        except Exception as e:
            logger.error(
                f"Error generating PPTX {pptx_path}: {str(e)}\n"
                f"Traceback:\n{traceback.format_exc()}"
            )
            # print(f"Error generating PPTX {pptx_path}: {str(e)}")
            return False
    else:
        # print(f"api_calls is not a list: {api_calls}")
        return False


def main() -> None:
    output_path = Path("example.pptx")  # 生成的 PPT 文件路径
    pptx_path = None  # 如果不基于已有 PPT 模板，可设为 None

    # 2. API 调用列表
    # api_calls = [
    #     'create_slide(0)',
    #     'choose_slide(256)',
    #     'choose_shape(2)',
    #     "insert_text('U.S. Department of Transportation\\\\nFederal Railroad Administration')",
    #     'choose_shape(3)',
    #     "insert_text('Overview of Proposed Rail Legislation\\\\n\\\\nKevin R. Blackwell\\\\nFRA Hazmat Division\\\\nWashington, DC')"
    # ]

    # api_calls = [
    #     'create_slide(0)',
    #     'choose_slide(256)',
    #     'choose_shape(2)',
    #     "insert_text('Under Dispenser Containment')",
    #     # 'choose_slide(256)',
    #     # 'choose_shape(3)',
    #     # "insert_text('')",
    #     'create_slide(8)',
    #     'choose_slide(257)',
    #     'choose_shape(2)',
    #     "insert_text('Under Dispenser Containment')",
    #     'choose_slide(257)',
    #     'choose_shape(3)',
    #     # "add_picture(1500000, 1000000, 6000000, 4000000, 'dataset/extracted_images/W7RJCH3WN2DEJH5CHAXOMF7RX3AFE3PW/17/image_17_2.jpg')"
    #     "add_picture(141, 48, 432, 324, 'dataset/extracted_images/W7RJCH3WN2DEJH5CHAXOMF7RX3AFE3PW/17/image_17_2.jpg')"
    # ]

    # api_calls = [
    # "create_slide(6)",
    # "add_text_box(0, 0, 960, 150, ' ')",
    # "set_font_color('0D253F')", 
    # "set_font_size(1)",
    
    # "add_text_box(100, 350, 760, 100, 'PROJECT INITIATIVE: Q4 REVIEW')",
    # "set_font_size(40)",
    # "set_font('Lato')",
    # "set_font_color('66ccff')",
    
    # "add_text_box(100, 480, 760, 500, 'A Professional Corporate Presentation')",
    # "set_font_size(24)",
    # "set_font('Lato')",
    # "set_font_color('4A4A4A')",
    # ]
    

    # #title页的函数调用模板
    # api_calls = [
    #     "create_slide(6)",
    #     "add_picture(0, 0, 720, 540, 'dataset/A modern, geometric design featuring a central rounded frame bordered by blocks of navy, pastel pink, and light blue.jpg')", # Background Image
    #     "add_text_box(60, 160, 600, 100, 'Science, Technology, Engineering\\nand Mathematics Talent\\nExpansion Program (STEP)')", # Our Main Title
    #     "set_font_color('483D8B')",
    #     "set_font_size(32)",
    #     'set_text_align("CENTER")',
    #     "set_font(font_name='Arial Black')",

    #     "add_text_box(110, 280, 500, 50, 'National Science Foundation Directorate for Education & Human Resources Division of Undergraduate Education (DUE)')", #our Subtitle Description
    #     "set_font_color('2F4F4F')",
    #     "set_word_wrap(True)",
    #     "set_font_size(24)",
    #     "set_font(font_name='Calibri')",

    #     "add_text_box(210, 415, 300, 30, 'November 18, 2009')",
    #     "set_text_align('CENTER')",
    #     "set_font_color('696969')",
    #     "set_font_size(18)",
    #     "set_font(font_name='Calibri')"
    # ]

    # #分点解释类的ppt模板
    # api_calls = [
    #     "create_slide(6)",
    #     "add_picture(0, 0, 720, 540, 'dataset/A modern, geometric design featuring a central rounded frame bordered by blocks of navy, pastel pink, and light blue.jpg')",
    #     # --- Part 2: 添加和设置页面标题 ---
    #     "add_text_box(80, 70, 560, 60, 'Some Guiding Principles (Water 2025)')",
    #     "set_text_align('CENTER')",
    #     "set_font_color('483D8B')",  # 与主标题颜色一致，保持视觉重点
    #     "set_font_size(28)",
    #     "set_font(font_name='Arial Black')",
    #     # --- Part 3: 添加和设置分点介绍内容 ---
    #     "add_text_box(100, 130, 520, 360, "
    #     "'• Recognize and respect state, tribal, and federal water rights, contracts, and interstate compacts or decrees of the United States Supreme Court that allocate the right to use water.\\n\\n' "
    #     "'• Maintain and modernize existing water facilities so they will continue to provide water and power.\\n\\n' "
    #     "'• Enhance water conservation, use efficiency, and resource monitoring to allow existing water supplies to be used more effectively.\\n\\n')",
    #     "set_text_align('LEFT')",
    #     "set_word_wrap(True)",
    #     "set_font_color('2F4F4F')", 
    #     "set_font_size(22)",
    #     "set_font(font_name='Calibri')"
    # ]



    # #图标+解释类的ppt模板
    # api_calls = [
    #     # --- Part 1: Set up the slide with the standard background ---
    #     "create_slide(6)",
    #     "add_picture(0, 0, 720, 540, 'dataset/A modern, geometric design featuring a central rounded frame bordered by blocks of navy, pastel pink, and light blue.jpg')",

    #     # --- Part 2: Add the main image to the left side ---
    #     # Centered vertically with generous padding around it
    #     "add_picture(60, 70, 280, 400, 'dataset/extracted_images/5GLBKNRC3EXYC6UNLASJOTJJ7XBA7MA6/2/image_2_1.jpg')", # Replace with your image path

    #     # --- Part 3: Add the title text box to the right ---
    #     "add_text_box(380, 90, 280, 80, '“Tosoiba” - Land of sparkling waters')",
    #     "set_word_wrap(True)",
    #     "set_font_color('483D8B')",  # Primary color for emphasis
    #     "set_font_size(32)",
    #     "set_font(font_name='Arial Black')",
        
    #     # --- Part 4: Add the description text box below the title ---
    #     "add_text_box(380, 240, 280, 150, 'Understanding the hydro-geology in and around Monsanto’s operations has been a key component of our business for decades now.')",
    #     "set_word_wrap(True)",
    #     "set_font_color('2F4F4F')",  # Secondary color for body text
    #     "set_font_size(18)",
    #     "set_font(font_name='Calibri')",
    # ]

    api_calls = [
    "create_slide(6)",
    "add_picture(0, 0, 720, 540, 'dataset/A modern, geometric design featuring a central rounded frame bordered by blocks of navy, pastel pink, and light blue.jpg')",
    # --- Part 2: Add and set the page title ---
    "add_text_box(80, 70, 560, 60, 'Some Guiding Principles (Water 2025)')",
    "set_text_align('CENTER')",
    "set_font_color('483D8B')",  # Same color as the main title for visual emphasis
    "set_font_size(28)",
    "set_font(font_name='Arial Black')",
    # --- Part 3: Add and set the bullet point content ---
    "add_text_box(100, 130, 520, 360, "
    "'• Recognize and respect state, tribal, and federal water rights, contracts, and interstate compacts or decrees of the United States Supreme Court that allocate the right to use water.\\n\\n' "
    "'• Maintain and modernize existing water facilities so they will continue to provide water and power.\\n\\n' "
    "'• Enhance water conservation, use efficiency, and resource monitoring to allow existing water supplies to be used more effectively.\\n\\n')",
    "set_text_align('LEFT')",
    "set_word_wrap(True)",
    "set_font_color('2F4F4F')", 
    "set_font_size(22)",
    "set_font(font_name='Calibri')"
]


    print(api_calls)
    success = generate_pptx(api_calls=api_calls, pptx_path=pptx_path, output_path=output_path)

    if success:
        print(f"PPT successfully generated: {output_path}")
    else:
        print("Failed to generate PPT.")

if __name__ == "__main__":
    main()