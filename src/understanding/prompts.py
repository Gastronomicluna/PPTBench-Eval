import json
from typing import Any, Dict, Union

# JSON templates for examples
UNDERSTANDING_EXAMPLE = {
    "answer": "A"
}

def build_prompt(
    question: str,
    options: Union[str, Dict[str, Any]],
    slide_json: Dict[str, Any],
) -> str:
    """
    Builds a prompt for the model based on the question and slide JSON.

    Args:
        question (str): The question text.
        options (Union[str, Dict[str, Any]]): Options as string or dictionary.
        slide_json (dict): The JSON data for the slide.

    Returns:
        str: The prompt text.
    """
    divider = "#" * 80
    example_json_str = json.dumps(UNDERSTANDING_EXAMPLE, indent=2)

    # Handle options being either a string or dict
    if isinstance(options, str):
        options_dict = json.loads(options)
    else:
        options_dict = options

    # Format the options
    options_formatted = "\n".join(
        [f"{key}. {value}" for key, value in options_dict.items()]
    )

    prompt = ""
    prompt += "Task: You are provided with a slide from a presentation and a multiple-choice question related to it. "
    prompt += "Analyze the slide content and select the most appropriate option that answers the question.\n\n"
    prompt += "Instructions:\n"
    prompt += "- Choose the most appropriate answer from the given options.\n"
    prompt += "- Return only the letter of your choice in JSON format.\n"
    prompt += "- Do not include any explanations or additional text.\n\n"
    prompt += "Example:\n"
    prompt += f"{example_json_str}\n\n"
    prompt += f"{divider}\n"
    prompt += "Slide Content:\n"
    prompt += f"{json.dumps(slide_json, indent=2)}\n\n"
    prompt += f"{divider}\n"
    prompt += f"Question:\n{question}\n\n"
    prompt += f"Options:\n{options_formatted}\n\n"
    prompt += f"{divider}\n"
    prompt += 'Answer (Please provide a JSON object with the key "answer" and the value being the letter of the correct option, without any additional text):\n'

    return prompt


def main() -> None:
    from src.shared.load_save_dataset import load_save_huggingface_dataset_df

    dataset_name = "tyrionhuu/PPTBench-Understanding"
    dataset_path = "data/PPTBench-Understanding"

    df = load_save_huggingface_dataset_df(
        dataset_name=dataset_name,
        dataset_path=dataset_path,
        force_download=False,
    )
    # Print complete header
    # print(df.columns)
    seed = 42
    row = df.sample(random_state=seed).iloc[0]
    question = row["question"]
    options = row["options"]
    json_content = row["json_content"]
    # print(json_content)
    prompt = build_prompt(question, options, json_content)
    print(prompt)


if __name__ == "__main__":
    main()
