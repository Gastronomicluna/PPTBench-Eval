import json
from pathlib import Path
from typing import Any, Dict, List, Literal

from ..shared.pptx_api.api_doc import SLIDE_LAYOUTS
from ..shared.utils import (
    get_api_list_prompt,
    get_notes_from_json_data,
    get_texts_from_json_data,
)

# visual_design_guides.py

DESIGN_GUIDANCE = """
Visual Design Guidance (Modern Corporate/Tech Style):
- Visual Tone: Clean, flat, modern, trustworthy.
- Color Scheme:
- Primary: Deep Blue (#0D253F) or Graphite Gray (#2C3E50) for titles and core elements.
  - Secondary: Tech Blue (#3498DB) for charts, links, or secondary information.
  - Accent: Vibrant Teal (#1ABC9C) or Mango Orange (#F39C12) for call-to-actions (CTAs) or key data points.
  - Background: Pure White (#FFFFFF) or Light Gray (#F8F9FA) to ensure maximum readability.
- Typography (Sans-serif fonts like Arial, Lato, Helvetica are recommended):
  - Main Title: 32-40pt, Bold.
  - Subtitle: 20-24pt, Medium or Regular.
  - Body Text: 16-18pt, Regular.
  - Captions/Notes: 12-14pt, Light or Regular.
- Layout & Alignment:
  - Alignment: Strongly recommend left-alignment for all text to create a clear visual path.
  - Grid System: Adhere to an invisible grid to ensure all elements (icons, text boxes, images) are properly aligned.
  - Spacing: Maintain consistent spacing between modules (e.g., a fixed 20pt gap between title and body) and ensure ample white space.
- Visual Elements:
  - Icons: Use a consistent set of line icons or flat icons.
  - Images: Use high-quality, modern stock photos. A semi-transparent color overlay can be used on images to improve text legibility.

Visual Design Guidance (Creative/Artistic Style):
- Visual Tone: Bold, expressive, asymmetrical, engaging.
- Color Scheme:
  - Background: Deep Black (#1A1A1A) or a textured dark image to create an immersive feel.
  - Primary/Title: Bright Yellow (#FFD700) or Electric Purple (#9B59B6) for strong contrast on dark backgrounds.
  - Accent: Neon Pink (#E01A8C) or Lime Green (#00FF7F) for decorative touches and to grab attention.
- Typography (A mix of serif and sans-serif fonts can be effective):
  - Main Title: 44-60pt, using a display or serif font (e.g., Playfair Display) as a core visual element.
  - Body Text: 18-22pt, using a clean sans-serif font (e.g., Montserrat, Raleway).
  - Quotes/Slogans: 24-30pt, Italic or a script font to create atmosphere.
- Layout & Alignment:
  - Layout: Break conventions with asymmetrical layouts, creating visual tension with large images and text.
  - Full-Bleed Images: Use full-bleed images that extend to the edges of the slide.
  - Alignment: Use flexible alignment based on the visual focus rather than rigid left or center alignment.
- Visual Elements:
  - Typography as Design: Treat text itself as a design element, using extreme contrasts in size, weight, and color.
  - Images: Use high-saturation, artistic, or abstract photography.

Visual Design Guidance (Academic/Research Style):
- Visual Tone: Rigorous, formal, authoritative, easy to read.
- Color Scheme:
  - Primary: Academic Blue (#003366) or Classic Gray (#4A4A4A) for titles and structural elements.
  - Secondary: Neutral Gray (#808080) for subtitles and supplementary text.
  - Chart Colors: Use a clear, distinguishable color palette (avoid overly bright colors). Signal Red (#D43F3A) is recommended for highlighting key data.
  - Background: Ivory (#FFFFF0) or Pure White to reduce eye strain.
- Typography (Traditional serif fonts like Times New Roman, Garamond, Georgia are recommended):
  - Main Title: 28-34pt, Bold.
  - Body Text: 14-16pt, Regular, ensuring readability for long paragraphs.
  - Data/Tables/Formulas: 12-14pt, using a monospace font (e.g., Courier New) to ensure proper alignment.
  - Citations/References: 10-12pt, Italic.
- Layout & Alignment:
  - Alignment: Titles can be centered or left-aligned; body text should be left-aligned.
  - Clear Structure: Strictly follow the hierarchy of title, body, chart, and notes. Keep the layout clean and uncluttered.
  - Chart Guidelines: All charts must include clear titles, axis labels, units, and legends.
- Visual Elements:
  - Images: Use only diagrams, experimental photos, or data charts that are highly relevant to the research content.
  - Tables: Use clean lines with minimal decoration. The three-line table format is recommended.

Visual Design Guidance (Natural/Eco-friendly Style):
- Visual Tone: Organic, calm, friendly, full of life.
- Color Scheme:
  - Primary: Forest Green (#2E8B57) or Earth Brown (#8B4513) to reflect nature.
  - Secondary: Off-White (#F5F5DC) or Oatmeal (#D2B48C) to create a warm and soft base.
  - Accent: Sky Blue (#87CEEB) or Sunshine Yellow (#FFC300) to add energy and hope.
- Typography (Rounded sans-serif or friendly script fonts are recommended):
  - Main Title: 30-38pt, using a rounded font (e.g., Quicksand) or a font with a handwritten feel.
  - Body Text: 16-20pt, Regular, with generous line spacing.
  - Keywords: 18-22pt, can be highlighted with a color matching the primary palette.
- Layout & Alignment:
  - White Space: Make generous use of white space to create a relaxed, breathable layout.
  - Alignment: Both center and left alignment work well; aim for a natural, balanced feel.
  - Rounded Corners: Consider using slight rounded corners for text boxes and images to enhance the friendly vibe.
- Visual Elements:
  - Images: Use high-quality photos of sunny landscapes, plants, or natural materials.
  - Textures: Subtly use natural textures like recycled paper, wood grain, or linen in the background.
  - Icons: Use hand-drawn style or simple line icons.
"""


