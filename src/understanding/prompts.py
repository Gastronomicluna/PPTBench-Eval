from typing import Any, Dict


def build_prompt(
    question: str,
    options: Dict[str, Any],
    slide_json: Dict[str, Any],
) -> str:
    """
    Builds a prompt for the model based on the question and slide JSON.

    Args:
        question (str): The question text.
        slide_json (dict): The JSON data for the slide.

    Returns:
        str: The prompt text.
    """
    divider = "#" * 80
    prompt = f"""
{divider}
Task: You are given a slide from a presentation in the form of an image and JSON data.
{question}. Only return the requested information in the following JSON format:
{{
    "left": <integer>,
    "top": <integer>,
    "width": <integer>,
    "height": <integer>
}}
Ensure that all values are integers and the JSON is properly formatted.
{divider}
Slide: {slide_json}
{divider}
Answer:
"""
    return prompt


# def main() -> None:
#     from src.shared.load_save_dataset import load_save_huggingface_dataset_df

#     dataset_name = "tyrionhuu/PPTBench-Detection"
#     dataset_path = "data/PPTBench-Detection"

#     df = load_save_huggingface_dataset_df(
#         dataset_name=dataset_name,
#         dataset_path=dataset_path,
#         force_download=False,
#     )
#     # Print complete header
#     # print(df.columns)
#     seed = 42
#     row = df.sample(random_state=seed).iloc[0]
#     description = row["description"]
#     json_data = row["json_data"]
#     # print(json_data)
#     prompt = build_prompt(description, json_data)
#     print(prompt)


# if __name__ == "__main__":
#     main()
