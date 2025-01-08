from .judge import compare_coordinate, exact_match, fuzzy_match

SUBCATEGORY_JUDGE_FUNCTION = {
    "content extraction": fuzzy_match,
    "layout detection": compare_coordinate,
    "style detection": exact_match,
}
