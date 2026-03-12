import json
from typing import Any, Dict, Union

# JSON templates for examples
UNDERSTANDING_EXAMPLE = {"answer": "A"}

UNDERSTANDING_EXAMPLE_COT1 = {
    "reasoning": "The southern area is shown with the darkest contour color, which represents the deepest depth level. Therefore, the southern part of the lake has the greatest water depth.",
    "answer": "A"
    }
UNDERSTANDING_EXAMPLE_COT2 = {
    "reasoning": "The chart shows that 'Taste tests at grocery stores' has the highest bar height compared to other categories, indicating it generated the most consumer impressions.",
    "answer": "B"
    }

# OpenQA example - 严格格式要求
OPENQA_EXAMPLE = {"answer": "The southern part of the lake has the greatest water depth because it is shown with the darkest contour color."}

# 错误示例 - 展示不应该输出的格式
OPENQA_WRONG_EXAMPLE_1 = '{"name": "", "shape_type": "FREEFORM", "measurement_unit": "emu", "height": 1189080, "width": 1189080}'
OPENQA_WRONG_EXAMPLE_2 = '{"reasoning": "some reasoning", "answer": "some answer"}'

CoT = False

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
    cot_example1 = json.dumps(UNDERSTANDING_EXAMPLE_COT1, indent=2)
    cot_example2 = json.dumps(UNDERSTANDING_EXAMPLE_COT2, indent=2)

    # Handle options being either a string or dict
    if isinstance(options, str):
        options_dict = json.loads(options)
    else:
        options_dict = options

    # Format the options
    options_formatted = "\n".join(
        [f"{key}. {value}" for key, value in options_dict.items()]
    )
    if CoT:
        prompt = ""
        prompt += "Task: You are provided with a slide from a presentation and a multiple-choice question related to it. "
        prompt += "Analyze the slide content and select the most appropriate option that answers the question.\n\n"
        prompt += "Instructions:\n"
        prompt += "- Choose the most appropriate answer from the given options.\n"
        prompt += "- Return your final answer and reasoning in JSON format.\n"
        prompt += "- Do not include any unrelated text.\n"
        prompt += "- The final JSON must have two fields: 'reasoning' and 'answer'.\n\n"
        prompt += "Examples:\n"
        prompt += "Question1:\nBased on the depth contour map of Mono Lake, which area has the greatest water depth?\n"
        prompt += "options:\nA. The southern part of the lake.\nB. The northernmost part of the lake.\nC. The eastern edge of the lake.\nD. The western edge of the lake."
        prompt += f"Answer:\n{cot_example1}\n"
        prompt += "Question2:\nWhich activity category had the highest total number of consumer impressions for the year?\n"
        prompt += "options:\nA. Grocery store tours.\nB. Taste tests at grocery stores.\nC. Other grocery promotions.\nD. Farmer's market taste tests."
        prompt += f"Answer:\n{cot_example2}\n\n"
        prompt += f"{divider}\n"
        prompt += "Slide Content:\n"
        prompt += f"{json.dumps(slide_json, indent=2)}\n\n"
        prompt += f"{divider}\n"
        prompt += f"Question:\n{question}\n\n"
        prompt += f"Options:\n{options_formatted}\n\n"
        prompt += f"{divider}\n"
        prompt += 'Answer (Provide your response in JSON format with two fields: "reasoning" and "answer", following the same format as the examples above, and without any extra text):\n'
    else:
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


def build_openqa_prompt(
    question: str,
    slide_json: Dict[str, Any],
) -> str:
    """
    Builds an OpenQA prompt for the model based on the question and slide JSON.
    OpenQA does not provide options, allowing free-form answers.

    Args:
        question (str): The question text.
        slide_json (dict): The JSON data for the slide.

    Returns:
        str: The prompt text.
    """
    divider = "#" * 80
    example_json_str = json.dumps(OPENQA_EXAMPLE, indent=2)

    prompt = ""
    prompt += "Task: You are provided with a slide from a presentation and a question related to it. "
    prompt += "Analyze the slide content and provide a direct, specific answer to the question.\n\n"
    prompt += "INSTRUCTIONS YOU MUST FOLLOW:\n"
    prompt += "1. ALWAYS provide a direct answer to the question, even if the information is incomplete\n"
    prompt += "2. NEVER say 'slide does not contain information' or similar evasive phrases\n"
    prompt += "3. If you're unsure, make the best guess based on the available information\n"
    prompt += "4. Provide the most specific answer possible, not vague statements\n"
    prompt += "5. Return your answer in JSON format with ONLY the 'answer' field\n"
    prompt += "-" * 80 + "\n\n"
    prompt += "CRITICAL FORMAT REQUIREMENTS:\n"
    prompt += "1. JSON format: {\"answer\": \"your answer text here\"}\n"
    prompt += "2. No extra fields, no extra text\n"
    prompt += "3. Answer must be concise and specific\n\n"

    prompt += "CORRECT Example (DO THIS):\n"
    prompt += f"{example_json_str}\n\n"
    prompt += f"{divider}\n"
    prompt += "Slide Content:\n"
    prompt += f"{json.dumps(slide_json, indent=2)}\n\n"
    prompt += f"{divider}\n"
    prompt += f"Question:\n{question}\n\n"
    prompt += f"{divider}\n"
    prompt += 'Your Answer (MUST be ONLY a JSON object in the format {"answer": "..."}, nothing else):\n'

    return prompt


def build_judge_prompt(
    question: str,
    ground_truth: str,
    answer: str,
    options: Union[str, Dict[str, Any]],
) -> str:
    """
    Builds a prompt for the judge LLM to evaluate OpenQA answers.

    Args:
        question (str): The original question.
        ground_truth (str): The ground truth answer (option letter like 'A', 'B', etc.).
        answer (str): The model's answer.
        options (dict | str): Dictionary of options {letter: text} or JSON string for context.

    Returns:
        str: The prompt text for the judge.
    """
    # Get correct answer text
    correct_answer_text = ""
    options_dict = {}
    
    # Parse options if it's a string
    if isinstance(options, str):
        import json
        try:
            options_dict = json.loads(options)
        except json.JSONDecodeError:
            pass
    elif isinstance(options, dict):
        options_dict = options
    
    if options_dict and ground_truth in options_dict:
        correct_answer_text = options_dict[ground_truth]
    
    prompt = "You are an expert evaluator. Judge if the model's answer matches the correct answer.\n\n"
    
    prompt += f"Question:\n{question}\n\n"
    
    if options_dict:
        prompt += "Options:\n"
        for letter, text in options_dict.items():
            prompt += f"{letter}. {text}\n"
        prompt += "\n"
    
    prompt += f"Correct Answer: {correct_answer_text}\n\n"
    prompt += f"Model's Answer: {answer}\n\n"
    
    prompt += "Instructions:\n"
    prompt += "- Judge if the model's answer conveys the SAME MEANING as the correct answer\n"
    prompt += "- The wording can be different, but the core information must match\n"
    prompt += "- If the model says 'slide does not contain information', mark as INCORRECT\n"
    prompt += "- Return ONLY a JSON object: {\"is_correct\": true} or {\"is_correct\": false}\n\n"
    prompt += 'Judgment (Please provide a JSON object like {"is_correct": true} or {"is_correct": false}):\n'

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
    ground_truth = row["ground_truth"]
    answer = "This is Answer"
    # print(json_content)
    # prompt = build_prompt(question, options, json_content)
    # prompt = build_judge_prompt(question, ground_truth, answer, options)
    prompt = build_openqa_prompt(question, json_content)
    print(prompt)


if __name__ == "__main__":
    main()
