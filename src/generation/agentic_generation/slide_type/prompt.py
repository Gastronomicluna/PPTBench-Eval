DIVIDER = "*" * 50

def build_slide_type_prompt(input_data: str) -> str:
    """
    Given a string of input data, return a well-structured prompt to identify the best slide type.
    
    Args:
        input_data (str): The input data that will inform the slide type recommendation.
        
    Returns:
        str: A structured prompt requesting the best slide type and the necessary shapes.
    """
    prompt = ""
    prompt += "You are tasked with selecting the most appropriate slide type for the following content. "
    prompt += "Your recommendation should be based on the structure and key message of the input data.\n"
    prompt += DIVIDER + "\n"
    prompt += "Input Data:\n"
    prompt += input_data + "\n"
    prompt += DIVIDER + "\n"
    prompt += "Please provide the best slide type for this content. In your response, be sure to include the following:\n"
    prompt += "1. The recommended slide type.\n"
    prompt += "2. The types and number of shapes or visual elements required for the slide.\n"
    prompt += "3. A brief explanation of why this slide type is the most suitable for the given input data.\n"
    prompt += "Your answer should be clear and concise. Answer: "

    return prompt

