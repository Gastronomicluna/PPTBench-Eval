import json
from typing import Any, Dict, Literal, Optional

from ..shared.utils import get_api_list_prompt
from .utils import get_font_from_shape

# JSON templates for examples - changed to dictionary with functions array
MODIFICATION_EXAMPLE = {
    "functions": [
        "choose_slide(0)",
        "choose_shape(1)",
        "set_width(1000000)",
        "insert_text('Hello, World!')",
    ]
}

MODIFICATION_EXAMPLE_COT_RESIZESHAPE = {
    "reasoning": "Original width = 5,744,215 EMUs. Increase by 30%: 0.3 * 5,744,215 = 1,723,264.5 EMUs, so new width = 5,744,215 + 1,723,264.5 = 7,467,479.5 EMUs. Round to nearest integer → 7,467,480 EMUs. To keep the middle-center fixed, shift the left position left by half of the width increase: half increase = 1,723,265 / 2 ≈ 861,632.5 EMUs → round to 861,633. Original left = 1,623,392 EMUs, new left = 1,623,392 - 861,633 = 761,759 EMUs → round to 761,760 to use an integer. Therefore select the slide and shape, set the new width, and update left to keep center fixed.",
    "functions": [
        "choose_slide(263)",
        "choose_shape(44)",
        "set_width(7467480)",
        "set_left(761760)"
  ]
}

MODIFICATION_EXAMPLE_COT_CHANGEFONT = {
    "reasoning": "Locate the slide and the title shape: the slide object has slide_id 311 and a shape with placeholder_type 'TITLE' and shape_id 722. The title's current font is 'Tahoma' at 24.0pt, so to change the title font to 'Arial Black' we should (1) select the slide, (2) select the title shape, and (3) set the font to 'Arial Black'. No size or position changes are required.",
    "functions": [
        "choose_slide(311)",
        "choose_shape(722)",
        "set_font('Arial Black')"
    ]
}

QUERY_EXAMPLE = [
    "Increase the width of the shape by 30% of its original width. The middle-center of the shape should be at a fixed position.",
    "Change the font of the title text to Arial Black."
]

CoT = False
def build_prompt(
    query: str,
    slide_json: Dict[str, Any],
    subcategory: Literal["element_modification", "refinement", "text_modification"],
    task: Optional[str] = None,
    shape_to_modify: Optional[Any] = None,
) -> str:
    """
    Builds a prompt for the model based on the query and slide JSON.

    Args:
        query (str): The query text.
        slide_json (dict): The JSON data for the slide.
        subcategory (str): The subcategory of the modification task.
        shape_to_modify (dict): The shape to modify, if applicable.

    Returns:
        str: The prompt text.
    """
    if not isinstance(slide_json, dict):
        raise ValueError("slide_json must be a dictionary.")

    if subcategory == "element_modification":
        return build_prompt_element_modification(
            query=query,
            task=task,
            slide_json=slide_json,
            shape_to_modify=shape_to_modify,
        )
    elif subcategory == "refinement":
        return build_prompt_refinement(query, slide_json)
    elif subcategory == "text_modification":
        return build_prompt_text_modification(query, slide_json)
    else:
        raise ValueError(f"Invalid subcategory: {subcategory}")


