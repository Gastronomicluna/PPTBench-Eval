from typing import Any, Dict, List

from ...shared.pptx_api.api_executor import api_executor
from ...shared.utils import fuzzy_match
from ..utils import (
    get_slide_from_presentation,
    has_out_of_bounds,
    has_overlap,
    produce_modified_presentation_json,
)


def judge_answer_add_shape(
    api_calls: List[str],
    shape_to_modify: Dict[str, Any],
    json_data: Dict[str, Any],  # JSON data, minus one shape
    presentation_json: Dict[str, Any],  # Original Presentation JSON data
) -> bool:
    """
    Judge the answer based on the API calls and ground truth.

    Args:
        api_calls (List[str]): The API calls made by the model.
        shape_to_modify (Dict[str, Any]): The shape to modify.
        json_data (Dict[str, Any]): The JSON data with n - 1 shapes.
        presentation_json (Dict[str, Any]): The original presentation JSON data.

    Returns:
        bool: Whether the answer is correct.
    """
    # Get slide height and width
    slide_height = presentation_json.get("slide_height")
    slide_width = presentation_json.get("slide_width")

    # Get slide ID
    slide_id = shape_to_modify.get("slide_id")

    # Get the minus one shape slide JSON data
    minus_one_shape_slide_json = json_data.get("slide", {})

    # Produce the modified presentation JSON data
    minus_one_shape_presentation_json = produce_modified_presentation_json(
        presentation=presentation_json,
        slide_id=slide_id,
        slide_json=minus_one_shape_slide_json,
    )

    # Execute the API calls
    modified_presentation_json = api_executor(
        lines=api_calls,
        json=minus_one_shape_presentation_json,
        mode="json",
    )
    print(modified_presentation_json)
    # Get the modified slide
    modified_slide = get_slide_from_presentation(
        slide_id=slide_id,
        presentation=modified_presentation_json,
    )
    # print(modified_slide)
    # Check if the slide has out of bounds or has overlap
    if has_out_of_bounds(
        slide_json=modified_slide,
        slide_height=slide_height,
        slide_width=slide_width,
    ):
        return False

    if has_overlap(slide_json=modified_slide):
        return False

    def get_new_shape(
        slide_with_n_shape: Dict[str, Any],
        slide_with_n_plus_one_shape: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Get the new shape from the modified slide JSON data.

        Args:
            slide_with_n_shape (Dict[str, Any]): The slide JSON data with n shapes.
            slide_with_n_plus_one_shape (Dict[str, Any]): The slide JSON data with n + 1 shapes.

        Returns:
            Dict[str, Any]: The new shape data.
        """
        # Get the shapes from the original slide
        original_shapes = slide_with_n_shape.get("shapes", [])

        # Get the shapes from the modified slide
        add_shape_slide_shapes = slide_with_n_plus_one_shape.get("shapes", [])
        # if len(add_shape_slide_shapes) <= len(original_shapes):
        #     raise ValueError("The number of shapes in the modified slide is not greater than the original slide.")
        # Find the new shape
        new_shape = None
        for shape in add_shape_slide_shapes:
            if shape not in original_shapes:
                new_shape = shape
                break

        return new_shape

    # Get the added shape
    added_shape = get_new_shape(
        slide_with_n_shape=minus_one_shape_slide_json,
        slide_with_n_plus_one_shape=modified_slide,
    )

    def compare_shape(
        gold_shape: Dict[str, Any],
        shape_to_test: Dict[str, Any],
        text_threshold: float = 0.95,
    ) -> bool:
        """
        Compare the original shape with the modified shape.

        Args:
            gold_shape (Dict[str, Any]): The original shape data.
            shape_to_test (Dict[str, Any]): The modified shape data.

        Returns:
            bool: Whether the shapes are the same.
        """
        # Compare text if it exists in either shape
        original_text = gold_shape.get("text")
        modified_text = shape_to_test.get("text")

        # If text exists in one shape but not the other, return False
        if bool(original_text) != bool(modified_text):
            return False

        # If both have text, compare them
        if (
            original_text
            and modified_text
            and fuzzy_match(
                ground_truth=original_text,
                answer=modified_text,
                threshold=text_threshold,
            )
        ):
            return False

        # Compare images
        original_image = gold_shape.get("image_path")
        modified_image = shape_to_test.get("image_path")

        # If image exists in one shape but not the other, return False
        if bool(original_image) != bool(modified_image):
            return False

        # If both have images, compare them
        if original_image and modified_image and original_image != modified_image:
            return False

    return compare_shape(
        gold_shape=shape_to_modify,
        shape_to_test=added_shape,
    )