# JSON templates for examples - changed to dictionary with functions array
GENERATION_EXAMPLES = {
    "functions": [
        "choose_slide(0)",
        "choose_shape(1)",
        "set_width(1000000)",
        "insert_text('Hello, World!')",
        "create_slide(1)",
    ]
}

GENERATION_EXAMPLES_COT1 = {
    "reasoning": "Screenshot is a text-heavy slide with a clear headline and three bullet points. Choose a 'Title and Content' layout. Identify page structure: The input consists of a clear headline ('Strength Through Diversity') and a large, structured block of text containing multiple sections (DBE Program, RCAR Program) with bullet points (indicated by `\\\\n-`). Plan based on functions: (1) Create a new slide (index 1) using `create_slide(1)`. (2) Apply slide layout 256 (`choose_slide(256)`). Based on the function sequence, this ID corresponds to a 'Title Slide' layout, which typically has two main placeholders: a title and a subtitle. (3) Select the first placeholder (the main title area) using its identifier, `choose_shape(2)`. (4) Insert the headline text ('Strength Through Diversity') into this shape. (5) Select the second placeholder (the subtitle area) using its identifier, `choose_shape(3)`. (6) Insert the *entire* remaining multi-line text block, including all program details and bullets, into this subtitle placeholder.",
        "functions": [
        "create_slide(1)",
        "choose_slide(256)",
        "choose_shape(2)",
        "insert_text('Strength Through Diversity')",
        "choose_shape(3)",
        "insert_text('Disadvantaged Business Enterprise (DBE) Program\\\n- Certifies small businesses owned and controlled by minorities, women and other socially and economically disadvantaged persons\\\n- Statewide goal of 10.5% of federal transportation funds for DBE-certified firms\\\nRoad Construction Apprenticeship Readiness (RCAR) Program\\\n- Free 8-week fast track program\\\n- Targets women, minorities and economically-disadvantaged individuals\\\\n- 58% of 2008 graduates have already found placements\\\nMichigan Recovery and Reinvestment Plan • michigan.gov/recovery')"
    ]
}

GENERATION_EXAMPLES_COT2 = {
    "reasoning": "Identify page structure: The input text, inferred from the `insert_text` commands, consists of two distinct blocks: (1) 'U.S. Department of Transportation...' and (2) 'Overview of Proposed Rail Legislation...'. This structure strongly suggests a **Title Slide**. The first block serves as the main organizational title or header, and the second block provides the specific presentation title and author details. Plan: (1) Create a new slide (`create_slide(0)`). (2) Apply a 'Title Slide' layout, which is represented by the ID in `choose_slide(256)`. This layout is expected to have two primary text placeholders. (3) Select the first placeholder (the main title area) using its identifier, `choose_shape(2)`. (4) Insert the first text block ('U.S. Department of Transportation...') into this shape. (5) Select the second placeholder (the subtitle area) using its identifier, `choose_shape(3)`. (6) Insert the second, multi-line text block ('Overview of Proposed Rail Legislation...') into this subtitle shape. This sequence correctly populates the title slide with the provided information.",
        "functions": [
        "create_slide(0)",
        "choose_slide(256)",
        "choose_shape(2)",
        "insert_text('U.S. Department of Transportation\\\nFederal Railroad Administration')",
        "choose_shape(3)",
        "insert_text('Overview of Proposed Rail Legislation\\\n\\\nKevin R. Blackwell\\\nFRA Hazmat Division\\\nWashington, DC')"
    ]
}

