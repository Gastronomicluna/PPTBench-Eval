from typing import Dict, Final

# Map of slide layout indices to their descriptive names
SLIDE_LAYOUTS: Final[Dict[int, str]] = {
    0: "Title Slide",
    1: "Title and Content",
    3: "Section Header",
    4: "Comparison",
    5: "Title Only",
    6: "Blank",
    7: "Content with Caption",
    8: "Picture with Caption",
    9: "Title and Vertical Text",
    10: "Vertical Title and Text",
}


class API(object):
    def __init__(
        self,
        name: str,
        parameters: str,
        description: str,
        parameters_description: str,
        notes: str = "",
        example: str = "",
    ):
        self.name = name
        self.parameters = parameters
        self.description = description
        self.parameters_description = parameters_description
        self.notes = notes
        self.example = example

    def __str__(self):
        return f"{self.name}: {self.description}"


API_LIST = [
    API(
        name="create_slide",
        parameters="layout: int = 6",
        description="Create a new slide with the specified layout, and choose the slide as the current slide.",
        parameters_description=(
            "It takes one parameter 'layout', which is an integer representing the slide layout type: "
            + ", ".join([f"{idx} ({name})" for idx, name in SLIDE_LAYOUTS.items()])
            + "."
        ),
        notes=f"This function creates a new slide in the presentation with the specified layout. Default is 6 ({SLIDE_LAYOUTS[6]}).",
        example="create_slide(0)  # Creates a title slide",
    ),
    API(
        name="choose_shape",
        parameters="shape_id: int",
        description="Choose a shape to work with.",
        parameters_description="It takes one parameter 'shape_id', which is the index of the shape to choose.",
        notes="The shape_id value can be found with the key 'shape_id' in the JSON data. The slide must be selected before calling this function.",
        example="choose_shape(0)",
    ),
    API(
        name="choose_slide",
        parameters="slide_id: int",
        description="Choose a slide to work with.",
        parameters_description="It takes one parameter 'slide_id', which is the index of the slide to choose.",
        notes="The slide_id value can be found with the key 'slide_id' in the JSON data.",
        example="choose_slide(0)",
    ),
    API(
        name="set_width",
        parameters="width: int",
        description="Set the width of the selected shape.",
        parameters_description="It takes one parameter 'width', which is in emu units as an integer.",
        notes="The shape must be selected before calling this function.",
        example="set_width(1000000)",
    ),
    API(
        name="set_height",
        parameters="height: int",
        description="Set the height of the selected shape.",
        parameters_description="It takes one parameter 'height', which is in emu units as an integer.",
        notes="The shape must be selected before calling this function.",
        example="set_height(1000000)",
    ),
    API(
        name="set_top",
        parameters="top: int",
        description="Set the top of the selected shape.",
        parameters_description="It takes one parameter 'top', which is in emu units as an integer.",
        notes="The shape must be selected before calling this function.",
        example="set_top(1000000)",
    ),
    API(
        name="set_left",
        parameters="left: int",
        description="Set the left of the selected shape.",
        parameters_description="It takes one parameter 'left', which is in emu units as an integer.",
        notes="The shape must be selected before calling this function.",
        example="set_left(1000000)",
    ),
    API(
        name="add_text_box",
        parameters="left: int, top: int, width: int, height: int, text: str",
        description="Add a text box to the current slide, and choose the shape as the current shape.",
        parameters_description="It takes five parameters: 'left', 'top', 'width', 'height', and 'text'. 'left', 'top', 'width', and 'height' are in emu units as integers. 'text' is a string.",
        notes="The current slide must be set before calling this function.",
        example="add_text_box(1000000, 1000000, 1000000, 1000000, 'Hello, World!')",
    ),
    API(
        name="add_picture",
        parameters="left: int, top: int, width: int, height: int, image_path: str",
        description="Add a picture to the current slide, and choose the shape as the current shape.",
        parameters_description="It takes five parameters: 'left', 'top', 'width', 'height', and 'image_path'. 'left', 'top', 'width', and 'height' are in emu units as integers. 'image_path' is the path to the image file to add.",
        notes="The current slide must be set before calling this function.",
        example="add_picture(1000000, 1000000, 1000000, 1000000, 'path/to/image.jpg')",
    ),
    API(
        name="insert_text",
        parameters="text: str",
        description="Insert text into the selected shape.",
        parameters_description="It takes one parameter 'text', which is a string.",
        notes="The shape must be selected before calling this function.",
        example="insert_text('Hello, World!')",
    ),
    API(
        name="set_font_size",
        parameters="font_size: int",
        description="Set the font size of the selected shape.",
        parameters_description="It takes one parameter 'font_size', which is an integer.",
        notes="The shape must be selected before calling this function.",
        example="set_font_size(24)",
    ),
    API(
        name="set_font_style",
        parameters="font_style: str",
        description="Set the font style of the selected shape.",
        parameters_description="It takes one parameter 'font_style', which is a string.",
        notes="The shape must be selected before calling this function.",
        example="set_font_style('bold')",
    ),
    API(
        name="set_font",
        parameters="font_name: str",
        description="Set the font of the selected shape.",
        parameters_description="It takes one parameter 'font_name', which is a string.",
        notes="The shape must be selected before calling this function.",
        example="set_font('Arial')",
    ),
    API(
        name="set_font_color",
        parameters="font_color: str",
        description="Set the font color of the selected shape.",
        parameters_description="It takes one parameter 'font_color', which is a string.",
        notes="The shape must be selected before calling this function.",
        example="set_font_color('FF0000')",
    ),
    API(
        name="set_notes_font",
        parameters="font_name: str",
        description="Set the font of the notes in the presentation.",
        parameters_description="It takes one parameter 'font_name', which is a string.",
        notes="The slide must be selected before calling this function, and it does not require a shape to be selected.",
        example="set_notes_font('Arial')",
    ),
]

add_shape_api_list = [
    API(
        name="add_text_box",
        parameters="left: int, top: int, width: int, height: int, text: str",
        description="Add a text box to the current slide, and choose the shape as the current shape.",
        parameters_description="It takes five parameters: 'left', 'top', 'width', 'height', and 'text'. 'left', 'top', 'width', and 'height' are in emu units as integers. 'text' is a string.",
        notes="The current slide must be set before calling this function.",
        example="add_text_box(1000000, 1000000, 1000000, 1000000, 'Hello, World!')",
    ),
    API(
        name="add_picture",
        parameters="left: int, top: int, width: int, height: int, image_path: str",
        description="Add a picture to the current slide, and choose the shape as the current shape.",
        parameters_description="It takes five parameters: 'left', 'top', 'width', 'height', and 'image_path'. 'left', 'top', 'width', and 'height' are in emu units as integers. 'image_path' is the path to the image file to add.",
        notes="The current slide must be set before calling this function.",
        example="add_picture(1000000, 1000000, 1000000, 1000000, 'path/to/image.jpg')",
    ),
]
