DIVIDER = "*" * 50
def build_slide_type_prompt(input_data: str) -> str:
    """
    Given a string of input data, return a string of the slide type prompt.
    """
    prompt = ""
    prompt += "You are tasked with identifying the best slide type to be used for the following input data. "
    prompt += DIVIDER + "\n"    
    prompt += "Input data:\n"
    prompt += input_data + "\n"
    prompt += DIVIDER + "\n"
    prompt += "Please tell me the best slide type and what and how many shapes should be included in the slide. "
    prompt += "Answer: "
    
    return prompt