GENERATION_EXAMPLES_COT3 = {
    "reasoning": "Goal: produce two slides from the multimedia materials — a title slide and a content slide with a large image. Steps: (1) Create a title slide and select the appropriate layout: call `create_slide(0)` to make a new slide and `choose_slide(256)` to set the Title Slide template. (2) Populate the title placeholder: select the title shape (`choose_shape(2)`) and insert the title text 'Under Dispenser Containment' so the first slide clearly states the topic. (3) Create a second slide for the image: call `create_slide(8)` to add a new slide using an image-centric layout, then `choose_slide(257)` to pick the specific template instance. (4) Add a consistent page title on the second slide: select its title placeholder (`choose_shape(2)`) and insert the same title to maintain context across slides. (5) Insert the main image into the image placeholder: switch to the image placeholder (`choose_shape(3)`) on slide 257 and call `add_picture(...)` with coordinates and size that place the image centrally and make it the dominant visual element while preserving margins. (6) Keep the reasoning concise and output the ordered function sequence afterwards.",
    "functions": ['create_slide(0)',
        'choose_slide(256)',
        'choose_shape(2)',
        "insert_text('Under Dispenser Containment')",
        'create_slide(8)',
        'choose_slide(257)',
        'choose_shape(2)',
        "insert_text('Under Dispenser Containment')",
        'choose_slide(257)',
        'choose_shape(3)',
        "add_picture(141, 48, 432, 324, 'dataset/extracted_images/W7RJCH3WN2DEJH5CHAXOMF7RX3AFE3PW/17/image_17_2.jpg')"]
}

QUERY_EXAMPLE = [
    "Generate slides from screenshots, with the given information.",
    "Generate slides from text, with the given information.",
    "Generate slides from multimedia content, with the given information."
]

Cot = True

# Default template directory path
DEFAULT_TEMPLATE_DIR = Path(__file__).parent / "json_templates"


def get_slide_layout_examples(template_dir: Path) -> str:
    """
    Get slide layout examples from the given template directory.

    Args:
        template_dir (Path): The path to the template directory.

    Returns:
        str: The slide layout examples as a formatted string.

    Raises:
        FileNotFoundError: If template_dir doesn't exist or required JSON files are missing.
        json.JSONDecodeError: If any JSON file is malformed.
    """
    if not template_dir.exists():
        raise FileNotFoundError(f"Template directory not found: {template_dir}")

    # Map layout indices to JSON files using all indices in SLIDE_LAYOUTS
    # Use consistent naming: <layout_index>.json
    layout_files = {idx: f"{idx}.json" for idx in SLIDE_LAYOUTS.keys()}

    # Verify all required files exist
    required_files = list(layout_files.values())
    missing_files = [f for f in required_files if not (template_dir / f).exists()]
    if missing_files:
        raise FileNotFoundError(
            f"Missing required template files: {', '.join(missing_files)}"
        )

    example_str = "Here is some example slide layouts:\n\n"
    try:
        # Use SLIDE_LAYOUTS to get the proper names when building examples
        for layout_idx, filename in layout_files.items():
            with open(template_dir / filename) as f:
                layout_data = json.load(f)
                layout_name = SLIDE_LAYOUTS[layout_idx]
                example_str += f"{layout_idx}. {layout_name}\n"
                example_str += json.dumps(layout_data, indent=2) + "\n\n"

        return example_str
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(
            f"Error parsing JSON template file: {e.doc}", e.doc, e.pos
        ) from e


