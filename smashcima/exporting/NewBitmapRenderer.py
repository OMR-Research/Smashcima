from typing import Tuple

import numpy as np

from .Canvas import Canvas
from .ImageLayer import ImageLayer


class NewBitmapRenderer:
    def __init__(
        self,
        background_color = (0, 0, 0, 0)
    ) -> None:
        self.background_color: Tuple[int, int, int, int] = background_color
        """Color to use for the blank canvas, transparent by default
        (BGRA uint8 format)"""

    def render(self, final_layer: ImageLayer) -> np.ndarray:
        """Exports the final layer from a compositor into a bitmap image"""

        # merge the background color with the final layer from the compositor
        canvas = Canvas(
            width=final_layer.width,
            height=final_layer.height,
            background_color=self.background_color
        )
        canvas.place_layer(final_layer.bitmap)

        return canvas.read()
