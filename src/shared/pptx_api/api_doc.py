from typing import Any, List


class API(object):
    def __init__(
        self,
        name: str,
        parameters: str,
        description: str,
        parameters_description: str,
        notes: str,
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


shape_api_list = [
    API(
        name="set_width",
        parameters="width: int",
        description="Set the width of the selected shape.",
        parameters_description="It takes one parameter 'width', which is in emu units as an integer.",
        notes="The shape must be selected before calling this function.",
    ),
]