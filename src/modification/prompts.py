from typing import List

from ..shared.pptx_api.api_doc import API, api_list


def api_to_string(
    api_list: List[API],
) -> str:
    """
    Convert a list of API objects to a string representation.

    Args:
        api_list (list): List of API objects.

    Returns:
        str: String representation of the API list.
    """
    api_strings = []
    for api in api_list:
        # Format each API with essential information only
        api_str = (
            f"{api.name}({api.parameters}) " 
            + f"Description: {api.description} " 
            + f"Notes: {api.notes}" 
        )

        api_strings.append(api_str)

    # Join all API strings with clear separation
    return "\n".join(api_strings)

def main() -> None:
    api_str = api_to_string(api_list)
    print(api_str)
    
if __name__ == "__main__":
    main()