def build_prompt(
    query: str,
    task: Literal[
        "note_to_slide", "multimedia_to_slide", "screenshot_to_slide", "text_to_slide"
    ],
    slide_json: Dict[str, Any],
    content_images: List[str] = [],
    template_dir: Path = DEFAULT_TEMPLATE_DIR,
    height: int = None,
    width: int = None,
) -> str:
    """
    Build the prompt for the given query.

    Args:
        query (str): The query to build the prompt for.
        slide_json (Dict[str, Any]): The JSON data for the slide.
        task (Literal["note_to_slide", "multimedia_to_slide", "screenshot_to_slide", "text_to_slide"]):
            The task to build the prompt for.
        content_images (List[str], optional): The list of content images. Defaults to [].
        template_dir (Path, optional): The path to the template directory. Defaults to DEFAULT_TEMPLATE_DIR.
        height (int, optional): The height of the slide. Defaults to None.
        width (int, optional): The width of the slide. Defaults to None.

    Returns:
        str: The prompt for the query.
    """
    if task == "note_to_slide":
        notes = get_notes_from_json_data(slide_json)
        return build_prompt_for_note_to_slide(
            query=query,
            notes=notes,
            content_images=content_images,
            template_dir=template_dir,
            height=height,
            width=width,
        )
    if task == "multimedia_to_slide":
        texts = get_texts_from_json_data(slide_json)
        return build_prompt_for_multimedia_to_slide(
            query=query,
            content_images=content_images,
            texts=texts,
            template_dir=template_dir,
            height=height,
            width=width,
        )
    if task == "screenshot_to_slide":
        return build_prompt_for_screenshot_to_slide(
            query=query,
            content_images=content_images,
            template_dir=template_dir,
            height=height,
            width=width,
        )
    if task == "text_to_slide":
        texts = get_texts_from_json_data(slide_json)
        return build_prompt_for_text_to_slide(
            query=query,
            texts=texts,
            template_dir=template_dir,
            height=height,
            width=width,
        )
    raise ValueError(f"Invalid task: {task}")


def build_prompt_for_text_to_slide(
    query: str,
    texts: List[str],
    template_dir: Path = DEFAULT_TEMPLATE_DIR,
    height: int = None,
    width: int = None,
) -> str:
    """
    Build the prompt for the given query for the text_to_slide task.

    Args:
        query (str): The query to build the prompt for.
        texts (List[str]): The list of texts.
        template_dir (Path): The path to the template directory.
        height (int, optional): The height of the slide. Defaults to None.
        width (int, optional): The width of the slide. Defaults to None.

    Returns:
        str: The prompt for the query.
    """
    divider = "#" * 80
    example_json_str = json.dumps(GENERATION_EXAMPLES, indent=2)
    

    if Cot:
        example_json_str_cot1 = json.dumps(GENERATION_EXAMPLES_COT1, indent=2)
        example_json_str_cot2 = json.dumps(GENERATION_EXAMPLES_COT2, indent=2)
        example_json_str_cot3 = json.dumps(GENERATION_EXAMPLES_COT3, indent=2)
        design_guide = json.dumps(DESIGN_GUIDANCE, indent=2)
        prompt = ""
        prompt += f"{query}\n"
        prompt += get_api_list_prompt()
        prompt += "Follow the instructions carefully:\n"
        prompt += "- Return a JSON object with two keys: 'reasoning' and 'functions' keys containing an array of function calls\n"
        prompt += "- 'reasoning' should describe your thought process step by step.\n"
        prompt += "- 'functions' should be an ordered array of function call strings.\n"
        prompt += "- Each function call in the array should be a string with the function name and parameters\n"
        prompt += "- The functions should be in the order they should be executed\n"
        prompt += "- Do NOT include extra explanations or markdown syntax.\n"
        prompt += "- The final output must be valid JSON.\n\n"
        prompt += "Examples:\n\n"
        prompt += f"Query1:{QUERY_EXAMPLE[0]}\n"
        prompt += f"{example_json_str_cot1}\n"
        prompt += f"Query2:{QUERY_EXAMPLE[1]}\n"
        prompt += f"{example_json_str_cot2}\n"
        prompt += f"Query3:{QUERY_EXAMPLE[2]}\n"
        prompt += f"{example_json_str_cot3}\n"
        prompt += f"{divider}\n"
        if height is not None and width is not None:
            prompt += f"Slide dimensions: Width={width}, Height={height}\n\n"
        prompt += "Texts:\n"
        for text in texts:
            prompt += f"{text}\n"
        prompt += "\n"
        try:
            prompt += get_slide_layout_examples(template_dir) + "\n"
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Warning: Could not load slide layout examples: {e}")
        prompt += f"{divider}\n"
        prompt += "The following are guidelines for slide design. Please generate the slide content based on these principles:\n"
        prompt += f"{design_guide}\n\n"
        prompt += f"Query: {query}\n"
        prompt += "Answer:\n"
    else:
        prompt = ""
        prompt += f"{query}\n"
        prompt += get_api_list_prompt()
        prompt += "Instructions:\n"
        prompt += "- Return a JSON dictionary with a single 'functions' key containing an array of function calls\n"
        prompt += "- Each function call in the array should be a string with the function name and parameters\n"
        prompt += "- The functions should be in the order they should be executed\n"
        prompt += "- Do not include any additional text or explanations\n"
        prompt += "- Abide by JSON formatting rules\n\n"
        prompt += "Examples:\n"
        prompt += f"{example_json_str}\n\n"
        prompt += f"{divider}\n"
        if height is not None and width is not None:
            prompt += f"Slide dimensions: Width={width}, Height={height}\n\n"
        prompt += "Texts:\n"
        for text in texts:
            prompt += f"{text}\n"
        prompt += "\n"
        try:
            prompt += get_slide_layout_examples(template_dir) + "\n"
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Warning: Could not load slide layout examples: {e}")
        prompt += f"Query: {query}\n"
        prompt += "Answer:\n"

    return prompt


