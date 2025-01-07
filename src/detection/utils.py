from .judge import fuzzy_match, compare_coordinates
SUBCATEGORY_JUDGE_FUNCTION_MAP = {
    'content extraction': fuzzy_match,
    'layout detection': compare_coordinates,
}