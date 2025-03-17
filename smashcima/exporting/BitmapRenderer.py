from typing import Tuple

import numpy as np

from smashcima.exporting.compositing.DefaultCompositor import DefaultCompositor
from smashcima.exporting.postprocessing.NullPostprocessor import NullPostprocessor
from smashcima.scene.ViewBox import ViewBox

from .image.Canvas import Canvas
from .image.ImageLayer import ImageLayer


class BitmapRenderer:
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

    @staticmethod
    def default_viewbox_render(view_box: ViewBox, dpi: float) -> np.ndarray:
        """Combines the renderer with default compositor and null postprocessor
        to serve as a debugging simple visualizer tool. Scene in, image out."""
        layer = DefaultCompositor(NullPostprocessor()).run(view_box, dpi=dpi)
        return BitmapRenderer().render(layer)