def build_prompt_for_screenshot_to_slide(
    query: str,
    content_images: List[str] = [],
    template_dir: Path = DEFAULT_TEMPLATE_DIR,
    height: int = None,
    width: int = None,
) -> str:
    """
    Build the prompt for the given query for the screenshot_to_slide task.

    Args:
        query (str): The query to build the prompt for.
        content_images (List[str], optional): The list of content images. Defaults to [].
        template_dir (Path, optional): The path to the template directory. Defaults to None.
        height (int, optional): The height of the slide. Defaults to None.
        width (int, optional): The width of the slide. Defaults to None.

    Returns:
        str: The prompt for the query.
    """

    divider = "#" * 80
    example_json_str = json.dumps(GENERATION_EXAMPLES, indent=2)

    if Cot:
        example_json_str_cot1 = json.dumps(GENERATION_EXAMPLES_COT1, indent=2)
        example_json_str_cot2 = json.dumps(GENERATION_EXAMPLES_COT2, indent=2)
        example_json_str_cot3 = json.dumps(GENERATION_EXAMPLES_COT3, indent=2)
        design_guide = json.dumps(DESIGN_GUIDANCE, indent=2)
        prompt = ""
        prompt += f"{query}\n"
        prompt += get_api_list_prompt()
        prompt += "Follow the instructions carefully:\n"
        prompt += "- Return a JSON object with two keys: 'reasoning' and 'functions' keys containing an array of function calls\n"
        prompt += "- 'reasoning' should describe your thought process step by step.\n"
        prompt += "- 'functions' should be an ordered array of function call strings.\n"
        prompt += "- Each function call in the array should be a string with the function name and parameters\n"
        prompt += "- The functions should be in the order they should be executed\n"
        prompt += "- Do NOT include extra explanations or markdown syntax.\n"
        prompt += "- The final output must be valid JSON.\n\n"
        prompt += "Examples:\n\n"
        prompt += f"Query1:{QUERY_EXAMPLE[0]}\n"
        prompt += f"{example_json_str_cot1}\n"
        prompt += f"Query2:{QUERY_EXAMPLE[1]}\n"
        prompt += f"{example_json_str_cot2}\n"
        prompt += f"Query3:{QUERY_EXAMPLE[2]}\n"
        prompt += f"{example_json_str_cot3}\n"
        prompt += f"{divider}\n"
        if height is not None and width is not None:
            prompt += f"Slide dimensions: Width={width}, Height={height}\n\n"
        if content_images != []:
            prompt += "The first image is the screenshot you need to convert to a slide.\n"
            prompt += "The remaining images are materials you can use, and their paths are "
            prompt += f"{content_images}"
            prompt += "\n"
        if template_dir:
            try:
                prompt += get_slide_layout_examples(template_dir) + "\n"
            except (FileNotFoundError, json.JSONDecodeError) as e:
                print(f"Warning: Could not load slide layout examples: {e}")
        prompt += f"{divider}\n"
        prompt += "The following are guidelines for slide design. Please generate the slide content based on these principles:\n"
        prompt += f"{design_guide}\n\n"
        prompt += f"Query: {query}\n"
        prompt += "Answer:\n"
    else:
        prompt = ""
        prompt += f"{query}\n"
        prompt += get_api_list_prompt()
        prompt += "Instructions:\n"
        prompt += "- Return a JSON dictionary with a single 'functions' key containing an array of function calls\n"
        prompt += "- Each function call in the array should be a string with the function name and parameters\n"
        prompt += "- The functions should be in the order they should be executed\n"
        prompt += "- Do not include any additional text or explanations\n"
        prompt += "- Abide by JSON formatting rules\n\n"
        prompt += "Examples:\n"
        prompt += f"{example_json_str}\n\n"
        prompt += f"{divider}\n"
        if height is not None and width is not None:
            prompt += f"Slide dimensions: Width={width}, Height={height}\n\n"
        if content_images != []:
            prompt += "The first image is the screenshot you need to convert to a slide.\n"
            prompt += "The remaining images are materials you can use, and their paths are "
            prompt += f"{content_images}"
            prompt += "\n"
        if template_dir:
            try:
                prompt += get_slide_layout_examples(template_dir) + "\n"
            except (FileNotFoundError, json.JSONDecodeError) as e:
                print(f"Warning: Could not load slide layout examples: {e}")
        prompt += f"Query: {query}\n"
        prompt += "Answer:\n"

    return prompt


