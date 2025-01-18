import os
import tempfile
from typing import Generator

import pytest
from PIL import Image
from pptx import Presentation

from src.shared.pptx_api.api_executor_json import (
    choose_shape,
    choose_slide,
    set_height,
    set_left,
    set_top,
    set_width,
)
from src.shared.pptx_api.utils import get_shape_ids, get_slide_ids