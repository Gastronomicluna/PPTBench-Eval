# pptbench/extractors/ppt_extractor.py

from pptx.presentation import Presentation
from pptx.slide import Slide

from pptbench.utils import unit_conversion

from .factories import shape_extractor_factory
from .notes_extractor import NotesExtractor


class SlideShapeExtractor:
    def __init__(self, slide: Slide, measurement_unit: str = "pt"):
        """Initializes the SlideShapeExtractor.

        Args:
            slide (Slide): The slide to extract shapes from.
            measurement_unit (str, optional): The unit of measurement. Defaults to "pt".
        """
        self._slide = slide
        self._measurement_unit = measurement_unit

    def extract_slide_metadata(self) -> dict:
        """Extracts metadata from the slide.

        Returns:
            dict: A dictionary containing slide metadata.
        """
        return {
            "slide_id": self._slide.slide_id,
            "slide_name": self._slide.name,
        }

    def extract_shapes(self) -> list:
        """Extracts shapes from the slide.

        Returns:
            list: A list of dictionaries, each containing shape data.
        """
        shapes = []
        for shape in self._slide.shapes:
            shapes.append(self._extract_shape(shape))
        return shapes

    def _extract_shape(self, shape) -> dict:
        """Extracts data from a shape.

        Args:
            shape: The shape to extract data from.

        Returns:
            dict: A dictionary containing shape data.
        """
        extractor = shape_extractor_factory(shape, self._measurement_unit)
        return extractor.extract_shape()

    def extract_notes(self) -> dict:
        """Extracts notes from the slide.

        Returns:
            dict: A dictionary containing notes data.
        """
        if self._slide.has_notes_slide:
            notes_slide = self._slide.notes_slide
            extractor = NotesExtractor(notes_slide, self._measurement_unit)
            return extractor.extract_notes()
        return {}

    def extract_slide(self) -> dict:
        """Extracts all data from the slide.

        Returns:
            dict: A dictionary containing slide data, including shapes and notes.
        """
        slide_data = self.extract_slide_metadata()
        slide_data["shapes"] = self.extract_shapes()
        notes_data = self.extract_notes()
        if notes_data:
            slide_data["notes"] = notes_data
        return slide_data


class PowerPointShapeExtractor:
    def __init__(self, ppt: Presentation, measurement_unit: str = "pt"):
        """Initializes the PowerPointShapeExtractor.

        Args:
            ppt (Presentation): The PowerPoint presentation to extract data from.
            measurement_unit (str, optional): The unit of measurement. Defaults to "pt".
        """
        self._ppt = ppt
        self._measurement_unit = measurement_unit

    def extract_slide_width(self) -> int | float:
        """Extracts the width of the slides.

        Returns:
            int | float: The width of the slides in the specified measurement unit.
        """
        return unit_conversion(self._ppt.slide_width, self._measurement_unit)

    def extract_slide_height(self) -> int | float:
        """Extracts the height of the slides.

        Returns:
            int | float: The height of the slides in the specified measurement unit.
        """
        return unit_conversion(self._ppt.slide_height, self._measurement_unit)

    def _extract_ppt_metadata(self) -> dict:
        """Extracts metadata from the PowerPoint presentation.

        Returns:
            dict: A dictionary containing presentation metadata.
        """
        return {
            "slide_width": self.extract_slide_width(),
            "slide_height": self.extract_slide_height(),
        }

    def extract_slides(self) -> list:
        """Extracts all slides from the presentation.

        Returns:
            list: A list of dictionaries, each containing slide data.
        """
        slides = []
        for slide in self._ppt.slides:
            slide_extractor = SlideShapeExtractor(
                slide, self._measurement_unit
            )
            slides.append(slide_extractor.extract_slide())
        return slides

    def extract_ppt(self) -> dict:
        """Extracts all data from the PowerPoint presentation.

        Returns:
            dict: A dictionary containing presentation data, including slides.
        """
        return {
            **self._extract_ppt_metadata(),
            "slides": self.extract_slides(),
        }