def build_prompt_for_multimedia_to_slide(
    query: str,
    content_images: List[str] = [],
    texts: List[str] = [],
    template_dir: Path = DEFAULT_TEMPLATE_DIR,
    height: int = None,
    width: int = None,
) -> str:
    """
    Build the prompt for the given query for the multimedia_to_slide task.

    Args:
        query (str): The query to build the prompt for.
        content_images (List[str], optional): The list of content images. Defaults to [].
        texts (List[str], optional): The list of texts. Defaults to [].
        template_dir (Path, optional): The path to the template directory. Defaults to None.
        height (int, optional): The height of the slide. Defaults to None.
        width (int, optional): The width of the slide. Defaults to None.

    Returns:
        str: The prompt for the query.
    """

    divider = "#" * 80
    example_json_str = json.dumps(GENERATION_EXAMPLES, indent=2)

    if Cot:
        example_json_str_cot1 = json.dumps(GENERATION_EXAMPLES_COT1, indent=2)
        example_json_str_cot2 = json.dumps(GENERATION_EXAMPLES_COT2, indent=2)
        example_json_str_cot3 = json.dumps(GENERATION_EXAMPLES_COT3, indent=2)
        design_guide = json.dumps(DESIGN_GUIDANCE, indent=2)
        prompt = ""
        prompt += f"{query}\n"
        prompt += get_api_list_prompt()
        prompt += "Follow the instructions carefully:\n"
        prompt += "- Return a JSON object with two keys: 'reasoning' and 'functions' keys containing an array of function calls\n"
        prompt += "- 'reasoning' should describe your thought process step by step.\n"
        prompt += "- 'functions' should be an ordered array of function call strings.\n"
        prompt += "- Each function call in the array should be a string with the function name and parameters\n"
        prompt += "- The functions should be in the order they should be executed\n"
        prompt += "- Do NOT include extra explanations or markdown syntax.\n"
        prompt += "- The final output must be valid JSON.\n\n"
        prompt += "Examples:\n\n"
        prompt += f"Query1:{QUERY_EXAMPLE[0]}\n"
        prompt += f"{example_json_str_cot1}\n"
        prompt += f"Query2:{QUERY_EXAMPLE[1]}\n"
        prompt += f"{example_json_str_cot2}\n"
        prompt += f"Query3:{QUERY_EXAMPLE[2]}\n"
        prompt += f"{example_json_str_cot3}\n"
        prompt += f"{divider}\n"
        if height is not None and width is not None:
            prompt += f"Slide dimensions: Width={width}, Height={height}\n\n"
        if texts != []:
            prompt += "Texts:\n"
            for text in texts:
                prompt += f"{text}\n"
            prompt += "\n"
        if content_images != []:
            prompt += "The images given are materials you can use, and their paths are "
            prompt += f"{content_images}"
            prompt += "\n"
        if template_dir:
            try:
                prompt += get_slide_layout_examples(template_dir) + "\n"
            except (FileNotFoundError, json.JSONDecodeError) as e:
                print(f"Warning: Could not load slide layout examples: {e}")
        prompt += f"{divider}\n"
        prompt += "The following are guidelines for slide design. Please generate the slide content based on these principles:\n"
        prompt += f"{design_guide}\n\n"
        prompt += f"Query: {query}\n"
        prompt += "Answer:\n"
    else:
        prompt = ""
        prompt += f"{query}\n"
        prompt += get_api_list_prompt()
        prompt += "Instructions:\n"
        prompt += "- Return a JSON dictionary with a single 'functions' key containing an array of function calls\n"
        prompt += "- Each function call in the array should be a string with the function name and parameters\n"
        prompt += "- The functions should be in the order they should be executed\n"
        prompt += "- Do not include any additional text or explanations\n"
        prompt += "- Abide by JSON formatting rules\n\n"
        prompt += "Examples:\n"
        prompt += f"{example_json_str}\n\n"
        prompt += f"{divider}\n"
        if height is not None and width is not None:
            prompt += f"Slide dimensions: Width={width}, Height={height}\n\n"
        if texts != []:
            prompt += "Texts:\n"
            for text in texts:
                prompt += f"{text}\n"
            prompt += "\n"
        if content_images != []:
            prompt += "The images given are materials you can use, and their paths are "
            prompt += f"{content_images}"
            prompt += "\n"
        if template_dir:
            try:
                prompt += get_slide_layout_examples(template_dir) + "\n"
            except (FileNotFoundError, json.JSONDecodeError) as e:
                print(f"Warning: Could not load slide layout examples: {e}")
        prompt += f"Query: {query}\n"
        prompt += "Answer:\n"

    return prompt