def build_prompt_element_modification(
    query: str,
    task: Literal["add_shape", "resize_shape", "reposition_shape"],
    slide_json: Dict[str, Any],
    shape_to_modify: Dict[str, Any],
) -> str:
    """
    Builds a prompt for the model based on the query and slide JSON, instructing the model to modify an element in the slide.

    Args:
        query (str): The query text.
        slide_json (dict): The JSON data for the slide.
        shape_to_modify (dict): The shape to modify.

    Returns:
        str: The prompt text.
    """
    if not isinstance(shape_to_modify, dict) and shape_to_modify is not None:
        raise ValueError("shape_to_modify must be a dictionary.")

    if task == "add_shape":
        return build_prompt_add_shape(query, slide_json, shape_to_modify)
    elif task == "resize_shape" or task == "reposition_shape":
        divider = "#" * 80
        example_json_str = json.dumps(MODIFICATION_EXAMPLE, indent=2)


        if CoT:
            example_json_str_cot1 = json.dumps(MODIFICATION_EXAMPLE_COT_RESIZESHAPE, indent=2)
            example_json_str_cot2 = json.dumps(MODIFICATION_EXAMPLE_COT_CHANGEFONT, indent=2)
            prompt = ""
            prompt += "Task: You are given a slide from a presentation in the form of an image and JSON data.\n"
            prompt += f"{query}\n"
            prompt += get_api_list_prompt()
            prompt += "Required format:\n"
            prompt += "- Return a JSON dictionary containing two keys: 'reasoning' and 'functions'.\n"
            prompt += "- 'reasoning': provide a clear, step-by-step explanation of how you derived the parameters or decided on the sequence of operations.\n"
            prompt += "- 'functions' should be an array of function call strings, each function call in the array should be a string with the function name and parameters\n"
            prompt += "- The functions should be in the order they should be executed\n"
            prompt += "- Do not include any additional text or explanations outside of JSON.\n"
            prompt += "- The final output must strictly follow the format shown in the Examples section.\n"
            prompt += "- No markdown formatting\n\n"
            prompt += "Examples:\n\n"
            prompt += f"Query1:{QUERY_EXAMPLE[0]}\n"
            prompt += f"{example_json_str_cot1}\n"
            prompt += f"Query2:{QUERY_EXAMPLE[1]}\n"
            prompt += f"{example_json_str_cot2}\n"
            prompt += f"{divider}\n"
            prompt += "Slide JSON:\n"
            prompt += f"{json.dumps(slide_json, indent=2)}\n\n"
            prompt += f"{divider}\n"
            prompt += f"Query: {query}\n"
            prompt += f"Shape to Modify: {json.dumps(shape_to_modify, indent=2)}\n"
            prompt += "Answer:\n"
        else:
            prompt = ""
            prompt += "Task: You are given a slide from a presentation in the form of an image and JSON data.\n"
            prompt += f"{query}\n"
            prompt += get_api_list_prompt()
            prompt += "Required format:\n"
            prompt += "- Return a JSON dictionary with a single 'functions' key containing an array of function calls\n"
            prompt += "- Each function call in the array should be a string with the function name and parameters\n"
            prompt += "- The functions should be in the order they should be executed\n"
            prompt += "- Do not include any additional text or explanations\n"
            prompt += "- No markdown formatting\n\n"
            prompt += "Examples:\n"
            prompt += f"{example_json_str}\n\n"
            prompt += f"{divider}\n"
            prompt += "Slide JSON:\n"
            prompt += f"{json.dumps(slide_json, indent=2)}\n\n"
            prompt += f"{divider}\n"
            prompt += f"Query: {query}\n"
            prompt += f"Shape to Modify: {json.dumps(shape_to_modify, indent=2)}\n"
            prompt += "Answer:\n"

        return prompt


def build_prompt_add_shape(
    query: str,
    slide_json: Dict[str, Any],
    shape_to_add: Dict[str, Any],
) -> str:
    """
    Builds a prompt for the model based on the query and slide JSON, instructing the model to add a shape to the slide.

    Args:
        query (str): The query text.
        slide_json (dict): The JSON data for the slide.
        shape_to_add (dict): The shape to add.

    Returns:
        str: The prompt text.
    """
    divider = "#" * 80
    example_json_str = json.dumps(MODIFICATION_EXAMPLE, indent=2)
    if "text" in shape_to_add:
        text_content = build_add_shape_text_content(shape_to_add)
    elif "image_path" in shape_to_add:
        text_content = build_add_shape_image_content(shape_to_add)
    else:
        raise ValueError("Shape to add must contain either 'text' or 'image_path'.")

    if CoT:
        example_json_str_cot1 = json.dumps(MODIFICATION_EXAMPLE_COT_RESIZESHAPE, indent=2)
        example_json_str_cot2 = json.dumps(MODIFICATION_EXAMPLE_COT_CHANGEFONT, indent=2)
        prompt = ""
        prompt += "Task: You are given a slide from a presentation in the form of an image and JSON data.\n"
        prompt += f"{query}\n"
        prompt += get_api_list_prompt()
        prompt += "Required format:\n"
        prompt += "- Return a JSON dictionary containing two keys: 'reasoning' and 'functions'.\n"
        prompt += "- 'reasoning': provide a clear, step-by-step explanation of how you derived the parameters or decided on the sequence of operations.\n"
        prompt += "- 'functions' should be an array of function call strings, each function call in the array should be a string with the function name and parameters\n"
        prompt += "- The functions should be in the order they should be executed\n"
        prompt += "- Do not include any additional text or explanations outside of JSON.\n"
        prompt += "- The final output must strictly follow the format shown in the Examples section.\n"
        prompt += "- No markdown formatting\n\n"
        prompt += "Examples:\n\n"
        prompt += f"Query1:{QUERY_EXAMPLE[0]}\n"
        prompt += f"{example_json_str_cot1}\n"
        prompt += f"Query2:{QUERY_EXAMPLE[1]}\n"
        prompt += f"{example_json_str_cot2}\n"
        prompt += f"{divider}\n"
        prompt += "Slide JSON:\n"
        prompt += f"{json.dumps(slide_json, indent=2)}\n\n"
        prompt += f"{divider}\n"
        prompt += f"Query: {query}\n"
        prompt += f"{text_content}\n"
        prompt += "Answer:\n"
    else:
        prompt = ""
        prompt += "Task: You are given a slide from a presentation in the form of an image and JSON data.\n"
        prompt += f"{query}\n"
        prompt += get_api_list_prompt()
        prompt += "Required format:\n"
        prompt += "- Return a JSON dictionary with a single 'functions' key containing an array of function calls\n"
        prompt += "- Each function call in the array should be a string with the function name and parameters\n"
        prompt += "- The functions should be in the order they should be executed\n"
        prompt += "- Do not include any additional text or explanations\n"
        prompt += "- No markdown formatting\n"
        prompt += "- The added shape should not overlap with existing shapes\n"
        prompt += "- The added shape should not be out of bounds\n\n"
        prompt += "Examples:\n"
        prompt += f"{example_json_str}\n\n"
        prompt += f"{divider}\n"
        prompt += "Slide JSON:\n"
        prompt += f"{json.dumps(slide_json, indent=2)}\n\n"
        prompt += f"{divider}\n"
        prompt += f"Query: {query}\n"
        prompt += f"{text_content}\n"
        prompt += "Answer:\n"
    return prompt


