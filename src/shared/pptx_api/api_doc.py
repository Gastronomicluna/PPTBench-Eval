from typing import List, Any
class API(object):
    def __init__(
        self,
        name: str,
        parameters: List[Any],
        description: str,
        parameters_description: List[str],
        notes: str,
        example: str,
    ):
        self.name = name
        self.parameters = parameters
        self.description = description
        self.parameters_description = parameters_description
        self.notes = notes
        self.example = example
        
    def __str__(self):
        return f"{self.name}: {self.description}"