def build_prompt_for_note_to_slide(
    query: str,
    notes: str,
    content_images: List[str] = [],
    template_dir: Path = DEFAULT_TEMPLATE_DIR,
    height: int = None,
    width: int = None,
) -> str:
    """
    Build the prompt for the given query for the note_to_slide task.

    Args:
        query (str): The query to build the prompt for.
        notes (str): The notes to include in the prompt.
        content_images (List[str], optional): The list of content images. Defaults to [].
        template_dir (Path, optional): The path to the template directory. Defaults to None.
        height (int, optional): The height of the slide. Defaults to None.
        width (int, optional): The width of the slide. Defaults to None.

    Returns:
        str: The prompt for the query.
    """

    divider = "#" * 80
    example_json_str = json.dumps(GENERATION_EXAMPLES, indent=2)

    if Cot:
        example_json_str_cot1 = json.dumps(GENERATION_EXAMPLES_COT1, indent=2)
        example_json_str_cot2 = json.dumps(GENERATION_EXAMPLES_COT2, indent=2)
        example_json_str_cot3 = json.dumps(GENERATION_EXAMPLES_COT3, indent=2)
        design_guide = json.dumps(DESIGN_GUIDANCE, indent=2)
        prompt = ""
        prompt += f"{query}\n"
        prompt += get_api_list_prompt()
        prompt += "Follow the instructions carefully:\n"
        prompt += "- Return a JSON object with two keys: 'reasoning' and 'functions' keys containing an array of function calls\n"
        prompt += "- 'reasoning' should describe your thought process step by step.\n"
        prompt += "- 'functions' should be an ordered array of function call strings.\n"
        prompt += "- Each function call in the array should be a string with the function name and parameters\n"
        prompt += "- The functions should be in the order they should be executed\n"
        prompt += "- Do NOT include extra explanations or markdown syntax.\n"
        prompt += "- The final output must be valid JSON.\n\n"
        prompt += "Examples:\n\n"
        prompt += f"Query1:{QUERY_EXAMPLE[0]}\n"
        prompt += f"{example_json_str_cot1}\n"
        prompt += f"Query2:{QUERY_EXAMPLE[1]}\n"
        prompt += f"{example_json_str_cot2}\n"
        prompt += f"Query3:{QUERY_EXAMPLE[2]}\n"
        prompt += f"{example_json_str_cot3}\n"
        prompt += f"{divider}\n"
        if height is not None and width is not None:
            prompt += f"Slide dimensions: Width={width}, Height={height}\n\n"
        prompt += "Notes:\n"
        prompt += f"{notes}\n\n"
        prompt += f"{divider}\n"
        if content_images != []:
            prompt += "The images given are materials you can use, and their paths are "
            prompt += f"{content_images}"
            prompt += "\n"
        if template_dir:
            try:
                prompt += get_slide_layout_examples(template_dir) + "\n"
            except (FileNotFoundError, json.JSONDecodeError) as e:
                print(f"Warning: Could not load slide layout examples: {e}")
        prompt += f"{divider}\n"
        prompt += "The following are guidelines for slide design. Please generate the slide content based on these principles:\n"
        prompt += f"{design_guide}\n\n"
        prompt += f"Query: {query}\n"
        prompt += "Answer:\n"
    else:
        prompt = ""
        prompt += f"{query}\n"
        prompt += get_api_list_prompt()
        prompt += "Instructions:\n"
        prompt += "- Return a JSON dictionary with a single 'functions' key containing an array of function calls\n"
        prompt += "- Each function call in the array should be a string with the function name and parameters\n"
        prompt += "- The functions should be in the order they should be executed\n"
        prompt += "- Do not include any additional text or explanations\n"
        prompt += "- Abide by JSON formatting rules\n\n"
        prompt += "Examples:\n"
        prompt += f"{example_json_str}\n\n"
        prompt += f"{divider}\n"
        if height is not None and width is not None:
            prompt += f"Slide dimensions: Width={width}, Height={height}\n\n"
        prompt += "Notes:\n"
        prompt += f"{notes}\n\n"
        prompt += f"{divider}\n"
        if content_images != []:
            prompt += "The images given are materials you can use, and their paths are "
            prompt += f"{content_images}"
            prompt += "\n"
        if template_dir:
            try:
                prompt += get_slide_layout_examples(template_dir) + "\n"
            except (FileNotFoundError, json.JSONDecodeError) as e:
                print(f"Warning: Could not load slide layout examples: {e}")
        prompt += f"Query: {query}\n"
        prompt += "Answer:\n"

    return prompt