def build_add_shape_text_content(
    shape_to_add: Dict[str, Any],
) -> str:
    """
    Builds the text content for a shape to add to the slide.

    Args:
        shape_to_add (dict): The shape to add.

    Returns:
        str: The text content for the shape.
    """
    text = shape_to_add["text"]
    result = f"Add a shape to the slide with the following text: '{text}'.\n"

    font_set = get_font_from_shape(shape_to_add)

    if len(font_set) > 1 or len(font_set) == 0:
        return result
    else:
        font_name = font_set.pop()
        result += f" The font used should be '{font_name}'."
        return result


def build_add_shape_image_content(
    shape_to_add: Dict[str, Any],
) -> str:
    """
    Builds the image content for a shape to add to the slide.

    Args:
        shape_to_add (dict): The shape to add.

    Returns:
        str: The image content for the shape.
    """
    # if not isinstance(shape_to_add, dict):
    #     raise ValueError("shape_to_add must be a dictionary.")
    image_path = shape_to_add["image_path"]
    result = f"Add a shape to the slide with the following image: '{image_path}'.\n"
    return result


def build_prompt_refinement(
    query: str,
    slide_json: Dict[str, Any],
) -> str:
    """
    Builds a prompt for the model based on the query and slide JSON, instructing the model to return the answer in JSON format.

    Args:
        query (str): The query text.
        slide_json (dict): The JSON data for the slide.

    Returns:
        str: The prompt text.
    """
    divider = "#" * 80
    example_json_str = json.dumps(MODIFICATION_EXAMPLE, indent=2)


    if CoT:
        example_json_str_cot1 = json.dumps(MODIFICATION_EXAMPLE_COT_RESIZESHAPE, indent=2)
        example_json_str_cot2 = json.dumps(MODIFICATION_EXAMPLE_COT_CHANGEFONT, indent=2)
        prompt = ""
        prompt += "Task: You are given a slide from a presentation in the form of an image and JSON data.\n"
        prompt += f"{query}\n"
        prompt += get_api_list_prompt()
        prompt += "Required format:\n"
        prompt += "- Return a JSON dictionary containing two keys: 'reasoning' and 'functions'.\n"
        prompt += "- 'reasoning': provide a clear, step-by-step explanation of how you derived the parameters or decided on the sequence of operations.\n"
        prompt += "- 'functions' should be an array of function call strings, each function call in the array should be a string with the function name and parameters\n"
        prompt += "- The functions should be in the order they should be executed\n"
        prompt += "- Do not include any additional text or explanations outside of JSON.\n"
        prompt += "- The final output must strictly follow the format shown in the Examples section.\n"
        prompt += "- No markdown formatting\n\n"
        prompt += "Examples:\n\n"
        prompt += f"Query1:{QUERY_EXAMPLE[0]}\n"
        prompt += f"{example_json_str_cot1}\n"
        prompt += f"Query2:{QUERY_EXAMPLE[1]}\n"
        prompt += f"{example_json_str_cot2}\n"
        prompt += f"{divider}\n"
        prompt += "Slide JSON:\n"
        prompt += f"{json.dumps(slide_json, indent=2)}\n\n"
        prompt += f"{divider}\n"
        prompt += f"Query: {query}\n"
        prompt += "Answer:\n"
    else:
        prompt = ""
        prompt += "Task: You are given a slide from a presentation in the form of an image and JSON data.\n"
        prompt += f"{query}\n"
        prompt += get_api_list_prompt()
        prompt += "Required format:\n"
        prompt += "- Return a JSON dictionary with a single 'functions' key containing an array of function calls\n"
        prompt += "- Each function call in the array should be a string with the function name and parameters\n"
        prompt += "- The functions should be in the order they should be executed\n"
        prompt += "- Do not include any additional text or explanations\n"
        prompt += "- No markdown formatting\n\n"
        prompt += "Examples:\n"
        prompt += f"{example_json_str}\n\n"
        prompt += f"{divider}\n"
        prompt += "Slide JSON:\n"
        prompt += f"{json.dumps(slide_json, indent=2)}\n\n"
        prompt += f"{divider}\n"
        prompt += f"Query: {query}\n"
        prompt += "Answer:\n"
    return prompt


