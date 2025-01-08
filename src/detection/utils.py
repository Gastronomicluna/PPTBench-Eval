from .judge import compare_coordinate, exact_match, fuzzy_match

SUBCATEGORY_JUDGE_FUNCTION = {
    "content extraction": fuzzy_match,
    "layout detection": compare_coordinate,
    "style detection": exact_match,
}

API_LLM_MODELS = [
    "claude-3-5-sonnet-20241022",
    "gpt-4o-2024-11-20",
    "o1-2024-12-17",
    "gemini-2.0-flash-exp",
    "gemini-2.0-flash-thinking-exp",
    "qwen-vl-max-0809",
    "llama-3.2-90b-vision-instruct"
]