def main() -> None:
    """Test the prompt generation functionality with sample inputs."""
    test_cases = [
        {
            "task": "text_to_slide",
            "query": "Create a slide about Python programming",
            "texts": [
                "Python is a popular programming language.",
                "It's known for its simplicity and readability.",
            ],
            "slide_json": {"slide": {"shapes":[{"type":"text","text": ["Sample text"]}]}},
            "content_images": [],
        },
        # {
        #     "task": "screenshot_to_slide",
        #     "query": "Convert this screenshot to a slide",
        #     "slide_json": {},
        #     "content_images": ["dataset/extracted_images/W7RJCH3WN2DEJH5CHAXOMF7RX3AFE3PW/17/image_17_2.jpg"],
        # },
        # {
        #     "task": "note_to_slide",
        #     "query": "Create a slide from these notes",
        #     "slide_json": {
        #         "notes": "Important meeting points:\n1. Project timeline\n2. Budget review"
        #     },
        #     "content_images": [],
        # },
        # {
        #     "task": "multimedia_to_slide",
        #     "query": "Create a slide with these images and text",
        #     "slide_json": {"texts": ["Caption for image"]},
        #     "content_images": ["path/to/image1.png", "path/to/image2.png"],
        # },
    ]

    # for i, test_case in enumerate(test_cases, 1):
    #     print(f"\n{'='*40} Test Case {i} {'='*40}")
    #     print(f"Task: {test_case['task']}")
    #     try:
    #         prompt = build_prompt(
    #             query=test_case["query"],
    #             task=test_case["task"],
    #             slide_json=test_case["slide_json"],
    #             content_images=test_case["content_images"],
    #         )
    #         print("\nGenerated Prompt:")
    #         print(f"{'-'*80}\n{prompt}\n{'-'*80}")
    #     except Exception as e:
    #         print(f"Error generating prompt: {str(e)}")

    from src.shared.load_save_dataset import load_save_huggingface_dataset_df

    dataset_name = "tyrionhuu/PPTBench-Generation"
    dataset_path = "data/PPTBench-Generation"

    df = load_save_huggingface_dataset_df(
        dataset_name=dataset_name,
        dataset_path=dataset_path,
        force_download=False,
    )
    # Print complete header
    # print(df.columns)
    seed = 40
    row = df.sample(random_state=seed).iloc[0]
    description = row["description"]
    json_data = json.loads(row["json_content"])
    content_images = row["content_images"]
    task = row["task"]

    # print(json_content)
    prompt = build_prompt(
        query=description,
        task=task,
        slide_json=json_data,
        content_images=content_images,
    )
    print(prompt)
    print(task)


if __name__ == "__main__":
    main()
