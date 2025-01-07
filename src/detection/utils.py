from .judge import fuzzy_match, compare_coordinates, exact_match
SUBCATEGORY_JUDGE_FUNCTION_MAP = {
    'content extraction': fuzzy_match,
    'layout detection': compare_coordinates,
    'style detection': exact_match,
}