def build_prompt_text_modification(
    query: str,
    slide_json: Dict[str, Any],
) -> str:
    """
    Builds a prompt for the model based on the query and slide JSON, instructing the model to modify the text in the slide.

    Args:
        query (str): The query text.
        slide_json (dict): The JSON data for the slide.
        shape_to_modify (dict): The shape to modify.

    Returns:
        str: The prompt text.
    """
    divider = "#" * 80
    example_json_str = json.dumps(MODIFICATION_EXAMPLE, indent=2)

    if CoT:
        example_json_str_cot1 = json.dumps(MODIFICATION_EXAMPLE_COT_RESIZESHAPE, indent=2)
        example_json_str_cot2 = json.dumps(MODIFICATION_EXAMPLE_COT_CHANGEFONT, indent=2)
        prompt = ""
        prompt += "Task: You are given a slide from a presentation in the form of an image and JSON data.\n"
        prompt += f"{query}\n"
        prompt += get_api_list_prompt()
        prompt += "Required format:\n"
        prompt += "- Return a JSON dictionary containing two keys: 'reasoning' and 'functions'.\n"
        prompt += "- 'reasoning': provide a clear, step-by-step explanation of how you derived the parameters or decided on the sequence of operations.\n"
        prompt += "- 'functions' should be an array of function call strings, each function call in the array should be a string with the function name and parameters\n"
        prompt += "- The functions should be in the order they should be executed\n"
        prompt += "- Do not include any additional text or explanations outside of JSON.\n"
        prompt += "- The final output must strictly follow the format shown in the Examples section.\n"
        prompt += "- No markdown formatting\n\n"
        prompt += "Examples:\n\n"
        prompt += f"Query1:{QUERY_EXAMPLE[0]}\n"
        prompt += f"{example_json_str_cot1}\n"
        prompt += f"Query2:{QUERY_EXAMPLE[1]}\n"
        prompt += f"{example_json_str_cot2}\n"
        prompt += f"{divider}\n"
        prompt += "Slide JSON:\n"
        prompt += f"{json.dumps(slide_json, indent=2)}\n\n"
        prompt += f"{divider}\n"
        prompt += f"Query: {query}\n"
        prompt += "Answer:\n"

    else:
        prompt = ""
        prompt += "Task: You are given a slide from a presentation in the form of an image and JSON data.\n"
        prompt += f"{query}\n"
        prompt += get_api_list_prompt()
        prompt += "Required format:\n"
        prompt += "- Return a JSON dictionary with a single 'functions' key containing an array of function calls\n"
        prompt += "- Each function call in the array should be a string with the function name and parameters\n"
        prompt += "- The functions should be in the order they should be executed\n"
        prompt += "- Do not include any additional text or explanations\n"
        prompt += "- No markdown formatting\n\n"
        prompt += "Examples:\n"
        prompt += f"{example_json_str}\n\n"
        prompt += f"{divider}\n"
        prompt += "Slide JSON:\n"
        prompt += f"{json.dumps(slide_json, indent=2)}\n\n"
        prompt += f"{divider}\n"
        prompt += f"Query: {query}\n"
        prompt += "Answer:\n"
    return prompt


def main() -> None:
    # print(build_prompt_refinement("Refine the slide.", {"slide": "data"}))
    from src.shared.load_save_dataset import load_save_huggingface_dataset_df

    dataset_name = "tyrionhuu/PPTBench-Modification"
    dataset_path = "data/PPTBench-Modification"

    df = load_save_huggingface_dataset_df(
        dataset_name=dataset_name,
        dataset_path=dataset_path,
        force_download=False,
    )
    # Print complete header
    # print(df.columns)
    seed = 42
    row = df.sample(random_state=seed).iloc[0]
    description = row["description"]
    json_data = json.loads(row["json_data"])
    subcategory = row["subcategory"]
    shape_to_modify = json.loads(row["shape_to_modify"])
    task = row["task"]

    # print(json_content)
    prompt = build_prompt(                
        query=description,
        slide_json=json_data,
        task=task,
        subcategory=subcategory,
        shape_to_modify=shape_to_modify,
        )
    print(prompt)
    print(task)


if __name__ == "__main__":
    main()
